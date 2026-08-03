import uuid
from datetime import datetime, timezone
from typing import Optional, List
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.utils.exceptions import NotFoundException, ValidationException


class RegistryService:
    """Performs Active Model Registry status checks, updates, and activations."""

    def __init__(self, model_repo: TrainedModelRepository):
        self.model_repo = model_repo

    async def get_model(self, model_id: uuid.UUID, user_id: uuid.UUID) -> TrainedModel:
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise NotFoundException("Model not found.")
            
        if model.training_session.user_id != user_id:
            raise NotFoundException("Model not found or access denied.")
        return model

    async def list_models(self, project_id: uuid.UUID) -> List[TrainedModel]:
        return await self.model_repo.get_by_project_id(project_id)

    async def get_active_model(self, project_id: uuid.UUID) -> Optional[TrainedModel]:
        return await self.model_repo.get_active_model(project_id)

    async def activate_model(self, model_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID) -> TrainedModel:
        model = await self.get_model(model_id, user_id)
        
        if model.training_session.dataset.project_id != project_id:
            raise ValidationException("Target model does not belong to the active project.")
            
        if model.status != "READY":
            raise ValidationException(f"Cannot activate model: status is currently '{model.status}' and not READY.")
            
        await self.model_repo.deactivate_all_in_project(project_id)
        
        model.is_active = True
        model.activated_at = datetime.now(timezone.utc)
        model.activated_by = user_id
        
        await self.model_repo.session.flush()
        await self.model_repo.session.commit()
        return model

    async def archive_model(self, model_id: uuid.UUID, user_id: uuid.UUID) -> TrainedModel:
        model = await self.get_model(model_id, user_id)
        
        model.is_active = False
        model.status = "ARCHIVED"
        
        await self.model_repo.session.flush()
        await self.model_repo.session.commit()
        return model

    async def delete_model(self, model_id: uuid.UUID, user_id: uuid.UUID) -> None:
        model = await self.get_model(model_id, user_id)
        
        if model.is_active:
            raise ValidationException("Cannot delete active model. Please activate a different model first.")
            
        await self.model_repo.delete(model.id)
        await self.model_repo.session.flush()
        await self.model_repo.session.commit()
