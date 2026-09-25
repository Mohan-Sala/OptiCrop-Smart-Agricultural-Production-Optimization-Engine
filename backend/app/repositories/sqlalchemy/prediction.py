from app.repositories.mongodb.prediction import MongoPredictionRepository


class SqlAlchemyPredictionRepository(MongoPredictionRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPredictionRepository calls to MongoPredictionRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
