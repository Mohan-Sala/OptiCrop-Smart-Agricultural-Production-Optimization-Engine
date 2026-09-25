from app.repositories.mongodb.artifact import MongoPreprocessingArtifactRepository


class SqlAlchemyPreprocessingArtifactRepository(MongoPreprocessingArtifactRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPreprocessingArtifactRepository calls to MongoPreprocessingArtifactRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
