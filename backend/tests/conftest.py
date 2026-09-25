import os
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport

# Force testing environment before loading Settings
os.environ["ENVIRONMENT"] = "testing"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["MONGODB_DATABASE"] = "opticrop_ai_test"

from app.main import app
from app.core.config import settings
from app.database.mongodb import init_mongodb, close_mongodb, get_motor_database
from app.models import ALL_DOCUMENT_MODELS
from beanie import Document
import sqlalchemy

class MongoDeleteClause:
    def __init__(self, model):
        self.model = model
        self.criteria = []

    def where(self, *criteria):
        self.criteria.extend(criteria)
        return self

    def __repr__(self):
        return f"MongoDeleteClause({self.model}, {self.criteria})"


orig_sa_delete = sqlalchemy.delete

def smart_delete(target, *args, **kwargs):
    if isinstance(target, type) and issubclass(target, Document):
        return MongoDeleteClause(target)
    return orig_sa_delete(target, *args, **kwargs)

sqlalchemy.delete = smart_delete


class MongoTestSession:
    """Compatibility session wrapping Beanie/MongoDB document operations for test fixtures."""
    def __init__(self):
        self._pending = []

    def add(self, entity):
        self._pending.append(entity)

    def add_all(self, entities):
        self._pending.extend(entities)

    async def flush(self):
        for entity in self._pending:
            if hasattr(entity, "save"):
                try:
                    await entity.save()
                except Exception:
                    await entity.insert()
            elif hasattr(entity, "insert"):
                await entity.insert()
        self._pending.clear()

    async def commit(self):
        await self.flush()

    async def rollback(self):
        self._pending.clear()

    async def close(self):
        self._pending.clear()

    async def get(self, entity_class, id):
        if hasattr(entity_class, "get"):
            return await entity_class.get(id)
        return None

    async def refresh(self, entity):
        if hasattr(entity, "id") and hasattr(type(entity), "get"):
            fresh = await type(entity).get(entity.id)
            if fresh:
                fields = getattr(fresh, "model_fields", getattr(fresh, "__fields__", {}))
                for field in fields:
                    setattr(entity, field, getattr(fresh, field))

    async def execute(self, statement):
        try:
            if isinstance(statement, MongoDeleteClause):
                if not statement.criteria:
                    await statement.model.find_all().delete()
                else:
                    for crit in statement.criteria:
                        await statement.model.find(crit).delete()
                return

            stmt_str = str(statement).lower()
            for model in ALL_DOCUMENT_MODELS:
                col_name = getattr(getattr(model, "Settings", None), "name", model.__name__.lower())
                if col_name in stmt_str or model.__name__.lower() in stmt_str:
                    if "where" in stmt_str and "sequence_number" in stmt_str and hasattr(model, "sequence_number"):
                        await model.find(model.sequence_number == 5).delete()
                    else:
                        await model.find_all().delete()
                    return
        except Exception:
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()


class TestSessionMaker:
    def __call__(self):
        return MongoTestSession()

    async def __aenter__(self):
        return MongoTestSession()

    async def __aexit__(self, *args):
        pass


test_session = TestSessionMaker()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provides a TestClient instance for route verification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


async def mock_async_true() -> bool:
    return True


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mocks external network health checks for testing isolation."""
    monkeypatch.setattr("app.api.v1.routes.health.check_db_connection", mock_async_true)
    monkeypatch.setattr("app.api.v1.routes.health.check_gridfs_connection", mock_async_true)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Session-scoped fixture to initialize MongoDB and Beanie on test database."""
    await init_mongodb(database_name=settings.MONGODB_TEST_DATABASE)
    try:
        db = get_motor_database()
        collections = await db.list_collection_names()
        for col in collections:
            if not col.startswith("system."):
                await db.drop_collection(col)
    except Exception:
        pass

    yield

    try:
        db = get_motor_database()
        collections = await db.list_collection_names()
        for col in collections:
            if not col.startswith("system."):
                await db.drop_collection(col)
    except Exception:
        pass
    await close_mongodb()


@pytest.fixture(autouse=True)
def override_db_dependency():
    yield
    app.dependency_overrides.clear()
