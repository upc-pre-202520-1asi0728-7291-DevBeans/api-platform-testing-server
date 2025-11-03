from datetime import datetime, UTC
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from shared.domain.database import Base


class AuditableAbstractAggregateRoot(Base):
    """
    Abstract Aggregate Root for auditable entities
    It also provides timestamps for creation and last updates
    """
    __abstract__ = True

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, index=True, autoincrement=True)

    @declared_attr
    def created_at(self):
        return Column(DateTime, default=datetime.now(UTC), nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)

    def to_dict(self):
        """Convert the aggregate root to a dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }