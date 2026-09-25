from app.repositories.mongodb.comparison_analytics import MongoComparisonAnalyticsRepository


class SqlAlchemyComparisonAnalyticsRepository(MongoComparisonAnalyticsRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyComparisonAnalyticsRepository calls to MongoComparisonAnalyticsRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
