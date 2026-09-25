from app.repositories.mongodb.preprocessing import MongoPreprocessingRepository


class SqlAlchemyPreprocessingRepository(MongoPreprocessingRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPreprocessingRepository calls to MongoPreprocessingRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
