from typing import Any, List, Optional
from app.models.project import Project
from app.repositories.interfaces.project import ProjectRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoProjectRepository(MongoBaseRepository[Project], ProjectRepository):
    """Concrete MongoDB / Beanie implementation of ProjectRepository."""

    def __init__(self):
        super().__init__(Project)

    async def get_by_user_id(self, user_id: Any) -> List[Project]:
        parsed_user_id = to_uuid(user_id)
        return await Project.find(Project.user_id == parsed_user_id).to_list()

    async def get_by_id_and_user_id(self, project_id: Any, user_id: Any) -> Optional[Project]:
        parsed_project_id = to_uuid(project_id)
        parsed_user_id = to_uuid(user_id)
        return await Project.find_one(
            Project.id == parsed_project_id,
            Project.user_id == parsed_user_id,
        )
