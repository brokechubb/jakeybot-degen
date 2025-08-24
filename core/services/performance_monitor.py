"""
Performance Monitor for JakeyBot

This module provides comprehensive performance monitoring and metrics
collection to identify bottlenecks and optimize performance.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import psutil
import threading


@dataclass
class PerformanceMetric:
    """Represents a performance measurement."""

    name: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandPerformance:
    """Performance data for a specific command."""

    command_name: str
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call: Optional[float] = None
    error_count: int = 0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))

    def update(self, execution_time: float, had_error: bool = False):
        """Update performance statistics."""
        self.total_calls += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.total_calls
        self.last_call = time.time()
        self.recent_times.append(execution_time)

        if had_error:
            self.error_count += 1


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.

    Features:
    - Command execution timing
    - Memory and CPU usage tracking
    - Database query performance
    - API call performance
    - Automatic performance alerts
    - Performance trend analysis
    """

    def __init__(self):
        self.command_metrics: Dict[str, CommandPerformance] = {}
        self.api_metrics: Dict[str, CommandPerformance] = {}
        self.db_metrics: Dict[str, CommandPerformance] = {}

        # System metrics
        self.system_metrics: deque = deque(maxlen=1000)
        self.start_time = time.time()

        # Performance thresholds
        self.thresholds = {
            "command_slow": 5.0,  # 5 seconds
            "api_slow": 10.0,  # 10 seconds
            "db_slow": 2.0,  # 2 seconds
            "memory_high": 80.0,  # 80% memory usage
            "cpu_high": 90.0,  # 90% CPU usage
        }

        # Monitoring tasks
        self.monitoring_task = None
        self.alert_task = None
        # Don't start tasks in constructor - wait for explicit start

    def _start_monitoring_tasks(self):
        """Start background monitoring tasks."""

        async def system_monitoring_loop():
            while True:
                try:
                    await asyncio.sleep(30)  # Monitor every 30 seconds
                    await self._collect_system_metrics()
                except Exception as e:
                    logging.error(f"Error in system monitoring: {e}")

        async def alert_loop():
            while True:
                try:
                    await asyncio.sleep(60)  # Check alerts every minute
                    await self._check_performance_alerts()
                except Exception as e:
                    logging.error(f"Error in alert monitoring: {e}")

        try:
            # Check if we're in an event loop
            loop = asyncio.get_running_loop()
            self.monitoring_task = loop.create_task(system_monitoring_loop())
            self.alert_task = loop.create_task(alert_loop())
        except RuntimeError:
            # No event loop running, will start later
            self.monitoring_task = None
            self.alert_task = None
            logging.debug("No event loop running, monitoring tasks will start later")

    async def start_monitoring_tasks(self):
        """Start monitoring tasks if not already running."""
        if self.monitoring_task is None or self.alert_task is None:
            self._start_monitoring_tasks()

    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Network I/O
            network = psutil.net_io_counters()

            metric = PerformanceMetric(
                name="system",
                value=time.time(),
                timestamp=time.time(),
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "memory_total_gb": memory.total / (1024**3),
                    "disk_percent": disk_percent,
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                },
            )

            self.system_metrics.append(metric)

        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")

    async def _check_performance_alerts(self):
        """Check for performance issues and generate alerts."""
        current_time = time.time()

        # Check command performance
        for cmd_name, metrics in self.command_metrics.items():
            if metrics.avg_time > self.thresholds["command_slow"]:
                logging.warning(
                    f"Slow command detected: {cmd_name} "
                    f"(avg: {metrics.avg_time:.2f}s, threshold: {self.thresholds['command_slow']}s)"
                )

        # Check API performance
        for api_name, metrics in self.api_metrics.items():
            if metrics.avg_time > self.thresholds["api_slow"]:
                logging.warning(
                    f"Slow API detected: {api_name} "
                    f"(avg: {metrics.avg_time:.2f}s, threshold: {self.thresholds['api_slow']}s)"
                )

        # Check database performance
        for db_name, metrics in self.db_metrics.items():
            if metrics.avg_time > self.thresholds["db_slow"]:
                logging.warning(
                    f"Slow database operation detected: {db_name} "
                    f"(avg: {metrics.avg_time:.2f}s, threshold: {self.thresholds['db_slow']}s)"
                )

        # Check system metrics
        if self.system_metrics:
            latest = self.system_metrics[-1]
            if (
                latest.metadata.get("memory_percent", 0)
                > self.thresholds["memory_high"]
            ):
                logging.warning(
                    f"High memory usage: {latest.metadata['memory_percent']:.1f}% "
                    f"(threshold: {self.thresholds['memory_high']}%)"
                )

            if latest.metadata.get("cpu_percent", 0) > self.thresholds["cpu_high"]:
                logging.warning(
                    f"High CPU usage: {latest.metadata['cpu_percent']:.1f}% "
                    f"(threshold: {self.thresholds['cpu_high']}%)"
                )

    def time_command(self, command_name: str):
        """
        Decorator to time command execution.

        Args:
            command_name: Name of the command to monitor
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                had_error = False

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    had_error = True
                    raise
                finally:
                    execution_time = time.time() - start_time
                    if command_name not in self.command_metrics:
                        self.command_metrics[command_name] = CommandPerformance(
                            command_name
                        )
                    self.command_metrics[command_name].update(execution_time, had_error)

            return wrapper

        return decorator

    def time_api_call(self, api_name: str):
        """
        Decorator to time API calls.

        Args:
            api_name: Name of the API to monitor
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                had_error = False

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    had_error = True
                    raise
                finally:
                    execution_time = time.time() - start_time
                    if api_name not in self.api_metrics:
                        self.api_metrics[api_name] = CommandPerformance(api_name)
                    self.api_metrics[api_name].update(execution_time, had_error)

            return wrapper

        return decorator

    def time_db_operation(self, operation_name: str):
        """
        Decorator to time database operations.

        Args:
            operation_name: Name of the database operation to monitor
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                had_error = False

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    had_error = True
                    raise
                finally:
                    execution_time = time.time() - start_time
                    if operation_name not in self.db_metrics:
                        self.db_metrics[operation_name] = CommandPerformance(
                            operation_name
                        )
                    self.db_metrics[operation_name].update(execution_time, had_error)

            return wrapper

        return decorator

    def get_command_stats(self, command_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get command performance statistics.

        Args:
            command_name: Specific command name or None for all

        Returns:
            Dictionary with command statistics
        """
        if command_name:
            if command_name not in self.command_metrics:
                return {}

            metrics = self.command_metrics[command_name]
            return {
                "command_name": metrics.command_name,
                "total_calls": metrics.total_calls,
                "total_time": metrics.total_time,
                "min_time": metrics.min_time,
                "max_time": metrics.max_time,
                "avg_time": metrics.avg_time,
                "error_rate": metrics.error_count / metrics.total_calls
                if metrics.total_calls > 0
                else 0,
                "last_call": datetime.fromtimestamp(metrics.last_call)
                if metrics.last_call
                else None,
                "recent_avg": sum(metrics.recent_times) / len(metrics.recent_times)
                if metrics.recent_times
                else 0,
            }

        # Return all command stats
        return {
            name: self.get_command_stats(name) for name in self.command_metrics.keys()
        }

    def get_api_stats(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get API performance statistics.

        Args:
            api_name: Specific API name or None for all

        Returns:
            Dictionary with API statistics
        """
        if api_name:
            if api_name not in self.api_metrics:
                return {}

            metrics = self.api_metrics[api_name]
            return {
                "command_name": metrics.command_name,
                "total_calls": metrics.total_calls,
                "total_time": metrics.total_time,
                "min_time": metrics.min_time,
                "max_time": metrics.max_time,
                "avg_time": metrics.avg_time,
                "error_rate": metrics.error_count / metrics.total_calls
                if metrics.total_calls > 0
                else 0,
                "last_call": datetime.fromtimestamp(metrics.last_call)
                if metrics.last_call
                else None,
                "recent_avg": sum(metrics.recent_times) / len(metrics.recent_times)
                if metrics.recent_times
                else 0,
            }

        # Return all API stats
        return {name: self.get_api_stats(name) for name in self.api_metrics.keys()}

    def get_db_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get database operation performance statistics.

        Args:
            operation_name: Specific operation name or None for all

        Returns:
            Dictionary with database operation statistics
        """
        if operation_name:
            if operation_name not in self.db_metrics:
                return {}

            metrics = self.db_metrics[operation_name]
            return {
                "command_name": metrics.command_name,
                "total_calls": metrics.total_calls,
                "total_time": metrics.total_time,
                "min_time": metrics.min_time,
                "max_time": metrics.max_time,
                "avg_time": metrics.avg_time,
                "error_rate": metrics.error_count / metrics.total_calls
                if metrics.total_calls > 0
                else 0,
                "last_call": datetime.fromtimestamp(metrics.last_call)
                if metrics.last_call
                else None,
                "recent_avg": sum(metrics.recent_times) / len(metrics.recent_times)
                if metrics.recent_times
                else 0,
            }

        # Return all DB operation stats
        return {name: self.get_db_stats(name) for name in self.db_metrics.keys()}

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system performance statistics.

        Returns:
            Dictionary with system statistics
        """
        if not self.system_metrics:
            return {}

        latest = self.system_metrics[-1]
        uptime = time.time() - self.start_time

        # Calculate averages over the last hour
        recent_metrics = [
            m for m in self.system_metrics if time.time() - m.timestamp < 3600
        ]

        if recent_metrics:
            avg_cpu = sum(
                m.metadata.get("cpu_percent", 0) for m in recent_metrics
            ) / len(recent_metrics)
            avg_memory = sum(
                m.metadata.get("memory_percent", 0) for m in recent_metrics
            ) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = 0

        return {
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "current_cpu_percent": latest.metadata.get("cpu_percent", 0),
            "current_memory_percent": latest.metadata.get("memory_percent", 0),
            "current_memory_used_gb": latest.metadata.get("memory_used_gb", 0),
            "current_memory_total_gb": latest.metadata.get("memory_total_gb", 0),
            "avg_cpu_percent_1h": avg_cpu,
            "avg_memory_percent_1h": avg_memory,
            "total_metrics_collected": len(self.system_metrics),
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance summary.

        Returns:
            Dictionary with performance summary
        """
        # Top slowest commands
        slow_commands = sorted(
            self.command_metrics.values(), key=lambda x: x.avg_time, reverse=True
        )[:5]

        # Top slowest APIs
        slow_apis = sorted(
            self.api_metrics.values(), key=lambda x: x.avg_time, reverse=True
        )[:5]

        # Top slowest DB operations
        slow_db_ops = sorted(
            self.db_metrics.values(), key=lambda x: x.avg_time, reverse=True
        )[:5]

        return {
            "system": self.get_system_stats(),
            "slowest_commands": [
                {
                    "name": cmd.command_name,
                    "avg_time": cmd.avg_time,
                    "total_calls": cmd.total_calls,
                    "error_rate": cmd.error_count / cmd.total_calls
                    if cmd.total_calls > 0
                    else 0,
                }
                for cmd in slow_commands
            ],
            "slowest_apis": [
                {
                    "name": api.command_name,
                    "avg_time": api.avg_time,
                    "total_calls": api.total_calls,
                    "error_rate": api.error_count / api.total_calls
                    if api.total_calls > 0
                    else 0,
                }
                for api in slow_apis
            ],
            "slowest_db_operations": [
                {
                    "name": db.command_name,
                    "avg_time": db.avg_time,
                    "total_calls": db.total_calls,
                    "error_rate": db.error_count / db.total_calls
                    if db.total_calls > 0
                    else 0,
                }
                for db in slow_db_ops
            ],
            "total_commands_monitored": len(self.command_metrics),
            "total_apis_monitored": len(self.api_metrics),
            "total_db_operations_monitored": len(self.db_metrics),
        }

    async def cleanup(self):
        """Clean up resources when shutting down."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        if self.alert_task:
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                pass

        try:
            from core.services.colored_logging import log_success

            log_success("Performance monitor cleanup completed")
        except ImportError:
            logging.info("Performance monitor cleanup completed")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


async def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    await performance_monitor.start_monitoring_tasks()
    return performance_monitor


async def cleanup_performance_monitor():
    """Cleanup function for the performance monitor."""
    await performance_monitor.cleanup()


# Convenience decorators
def monitor_command(command_name: str):
    """Decorator to monitor command performance."""
    return performance_monitor.time_command(command_name)


def monitor_api_call(api_name: str):
    """Decorator to monitor API call performance."""
    return performance_monitor.time_api_call(api_name)


def monitor_db_operation(operation_name: str):
    """Decorator to monitor database operation performance."""
    return performance_monitor.time_db_operation(operation_name)


# Convenience functions
def get_command_stats(command_name: Optional[str] = None) -> Dict[str, Any]:
    """Get command performance statistics."""
    return performance_monitor.get_command_stats(command_name)


def get_system_stats() -> Dict[str, Any]:
    """Get system performance statistics."""
    return performance_monitor.get_system_stats()


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return performance_monitor.get_performance_summary()
