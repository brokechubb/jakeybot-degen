"""
Centralized Database Manager for JakeyBot

This module provides a singleton pattern for managing MongoDB connections
to prevent connection leaks and ensure proper resource management.
"""

import motor.motor_asyncio
import logging
from typing import Optional
from os import environ


class DatabaseManager:
    """
    Singleton database manager for MongoDB connections.

    Ensures only one client instance exists and provides proper cleanup.
    """

    _instance: Optional["DatabaseManager"] = None
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._client = None
            self._connection_string = environ.get("MONGO_DB_URL")

            # Don't raise error immediately - just log warning
            if not self._connection_string:
                logging.warning(
                    "MONGO_DB_URL environment variable not set - database features will be disabled"
                )

    async def get_client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """
        Get the MongoDB client instance, creating it if necessary.

        Returns:
            motor.motor_asyncio.AsyncIOMotorClient: The MongoDB client

        Raises:
            ValueError: If MONGO_DB_URL is not set or client creation fails
        """
        if not self._connection_string:
            raise ValueError(
                "MONGO_DB_URL environment variable is required for database operations"
            )

        if self._client is None:
            try:
                self._client = motor.motor_asyncio.AsyncIOMotorClient(
                    self._connection_string
                )
                logging.info("MongoDB client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize MongoDB client: {e}")
                raise

        return self._client

    async def get_database(
        self, db_name: Optional[str] = None
    ) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """
        Get a database instance.

        Args:
            db_name: Database name (defaults to MONGO_DB_NAME env var)

        Returns:
            motor.motor_asyncio.AsyncIOMotorDatabase: The database instance
        """
        client = await self.get_client()
        db_name = db_name or environ.get("MONGO_DB_NAME", "jakey_prod_db")
        return client[db_name]

    async def get_collection(
        self, collection_name: Optional[str] = None, db_name: Optional[str] = None
    ):
        """
        Get a collection instance.

        Args:
            collection_name: Collection name (defaults to MONGO_DB_COLLECTION_NAME env var)
            db_name: Database name (defaults to MONGO_DB_NAME env var)

        Returns:
            motor.motor_asyncio.AsyncIOMotorCollection: The collection instance
        """
        db = await self.get_database(db_name)
        collection_name = collection_name or environ.get(
            "MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection"
        )
        return db[collection_name]

    async def close(self):
        """Close the MongoDB client and cleanup resources."""
        if self._client is not None:
            try:
                await self._client.close()
                self._client = None
                logging.info("MongoDB client closed successfully")
            except Exception as e:
                logging.error(f"Error closing MongoDB client: {e}")
                self._client = None  # Ensure it's set to None even on error
        else:
            logging.info("MongoDB client was not initialized, skipping cleanup")

    async def health_check(self) -> bool:
        """
        Perform a health check on the database connection.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            client = await self.get_client()
            # Ping the database
            await client.admin.command("ping")
            return True
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return False

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if self._client:
            logging.warning(
                "DatabaseManager destroyed without proper cleanup. Call close() explicitly."
            )


# Global instance
database_manager = DatabaseManager()


async def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager: The singleton database manager
    """
    return database_manager


async def cleanup_database():
    """Cleanup function for the database manager."""
    await database_manager.close()
