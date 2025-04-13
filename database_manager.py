import time
import docker
from docker.errors import NotFound, APIError
from pymysql import MySQLError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from contextlib import contextmanager

from config import CONFIG
from database_models import Base

class DatabaseManager:
    def __init__(self, db_config=CONFIG["db"]):
        self.db_config = db_config
        self.engine = create_engine(
            self.db_config.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={'connect_timeout': self.db_config.DB_CONNECT_TIMEOUT}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = Base

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"DatabaseManager: Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def wait_for_mysql(self, timeout=30) -> bool:
        print(f"Waiting for MySQL connection at {self.db_config.DB_HOST}:{self.db_config.DB_PORT}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with self.engine.connect():
                    print("MySQL connection successful (via SQLAlchemy engine).")
                    return True
            except (OperationalError, MySQLError, ConnectionRefusedError, ConnectionResetError) as e:
                time.sleep(1)
            except SQLAlchemyError as e:
                 time.sleep(1)
        print(f"MySQL connection timed out after {timeout} seconds.")
        return False

    def check_mysql_container(self, docker_config=CONFIG["docker"]) -> bool:
        container_name = docker_config.MYSQL_CONTAINER_NAME
        print(f"Checking Docker container '{container_name}'...")
        try:
            client = docker.from_env()
            container = client.containers.get(container_name)

            if container.status != "running":
                print(f"Error: Container '{container_name}' exists but is not running ({container.status}).")
                return False

            print(f"Container '{container_name}' is running.")
            if not self.wait_for_mysql():
                print("Error: MySQL in container is running but not responding to connection attempts.")
                return False

            print("MySQL container check successful and database is responding.")
            return True

        except NotFound:
            print(f"Error: Docker container '{container_name}' not found.")
            return False
        except APIError as e:
            print(f"Error: Docker API error: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during Docker check: {e}")
            return False

    def setup_database_schema(self) -> bool:
        try:
            with self.engine.connect():
                print("Database connection verified.")
            self.Base.metadata.create_all(bind=self.engine)
            print("Database tables checked/created via SQLAlchemy.")
            return True
        except SQLAlchemyError as e:
            print(f"Error setting up database schema via SQLAlchemy: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during schema setup: {e}")
            return False