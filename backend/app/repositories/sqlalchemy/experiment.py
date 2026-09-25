from app.repositories.mongodb.experiment import MongoExperimentRepository


class SqlAlchemyExperimentRepository(MongoExperimentRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyExperimentRepository calls to MongoExperimentRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
