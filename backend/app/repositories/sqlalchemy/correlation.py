from app.repositories.mongodb.correlation import MongoCorrelationRepository


class SqlAlchemyCorrelationRepository(MongoCorrelationRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyCorrelationRepository calls to MongoCorrelationRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
