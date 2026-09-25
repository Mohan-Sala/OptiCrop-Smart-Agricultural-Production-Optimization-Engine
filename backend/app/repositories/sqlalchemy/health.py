from app.repositories.mongodb.health import MongoHealthRepository


class SqlAlchemyHealthRepository(MongoHealthRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyHealthRepository calls to MongoHealthRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
