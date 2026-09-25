from app.repositories.mongodb.drift import MongoDriftRepository


class SqlAlchemyDriftRepository(MongoDriftRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyDriftRepository calls to MongoDriftRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
