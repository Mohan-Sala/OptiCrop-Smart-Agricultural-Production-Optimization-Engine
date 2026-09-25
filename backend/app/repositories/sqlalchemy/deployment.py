from app.repositories.mongodb.deployment import MongoDeploymentRepository


class SqlAlchemyDeploymentRepository(MongoDeploymentRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyDeploymentRepository calls to MongoDeploymentRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
