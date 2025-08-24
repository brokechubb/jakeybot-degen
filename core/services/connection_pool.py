"""
Connection Pool Manager for JakeyBot

This module provides connection pooling for databases and HTTP clients
to improve performance and resource management.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp


class ConnectionPool:
    """
    Manages connection pools for various services.

    Features:
    - Database connection pooling
    - HTTP client connection pooling
    - Automatic connection health checks
    - Connection lifecycle management
    """

    def __init__(self):
        self.database_pools: Dict[str, Any] = {}
        self.http_pools: Dict[str, aiohttp.ClientSession] = {}
        self.health_check_task = None
        self._start_health_check_task()

    def _start_health_check_task(self):
        """Start the background health check task."""

        async def health_check_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    await self._perform_health_checks()
                except Exception as e:
                    logging.error(f"Error in connection health check: {e}")

        try:
            self.health_check_task = asyncio.create_task(health_check_loop())
        except RuntimeError:
            # No event loop running, will start later
            self.health_check_task = None

    async def start_health_check_task(self):
        """Start the background health check task if not already running."""
        if self.health_check_task is None:
            self._start_health_check_task()

    async def _perform_health_checks(self):
        """Perform health checks on all connections."""
        # Check database connections
        for pool_name, pool in self.database_pools.items():
            try:
                if hasattr(pool, "admin"):
                    await pool.admin.command("ping")
                    logging.debug(f"Database pool {pool_name} health check passed")
            except Exception as e:
                logging.warning(f"Database pool {pool_name} health check failed: {e}")

        # Check HTTP connections
        for pool_name, session in self.http_pools.items():
            try:
                if not session.closed:
                    # Try a simple request to check health
                    async with session.get(
                        "https://httpbin.org/get", timeout=5
                    ) as resp:
                        if resp.status == 200:
                            logging.debug(f"HTTP pool {pool_name} health check passed")
                        else:
                            logging.warning(
                                f"HTTP pool {pool_name} health check failed: status {resp.status}"
                            )
            except Exception as e:
                logging.warning(f"HTTP pool {pool_name} health check failed: {e}")

    async def get_database_pool(
        self, name: str, connection_string: str, max_pool_size: int = 100
    ) -> Any:
        """
        Get or create a database connection pool.

        Args:
            name: Name of the connection pool
            connection_string: Database connection string
            max_pool_size: Maximum number of connections in the pool

        Returns:
            Database connection pool
        """
        if name not in self.database_pools:
            try:
                # Create new MongoDB connection pool
                pool = AsyncIOMotorClient(
                    connection_string,
                    maxPoolSize=max_pool_size,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                )

                self.database_pools[name] = pool
                logging.info(f"Created database connection pool: {name}")

            except Exception as e:
                logging.error(f"Failed to create database pool {name}: {e}")
                raise

        return self.database_pools[name]

    async def get_http_pool(self, name: str, **kwargs) -> aiohttp.ClientSession:
        """
        Get or create an HTTP connection pool.

        Args:
            name: Name of the connection pool
            **kwargs: Additional arguments for ClientSession

        Returns:
            HTTP client session
        """
        if name not in self.http_pools or self.http_pools[name].closed:
            try:
                # Create new HTTP session with connection pooling
                session = aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(
                        limit=100,  # Total connection limit
                        limit_per_host=30,  # Per-host connection limit
                        ttl_dns_cache=300,  # DNS cache TTL
                        use_dns_cache=True,
                        keepalive_timeout=30,
                        enable_cleanup_closed=True,
                    ),
                    timeout=aiohttp.ClientTimeout(total=30),
                    **kwargs,
                )

                self.http_pools[name] = session
                logging.info(f"Created HTTP connection pool: {name}")

            except Exception as e:
                logging.error(f"Failed to create HTTP pool {name}: {e}")
                raise

        return self.http_pools[name]

    @asynccontextmanager
    async def get_database_connection(self, name: str, connection_string: str):
        """
        Context manager for database connections.

        Args:
            name: Name of the connection pool
            connection_string: Database connection string

        Yields:
            Database connection
        """
        pool = await self.get_database_pool(name, connection_string)
        try:
            yield pool
        except Exception as e:
            logging.error(f"Database connection error in pool {name}: {e}")
            raise

    @asynccontextmanager
    async def get_http_connection(self, name: str, **kwargs):
        """
        Context manager for HTTP connections.

        Args:
            name: Name of the connection pool
            **kwargs: Additional arguments for ClientSession

        Yields:
            HTTP client session
        """
        session = await self.get_http_pool(name, **kwargs)
        try:
            yield session
        except Exception as e:
            logging.error(f"HTTP connection error in pool {name}: {e}")
            raise

    async def close_pool(self, name: str, pool_type: str = "database"):
        """
        Close a specific connection pool.

        Args:
            name: Name of the pool to close
            pool_type: Type of pool ("database" or "http")
        """
        try:
            if pool_type == "database" and name in self.database_pools:
                pool = self.database_pools.pop(name)
                pool.close()
                logging.info(f"Closed database pool: {name}")

            elif pool_type == "http" and name in self.http_pools:
                session = self.http_pools.pop(name)
                if not session.closed:
                    await session.close()
                logging.info(f"Closed HTTP pool: {name}")

        except Exception as e:
            logging.error(f"Error closing {pool_type} pool {name}: {e}")

    async def close_all_pools(self):
        """Close all connection pools."""
        # Close database pools
        for name in list(self.database_pools.keys()):
            await self.close_pool(name, "database")

        # Close HTTP pools
        for name in list(self.http_pools.keys()):
            await self.close_pool(name, "http")

        logging.info("All connection pools closed")

    def get_pool_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all connection pools.

        Returns:
            Dictionary with pool statistics
        """
        stats = {
            "database_pools": len(self.database_pools),
            "http_pools": len(self.http_pools),
            "total_pools": len(self.database_pools) + len(self.http_pools),
        }

        # Add database pool details
        for name, pool in self.database_pools.items():
            stats[f"db_pool_{name}"] = {"type": "mongodb", "status": "active"}

        # Add HTTP pool details
        for name, session in self.http_pools.items():
            stats[f"http_pool_{name}"] = {
                "type": "aiohttp",
                "status": "closed" if session.closed else "active",
            }

        return stats

    async def cleanup(self):
        """Clean up all resources when shutting down."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        await self.close_all_pools()
        try:
            from core.services.colored_logging import log_success

            log_success("Connection pool manager cleanup completed")
        except ImportError:
            logging.info("Connection pool manager cleanup completed")


# Global connection pool manager instance
connection_pool = ConnectionPool()


async def get_connection_pool() -> ConnectionPool:
    """Get the global connection pool manager instance."""
    await connection_pool.start_health_check_task()
    return connection_pool


async def cleanup_connection_pool():
    """Cleanup function for the connection pool manager."""
    await connection_pool.cleanup()


# Convenience functions
async def get_database_pool(
    name: str, connection_string: str, max_pool_size: int = 100
) -> Any:
    """Get a database connection pool."""
    pool_manager = await get_connection_pool()
    return await pool_manager.get_database_pool(name, connection_string, max_pool_size)


async def get_http_pool(name: str, **kwargs) -> aiohttp.ClientSession:
    """Get an HTTP connection pool."""
    pool_manager = await get_connection_pool()
    return await pool_manager.get_http_pool(name, **kwargs)


@asynccontextmanager
async def database_connection(name: str, connection_string: str):
    """Context manager for database connections."""
    pool_manager = await get_connection_pool()
    async with pool_manager.get_database_connection(name, connection_string) as conn:
        yield conn


@asynccontextmanager
async def http_connection(name: str, **kwargs):
    """Context manager for HTTP connections."""
    pool_manager = await get_connection_pool()
    async with pool_manager.get_http_connection(name, **kwargs) as session:
        yield session
