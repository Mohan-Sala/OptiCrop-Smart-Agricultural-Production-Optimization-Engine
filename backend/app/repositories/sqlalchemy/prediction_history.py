from app.repositories.mongodb.prediction_history import MongoPredictionHistoryRepository


class SqlAlchemyPredictionHistoryRepository(MongoPredictionHistoryRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPredictionHistoryRepository calls to MongoPredictionHistoryRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
