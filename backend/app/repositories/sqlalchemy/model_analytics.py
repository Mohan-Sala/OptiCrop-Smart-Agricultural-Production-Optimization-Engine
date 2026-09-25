from app.repositories.mongodb.model_analytics import MongoModelAnalyticsRepository


class SqlAlchemyModelAnalyticsRepository(MongoModelAnalyticsRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyModelAnalyticsRepository calls to MongoModelAnalyticsRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
