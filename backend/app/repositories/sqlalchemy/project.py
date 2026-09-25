from app.repositories.mongodb.project import MongoProjectRepository


class SqlAlchemyProjectRepository(MongoProjectRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyProjectRepository calls to MongoProjectRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
