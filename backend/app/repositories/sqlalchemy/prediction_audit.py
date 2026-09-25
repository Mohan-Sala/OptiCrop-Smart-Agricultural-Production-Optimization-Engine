from app.repositories.mongodb.prediction_audit import MongoPredictionAuditRepository


class SqlAlchemyPredictionAuditRepository(MongoPredictionAuditRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyPredictionAuditRepository calls to MongoPredictionAuditRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
