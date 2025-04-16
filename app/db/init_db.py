import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate


logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize database with admin user"""
    # Check if admin user exists
    user = get_user_by_email(db, email=settings.ADMIN_EMAIL)
    if not user:
        logger.info("Creating admin user")
        user_in = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            name="Admin",
            role="admin",
        )
        create_user(db, user=user_in)
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")