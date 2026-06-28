from app.infra.db.base import TimestampedTable


class AccountModel(TimestampedTable):
    __tablename__ = "accounts"
