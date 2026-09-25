from app.repositories.mongodb.refresh_token import MongoRefreshTokenRepository


class SqlAlchemyRefreshTokenRepository(MongoRefreshTokenRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyRefreshTokenRepository calls to MongoRefreshTokenRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
