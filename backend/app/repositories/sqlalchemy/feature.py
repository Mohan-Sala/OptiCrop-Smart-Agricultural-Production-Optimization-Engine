from app.repositories.mongodb.feature import MongoFeatureMetadataRepository


class SqlAlchemyFeatureMetadataRepository(MongoFeatureMetadataRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyFeatureMetadataRepository calls to MongoFeatureMetadataRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
