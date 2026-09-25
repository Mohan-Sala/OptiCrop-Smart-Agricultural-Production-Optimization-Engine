import logging
from typing import Optional, List, Type
from pymongo import AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie, Document
from app.core.config import settings

try:
    import certifi
    CA_FILE = certifi.where()
except ImportError:
    CA_FILE = None

logger = logging.getLogger("app.database.mongodb")

async_client: Optional[AsyncMongoClient] = None
motor_client: Optional[AsyncIOMotorClient] = None
motor_database: Optional[AsyncIOMotorDatabase] = None


def get_async_client() -> AsyncMongoClient:
    """Retrieves the active PyMongo AsyncMongoClient instance used for Beanie."""
    global async_client
    if async_client is None:
        client_kwargs = {
            "uuidRepresentation": "standard",
            "serverSelectionTimeoutMS": 5000,
        }
        if CA_FILE:
            client_kwargs["tlsCAFile"] = CA_FILE
        async_client = AsyncMongoClient(
            settings.MONGODB_URI,
            **client_kwargs,
        )
    return async_client


def get_motor_client() -> AsyncIOMotorClient:
    """Retrieves the active AsyncIOMotorClient instance used for GridFS."""
    global motor_client
    if motor_client is None:
        client_kwargs = {
            "uuidRepresentation": "standard",
            "serverSelectionTimeoutMS": 5000,
        }
        if CA_FILE:
            client_kwargs["tlsCAFile"] = CA_FILE
        motor_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            **client_kwargs,
        )
    return motor_client


def get_motor_database(db_name: Optional[str] = None) -> AsyncIOMotorDatabase:
    """Retrieves the active AsyncIOMotorDatabase instance."""
    global motor_database
    m_client = get_motor_client()
    target_name = db_name or settings.MONGODB_DATABASE
    if motor_database is None or motor_database.name != target_name:
        motor_database = m_client[target_name]
    return motor_database


async def init_db(
    db_name: Optional[str] = None,
    document_models: Optional[List[Type[Document]]] = None,
    database_name: Optional[str] = None,
) -> None:
    """Initializes MongoDB connections and registers Beanie Document models."""
    target_name = db_name or database_name or settings.MONGODB_DATABASE
    masked_uri = settings.MONGODB_URI.split("@")[-1] if "@" in settings.MONGODB_URI else settings.MONGODB_URI
    logger.info("Connecting to MongoDB at: %s (database: %s)", masked_uri, target_name)
    
    client = get_async_client()
    db = client[target_name]

    # Verify connectivity via admin ping
    try:
        await client.admin.command("ping")
        logger.info("MongoDB connection ping succeeded.")
    except Exception as e:
        err_msg = str(e)
        if "TLSV1_ALERT_INTERNAL_ERROR" in err_msg or "SSL handshake failed" in err_msg:
            logger.error(
                "MongoDB Atlas SSL/TLS handshake failed! In MongoDB Atlas, this occurs when your current "
                "public IP address is not authorized in Network Access. "
                "Action: Log in to MongoDB Atlas -> Security -> Network Access -> Add IP Address."
            )
            raise ConnectionError(
                f"Failed to connect to MongoDB Atlas database '{target_name}': SSL handshake failed. "
                "Your current IP address is not whitelisted in MongoDB Atlas Network Access. "
                "Please add your IP in Atlas: Security -> Network Access -> Add IP Address."
            ) from e
        logger.error("MongoDB Atlas connection ping failed during startup: %s", err_msg)
        raise ConnectionError(f"Failed to connect to MongoDB Atlas database '{target_name}': {err_msg}") from e

    # Resolve document models if not provided explicitly
    if document_models is None:
        try:
            from app.models import ALL_DOCUMENT_MODELS
            document_models = ALL_DOCUMENT_MODELS
        except ImportError:
            document_models = []

    if document_models:
        await init_beanie(
            database=db,
            document_models=document_models,
        )
        logger.info("Beanie ODM successfully initialized with %d document models.", len(document_models))


async def close_db() -> None:
    """Gracefully closes MongoDB connections."""
    global async_client, motor_client, motor_database
    if async_client is not None:
        await async_client.close()
        async_client = None
    if motor_client is not None:
        motor_client.close()
        motor_client = None
        motor_database = None
    logger.info("MongoDB client connections closed.")


async def check_mongodb_connection() -> bool:
    """Pings MongoDB to verify liveness."""
    try:
        client = get_async_client()
        await client.admin.command("ping")
        return True
    except Exception as e:
        logger.error("MongoDB health check ping failed: %s", str(e))
        return False


# Aliases for init_mongodb and close_mongodb
init_mongodb = init_db
close_mongodb = close_db
