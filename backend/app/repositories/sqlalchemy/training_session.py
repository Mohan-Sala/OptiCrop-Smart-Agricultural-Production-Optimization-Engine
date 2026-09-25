from app.repositories.mongodb.training_session import MongoTrainingSessionRepository


class SqlAlchemyTrainingSessionRepository(MongoTrainingSessionRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyTrainingSessionRepository calls to MongoTrainingSessionRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
