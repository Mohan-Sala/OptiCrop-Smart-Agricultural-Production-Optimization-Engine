from app.repositories.mongodb.login_audit import MongoLoginAuditRepository


class SqlAlchemyLoginAuditRepository(MongoLoginAuditRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyLoginAuditRepository calls to MongoLoginAuditRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
