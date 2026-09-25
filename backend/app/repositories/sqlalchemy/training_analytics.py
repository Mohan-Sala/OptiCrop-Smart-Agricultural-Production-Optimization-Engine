from app.repositories.mongodb.training_analytics import MongoTrainingAnalyticsRepository


class SqlAlchemyTrainingAnalyticsRepository(MongoTrainingAnalyticsRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyTrainingAnalyticsRepository calls to MongoTrainingAnalyticsRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
