from app.repositories.mongodb.trained_model import MongoTrainedModelRepository


class SqlAlchemyTrainedModelRepository(MongoTrainedModelRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyTrainedModelRepository calls to MongoTrainedModelRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
