"""
Colored Logging for JakeyBot

This module provides colored logging formatters to make logs more readable
and visually appealing in the terminal.
"""

import logging
import sys
from typing import Dict, Optional


class Colors:
    """ANSI color codes for terminal output."""

    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"


class ColoredFormatter(logging.Formatter):
    """
    Colored logging formatter that adds colors based on log level.

    Features:
    - Different colors for each log level
    - Colored timestamps and module names
    - Automatic color detection (disables colors if not in terminal)
    - Customizable color schemes
    """

    # Enhanced color scheme with more vibrant colors
    DEFAULT_COLORS = {
        "DEBUG": Colors.BRIGHT_BLACK + Colors.DIM,
        "INFO": Colors.BRIGHT_CYAN + Colors.BOLD,
        "WARNING": Colors.BRIGHT_YELLOW + Colors.BOLD,
        "ERROR": Colors.BRIGHT_RED + Colors.BOLD,
        "CRITICAL": Colors.BRIGHT_WHITE + Colors.BG_RED + Colors.BOLD,
        "SUCCESS": Colors.BRIGHT_GREEN + Colors.BOLD,
        "TIMESTAMP": Colors.BRIGHT_BLACK + Colors.DIM,
        "MODULE": Colors.BRIGHT_MAGENTA + Colors.BOLD,
        "FUNCTION": Colors.BRIGHT_BLUE + Colors.BOLD,
        "LINE_NUMBER": Colors.BRIGHT_BLACK,
        "MESSAGE": Colors.WHITE,
        "RESET": Colors.RESET,
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        use_colors: Optional[bool] = None,
    ):
        """
        Initialize the colored formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
            colors: Custom color scheme dictionary
            use_colors: Force enable/disable colors (auto-detect if None)
        """
        super().__init__(fmt, datefmt)

        # Use custom colors or default
        self.colors = colors or self.DEFAULT_COLORS.copy()

        # Auto-detect color support if not specified
        if use_colors is None:
            self.use_colors = self._supports_color()
        else:
            self.use_colors = use_colors

        # If colors are disabled, set all colors to empty strings
        if not self.use_colors:
            self.colors = {key: "" for key in self.colors.keys()}

    def _supports_color(self) -> bool:
        """
        Check if the terminal supports colors.

        Returns:
            True if colors are supported, False otherwise
        """
        # Check if we're in a terminal
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check for common color-supporting terminals
        import os

        term = os.environ.get("TERM", "").lower()
        colorterm = os.environ.get("COLORTERM", "").lower()

        # Common terminals that support colors
        color_terms = [
            "xterm",
            "xterm-color",
            "xterm-256color",
            "screen",
            "screen-256color",
            "tmux",
            "tmux-256color",
            "linux",
            "cygwin",
        ]

        return (
            term in color_terms
            or "color" in term
            or colorterm in ["truecolor", "24bit"]
            or os.environ.get("FORCE_COLOR", "").lower() in ["1", "true", "yes"]
        )

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with enhanced colors and visual elements.

        Args:
            record: The log record to format

        Returns:
            Formatted and colored log string
        """
        # Create a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)

        # Get colors
        level_color = self.colors.get(record.levelname, self.colors["MESSAGE"])
        timestamp_color = self.colors["TIMESTAMP"]
        module_color = self.colors["MODULE"]
        function_color = self.colors["FUNCTION"]
        line_color = self.colors["LINE_NUMBER"]
        message_color = self.colors["MESSAGE"]
        reset = self.colors["RESET"]

        # Format the basic message
        formatted = super().format(record_copy)

        if not self.use_colors:
            return formatted

        # Apply enhanced colors to different parts of the log message

        # Color the level name with visual separator
        if record.levelname in formatted:
            # Only replace if it's not already been processed
            if not formatted.startswith(f"{level_color}▶"):
                level_with_separator = f"{level_color}▶ {record.levelname}{reset}"
                formatted = formatted.replace(record.levelname, level_with_separator)

        # Color the timestamp with visual separator
        if hasattr(record, "asctime"):
            timestamp_with_separator = f"{timestamp_color}🕐 {record.asctime}{reset}"
            formatted = formatted.replace(record.asctime, timestamp_with_separator)

        # Color the module and function with visual separators
        if hasattr(record, "module"):
            module_func_pattern = f"{record.module}.{record.funcName}()"
            module_func_colored = f"{module_color}📦 {record.module}{reset}.{function_color}⚙️ {record.funcName}(){reset}"
            formatted = formatted.replace(module_func_pattern, module_func_colored)

        # Color the line number
        if hasattr(record, "lineno"):
            line_pattern = f":{record.lineno}"
            line_colored = f"{line_color}:{record.lineno}{reset}"
            formatted = formatted.replace(line_pattern, line_colored)

        # Add message color to the actual message part with visual separator
        if "]: " in formatted:
            parts = formatted.split("]: ", 1)
            if len(parts) == 2:
                formatted = f"{parts[0]}]: {message_color}💬 {parts[1]}{reset}"

        return formatted


class SimpleColoredFormatter(logging.Formatter):
    """
    Simplified colored formatter with just level-based coloring.

    This is a lighter-weight alternative that just colors the entire
    log message based on the log level.
    """

    LEVEL_COLORS = {
        "DEBUG": Colors.BRIGHT_BLACK + Colors.DIM,
        "INFO": Colors.BRIGHT_CYAN + Colors.BOLD,
        "WARNING": Colors.BRIGHT_YELLOW + Colors.BOLD,
        "ERROR": Colors.BRIGHT_RED + Colors.BOLD,
        "CRITICAL": Colors.BRIGHT_WHITE + Colors.BG_RED + Colors.BOLD,
        "SUCCESS": Colors.BRIGHT_GREEN + Colors.BOLD,
    }

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
        self.use_colors = self._supports_color()

    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        import os

        return (
            os.environ.get("TERM", "").lower().find("color") != -1
            or os.environ.get("COLORTERM", "") != ""
            or os.environ.get("FORCE_COLOR", "").lower() in ["1", "true", "yes"]
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format with simple level-based coloring."""
        formatted = super().format(record)

        if not self.use_colors:
            return formatted

        color = self.LEVEL_COLORS.get(record.levelname, "")
        if color:
            return f"{color}{formatted}{Colors.RESET}"

        return formatted


