import asyncio
import uuid
from pydantic import Field
from beanie import Document, init_beanie
from pymongo import AsyncMongoClient

class UserTest(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str

    class Settings:
        name = "test_users"

async def test():
    client = AsyncMongoClient("mongodb://localhost:27017", uuidRepresentation="standard", serverSelectionTimeoutMS=1000)
    db = client["test_opticrop"]
    await init_beanie(database=db, document_models=[UserTest])
    u = UserTest(email="farmer@opticrop.ai")
    print("SUCCESS: Instantiated UserTest with id:", u.id, "type:", type(u.id))
    print("Dict dump:", u.model_dump())
    await client.close()

if __name__ == "__main__":
    asyncio.run(test())
