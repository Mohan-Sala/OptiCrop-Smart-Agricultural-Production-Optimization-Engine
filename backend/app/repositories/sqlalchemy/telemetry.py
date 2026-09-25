from app.repositories.mongodb.telemetry import MongoTelemetryRepository


class SqlAlchemyTelemetryRepository(MongoTelemetryRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyTelemetryRepository calls to MongoTelemetryRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
