from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from shared.domain.aggregate_root import AuditableAbstractAggregateRoot
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserType(str, enum.Enum):
    PRODUCER = "PRODUCER"
    COOPERATIVE = "COOPERATIVE"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class User(AuditableAbstractAggregateRoot):
    """
    Agregado User - Gestiona autenticación y perfiles de usuario
    """
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    # Relaciones
    producer_profile = relationship("ProducerProfile", back_populates="user", uselist=False,
                                    cascade="all, delete-orphan")
    cooperative_profile = relationship("CooperativeProfile", back_populates="user", uselist=False,
                                       cascade="all, delete-orphan")

    def __init__(self, email: str, password: str, user_type: UserType):
        self.email = email
        self.password = self.hash_password(password)
        self.user_type = user_type
        self.status = UserStatus.ACTIVE

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """Verifies the password against the hashed version"""
        return pwd_context.verify(plain_password, self.password)

    def change_password(self, new_password: str) -> None:
        """Changes the user's password for a new hashed password"""
        self.password = self.hash_password(new_password)

    def activate(self) -> None:
        """Activates the user account"""
        self.status = UserStatus.ACTIVE

    def suspend(self) -> None:
        """Suspends the user account"""
        self.status = UserStatus.SUSPENDED

    def deactivate(self) -> None:
        """Deactivates the user account"""
        self.status = UserStatus.INACTIVE