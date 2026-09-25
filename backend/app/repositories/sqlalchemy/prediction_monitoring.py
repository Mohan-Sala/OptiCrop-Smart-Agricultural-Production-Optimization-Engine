from app.repositories.mongodb.prediction_monitoring import MongoPredictionMonitoringRepository


class SqlAlchemyPredictionMonitoringRepository(MongoPredictionMonitoringRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPredictionMonitoringRepository calls to MongoPredictionMonitoringRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
