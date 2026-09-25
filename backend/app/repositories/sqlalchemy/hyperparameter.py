from app.repositories.mongodb.hyperparameter import MongoHyperparameterSetRepository


class SqlAlchemyHyperparameterSetRepository(MongoHyperparameterSetRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyHyperparameterSetRepository calls to MongoHyperparameterSetRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