def setup_colored_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    use_simple: bool = False,
    colors: Optional[Dict[str, str]] = None,
) -> None:
    """
    Set up colored logging for the application.

    Args:
        level: Logging level
        format_string: Custom format string
        use_simple: Use simple formatter instead of advanced
        colors: Custom color scheme
    """
    # Default format - shorter and more readable
    if format_string is None:
        format_string = "%(levelname)s %(asctime)s [%(module)s.%(funcName)s:%(lineno)d]:\n    %(message)s"

    # Choose formatter
    if use_simple:
        formatter = SimpleColoredFormatter(
            fmt=format_string, datefmt="%m/%d/%Y %I:%M:%S %p"
        )
    else:
        formatter = ColoredFormatter(
            fmt=format_string, datefmt="%m/%d/%Y %I:%M:%S %p", colors=colors
        )

    # Set up handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_colored_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a colored logger instance.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger with colored output
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = SimpleColoredFormatter(
            fmt="%(levelname)s %(asctime)s [%(name)s]: %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger


# Enhanced convenience functions with vibrant colors and visual elements
def log_success(message: str, logger: Optional[logging.Logger] = None):
    """Log a success message with vibrant green styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}🎉 {message}{Colors.RESET}"
    else:
        message = f"🎉 {message}"

    logger.info(message)


def log_warning(message: str, logger: Optional[logging.Logger] = None):
    """Log a warning message with vibrant yellow styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}⚠️  {message}{Colors.RESET}"
    else:
        message = f"⚠️  {message}"

    logger.warning(message)


def log_error(message: str, logger: Optional[logging.Logger] = None):
    """Log an error message with vibrant red styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_RED}{Colors.BOLD}💥 {message}{Colors.RESET}"
    else:
        message = f"💥 {message}"

    logger.error(message)


def log_critical(message: str, logger: Optional[logging.Logger] = None):
    """Log a critical message with high-visibility styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_WHITE}{Colors.BG_RED}{Colors.BOLD}🚨 {message}{Colors.RESET}"
    else:
        message = f"🚨 {message}"

    logger.critical(message)


def log_info(message: str, logger: Optional[logging.Logger] = None):
    """Log an info message with vibrant cyan styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}ℹ️  {message}{Colors.RESET}"
    else:
        message = f"ℹ️  {message}"

    logger.info(message)


def log_debug(message: str, logger: Optional[logging.Logger] = None):
    """Log a debug message with subtle gray styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_BLACK}{Colors.DIM}🔍 {message}{Colors.RESET}"
    else:
        message = f"🔍 {message}"

    logger.debug(message)


def log_startup(message: str, logger: Optional[logging.Logger] = None):
    """Log a startup message with special styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}🚀 {message}{Colors.RESET}"
    else:
        message = f"🚀 {message}"

    logger.info(message)


def log_shutdown(message: str, logger: Optional[logging.Logger] = None):
    """Log a shutdown message with special styling."""
    if logger is None:
        logger = logging.getLogger()

    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        message = f"{Colors.BRIGHT_BLUE}{Colors.BOLD}🛑 {message}{Colors.RESET}"
    else:
        message = f"🛑 {message}"

    logger.info(message)
