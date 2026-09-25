from app.repositories.mongodb.project_analytics import MongoProjectAnalyticsRepository


class SqlAlchemyProjectAnalyticsRepository(MongoProjectAnalyticsRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyProjectAnalyticsRepository calls to MongoProjectAnalyticsRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
