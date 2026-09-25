from app.repositories.mongodb.evaluation import MongoEvaluationReportRepository


class SqlAlchemyEvaluationReportRepository(MongoEvaluationReportRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyEvaluationReportRepository calls to MongoEvaluationReportRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
