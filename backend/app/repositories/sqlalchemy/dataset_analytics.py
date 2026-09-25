from app.repositories.mongodb.dataset_analytics import MongoDatasetAnalyticsRepository


class SqlAlchemyDatasetAnalyticsRepository(MongoDatasetAnalyticsRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyDatasetAnalyticsRepository calls to MongoDatasetAnalyticsRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
