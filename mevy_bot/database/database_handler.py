import os
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from mevy_bot.models.user import User

logger = logging.getLogger(__name__)


class DatabaseHandler:

    def __init__(self):
        self.database_url = self.build_database_url()
        self.engine = create_engine(self.database_url)
        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    @staticmethod
    def build_database_url() -> str:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    def get_session(self) -> Session:
        """Creates a new database session."""
        return self.session_local()

    def create_all_tables(self):
        """Optional: Creates all tables"""
        User.metadata.create_all(bind=self.engine)

    def drop_all_tables(self, base):
        """Optional: Drops all tables."""
        base.metadata.drop_all(bind=self.engine)

    def healthcheck(self) -> bool:
        """Simple database health check."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except OperationalError:
            logger.error("Database health check failed")
            return False

    def ensure_database_exists(self):
        """Creates the database if it doesn't exist."""
        db_name = os.getenv("DB_NAME")
        temp_url = self.database_url.replace(f"/{db_name}", "/postgres")

        # Create a temporary engine connected to the default 'postgres' database
        temp_engine = create_engine(temp_url)

        # Check if database exists
        if self.healthcheck():
            logger.info("Database %s already exists.", db_name)
        else:
            logger.info("Database %s does not exist. Creating...", db_name)
            self.create_database_instance(temp_engine, db_name)

    def create_database_instance(self, engine, db_name: str):
        """Creates the database instance if it does not exist."""
        try:
            # Use the engine to connect with autocommit to avoid transaction block for CREATE DATABASE
            with engine.connect() as connection:
                # Turn on autocommit mode
                connection.execution_options(isolation_level="AUTOCOMMIT")
                connection.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info("Database %s created successfully.", db_name)
        except SQLAlchemyError as e:
            logger.error("Error creating database.", exc_info=e)
