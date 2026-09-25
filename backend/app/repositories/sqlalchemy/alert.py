from app.repositories.mongodb.alert import MongoAlertRepository


class SqlAlchemyAlertRepository(MongoAlertRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyAlertRepository calls to MongoAlertRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
