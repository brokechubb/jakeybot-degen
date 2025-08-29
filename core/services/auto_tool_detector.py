"""
Auto-Tool Detection Service for JakeyBot

This module provides intelligent and configurable detection of when tools are needed,
with adjustable sensitivity settings to prevent over-triggering.
"""

import logging
import yaml
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path


class AutoToolDetector:
    """
    Intelligent auto-tool detection with configurable sensitivity.

    Features:
    - Configurable confidence thresholds
    - Tool-specific detection rules
    - Context-aware detection
    - User preference learning
    - Cooldown periods
    - Repetition penalties
    """

    def __init__(self, config_path: str = "data/auto_tool_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.user_preferences: Dict[int, Dict] = {}
        self.last_activations: Dict[int, datetime] = {}
        self.activation_counts: Dict[int, Dict[str, int]] = {}

        logging.info("AutoToolDetector initialized with configurable sensitivity")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                logging.info(f"Loaded auto-tool config from {self.config_path}")
                return config
            else:
                logging.warning(
                    f"Auto-tool config not found at {self.config_path}, using defaults"
                )
                return self._get_default_config()
        except Exception as e:
            logging.error(f"Error loading auto-tool config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with conservative settings."""
        return {
            "global": {
                "enabled": True,
                "confidence_threshold": 0.8,  # Conservative default
                "min_message_length": 3,
                "max_message_length": 0,
                "require_explicit_keywords": True,  # Conservative default
                "fuzzy_matching": False,
            },
            "tools": {
                "ExaSearch": {
                    "enabled": True,
                    "confidence_threshold": 0.9,
                    "strong_keywords": [
                        "search for",
                        "find information about",
                        "look up",
                        "research",
                    ],
                    "weak_keywords": ["latest", "news", "current", "recent"],
                    "min_weak_keywords": 2,
                    "require_sports_context": True,
                },
                "CryptoPrice": {
                    "enabled": True,
                    "confidence_threshold": 0.95,
                    "require_both_keywords": True,
                },
                "CurrencyConverter": {
                    "enabled": True,
                    "confidence_threshold": 0.9,
                    "require_conversion_format": True,
                },
                "CodeExecution": {
                    "enabled": True,
                    "confidence_threshold": 0.98,
                    "require_explicit_calc": True,
                },
                "Memory": {
                    "enabled": True,
                    "confidence_threshold": 0.7,
                    "require_explicit_memory": True,
                },
            },
            "advanced": {
                "context_aware": True,
                "max_context_messages": 3,
                "repetition_penalty": 0.15,
                "cooldown_period": 60,
                "learn_user_preferences": True,
                "min_interactions_for_learning": 5,
            },
        }

    def detect_tool_needs(
        self, message: str, user_id: int = None, context_messages: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if a message requires tool usage with configurable sensitivity.

        Args:
            message: The user's message
            user_id: User ID for preference learning
            context_messages: Recent conversation context

        Returns:
            Tool info dict if tool is needed, None otherwise
        """
        if not self.config["global"]["enabled"]:
            return None

        # Basic message validation
        if not self._validate_message(message):
            return None

        # Check cooldown period
        if user_id and self._is_in_cooldown(user_id):
            return None

        # Calculate confidence scores for each tool
        tool_scores = {}

        for tool_name, tool_config in self.config["tools"].items():
            if not tool_config.get("enabled", True):
                continue

            confidence = self._calculate_tool_confidence(
                tool_name, message, user_id, context_messages
            )

            if confidence > 0:
                tool_scores[tool_name] = confidence

        # Find the tool with highest confidence above threshold
        if tool_scores:
            best_tool = max(tool_scores.items(), key=lambda x: x[1])
            tool_name, confidence = best_tool

            tool_config = self.config["tools"][tool_name]
            threshold = tool_config.get("confidence_threshold", 0.8)

            if confidence >= threshold:
                # Apply repetition penalty if applicable
                if user_id:
                    confidence = self._apply_repetition_penalty(
                        user_id, tool_name, confidence
                    )

                if confidence >= threshold:
                    # Update user preferences
                    if user_id:
                        self._update_user_preferences(user_id, tool_name, confidence)
                        self._record_activation(user_id, tool_name)

                    return self._create_tool_info(tool_name, message, confidence)

        return None

    def _validate_message(self, message: str) -> bool:
        """Validate if message meets basic criteria for tool detection."""
        if not message or not message.strip():
            return False

        words = message.split()
        min_length = self.config["global"]["min_message_length"]
        max_length = self.config["global"]["max_message_length"]

        if len(words) < min_length:
            return False

        if max_length > 0 and len(words) > max_length:
            return False

        return True

    def _is_in_cooldown(self, user_id: int) -> bool:
        """Check if user is in cooldown period."""
        if user_id not in self.last_activations:
            return False

        cooldown = self.config["advanced"]["cooldown_period"]
        time_since_last = datetime.now() - self.last_activations[user_id]

        return time_since_last.total_seconds() < cooldown

    def _calculate_tool_confidence(
        self,
        tool_name: str,
        message: str,
        user_id: int = None,
        context_messages: List[str] = None,
    ) -> float:
        """Calculate confidence score for a specific tool."""
        message_lower = message.lower()
        tool_config = self.config["tools"][tool_name]

        if tool_name == "ExaSearch":
            return self._calculate_exasearch_confidence(
                message_lower, tool_config, context_messages
            )
        elif tool_name == "CryptoPrice":
            return self._calculate_cryptoprice_confidence(message_lower, tool_config)
        elif tool_name == "CurrencyConverter":
            return self._calculate_currency_confidence(message_lower, tool_config)
        elif tool_name == "CodeExecution":
            return self._calculate_code_confidence(message_lower, tool_config)
        elif tool_name == "Memory":
            return self._calculate_memory_confidence(message_lower, tool_config)

        return 0.0

    def _calculate_exasearch_confidence(
        self, message: str, config: Dict, context_messages: List[str] = None
    ) -> float:
        """Calculate confidence for ExaSearch tool."""
        confidence = 0.0

        # Check strong keywords (high confidence)
        strong_keywords = config.get("strong_keywords", [])
        for keyword in strong_keywords:
            if keyword in message:
                confidence += 0.8
                break

        # Check weak keywords (lower confidence, requires multiple)
        weak_keywords = config.get("weak_keywords", [])
        weak_matches = sum(1 for keyword in weak_keywords if keyword in message)
        min_weak = config.get("min_weak_keywords", 2)

        if weak_matches >= min_weak:
            confidence += 0.3 * (weak_matches / min_weak)

        # Check sports keywords (require additional context)
        sports_keywords = config.get("sports_keywords", [])
        sports_matches = sum(1 for keyword in sports_keywords if keyword in message)

        if sports_matches > 0:
            if config.get("require_sports_context", True):
                # Require additional context for sports queries
                if context_messages and any(
                    "sports" in ctx.lower() or "game" in ctx.lower()
                    for ctx in context_messages
                ):
                    confidence += 0.4
            else:
                confidence += 0.4

        # Apply user preference adjustment
        return min(confidence, 1.0)

    def _calculate_cryptoprice_confidence(self, message: str, config: Dict) -> float:
        """Calculate confidence for CryptoPrice tool."""
        price_keywords = [
            "price",
            "worth",
            "value",
            "cost",
            "how much",
            "current",
            "live",
        ]
        crypto_tokens = [
            "bitcoin",
            "btc",
            "ethereum",
            "eth",
            "solana",
            "sol",
            "bonk",
            "dogecoin",
            "doge",
        ]

        has_price_keyword = any(keyword in message for keyword in price_keywords)
        has_crypto_token = any(token in message for token in crypto_tokens)

        if config.get("require_both_keywords", True):
            if has_price_keyword and has_crypto_token:
                return 0.9
            else:
                return 0.0
        else:
            if has_price_keyword or has_crypto_token:
                return 0.6
            return 0.0

    def _calculate_currency_confidence(self, message: str, config: Dict) -> float:
        """Calculate confidence for CurrencyConverter tool."""
        conversion_keywords = [
            "convert",
            "exchange rate",
            "usd to",
            "eur to",
            "jpy to",
            "currency",
        ]

        has_conversion_keyword = any(
            keyword in message for keyword in conversion_keywords
        )

        if config.get("require_conversion_format", True):
            # Look for currency conversion pattern
            pattern = (
                r"\d+\s*(usd|eur|jpy|gbp|cad|aud)\s*to\s*(usd|eur|jpy|gbp|cad|aud)"
            )
            if re.search(pattern, message, re.IGNORECASE):
                return 0.9
            return 0.0
        else:
            return 0.7 if has_conversion_keyword else 0.0

    def _calculate_code_confidence(self, message: str, config: Dict) -> float:
        """Calculate confidence for CodeExecution tool."""
        calc_keywords = [
            "calculate",
            "math",
            "percentage",
            "formula",
            "equation",
            "solve",
            "compute",
        ]

        has_calc_keyword = any(keyword in message for keyword in calc_keywords)

        if config.get("require_explicit_calc", True):
            # Require explicit calculation request
            if has_calc_keyword and any(
                word in message
                for word in ["what is", "how much is", "compute", "solve"]
            ):
                return 0.9
            return 0.0
        else:
            return 0.6 if has_calc_keyword else 0.0

    def _calculate_memory_confidence(self, message: str, config: Dict) -> float:
        """Calculate confidence for Memory tool."""
        memory_keywords = [
            "remember this",
            "remember that",
            "save this",
            "store this",
            "keep this in mind",
        ]

        has_memory_keyword = any(keyword in message for keyword in memory_keywords)

        if config.get("require_explicit_memory", True):
            return 0.8 if has_memory_keyword else 0.0
        else:
            # More sensitive for memory - detect personal information
            personal_indicators = [
                "my name is",
                "i like",
                "i prefer",
                "my favorite",
                "i am",
                "i'm",
            ]
            has_personal = any(
                indicator in message for indicator in personal_indicators
            )
            return 0.6 if has_personal else 0.0

    def _apply_repetition_penalty(
        self, user_id: int, tool_name: str, confidence: float
    ) -> float:
        """Apply penalty for repeated tool usage."""
        if user_id not in self.activation_counts:
            return confidence

        tool_counts = self.activation_counts[user_id]
        count = tool_counts.get(tool_name, 0)

        if count > 0:
            penalty = self.config["advanced"]["repetition_penalty"]
            penalty_amount = min(penalty * count, 0.3)  # Max 30% penalty
            return max(confidence - penalty_amount, 0.0)

        return confidence

    def _update_user_preferences(self, user_id: int, tool_name: str, confidence: float):
        """Update user preferences based on tool usage."""
        if not self.config["advanced"]["learn_user_preferences"]:
            return

        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        if tool_name not in self.user_preferences[user_id]:
            self.user_preferences[user_id][tool_name] = {
                "count": 0,
                "avg_confidence": 0.0,
            }

        pref = self.user_preferences[user_id][tool_name]
        pref["count"] += 1
        pref["avg_confidence"] = (
            pref["avg_confidence"] * (pref["count"] - 1) + confidence
        ) / pref["count"]

    def _record_activation(self, user_id: int, tool_name: str):
        """Record tool activation for cooldown and repetition tracking."""
        self.last_activations[user_id] = datetime.now()

        if user_id not in self.activation_counts:
            self.activation_counts[user_id] = {}

        if tool_name not in self.activation_counts[user_id]:
            self.activation_counts[user_id][tool_name] = 0

        self.activation_counts[user_id][tool_name] += 1

    def _create_tool_info(
        self, tool_name: str, message: str, confidence: float
    ) -> Dict[str, Any]:
        """Create tool info dictionary for detected tool."""
        base_info = {
            "tool": tool_name,
            "confidence": confidence,
            "auto_enable": True,
            "description": f"Auto-detected {tool_name} need (confidence: {confidence:.2f})",
        }

        # Add tool-specific parameters
        if tool_name == "ExaSearch":
            base_info.update(
                {
                    "function": "_tool_function_web_search",
                    "args": [message],
                    "enhanced_params": {
                        "searchType": "auto",
                        "numResults": 5,
                        "showHighlights": True,
                        "showSummary": True,
                    },
                }
            )
        elif tool_name == "CryptoPrice":
            # Extract token from message
            token = self._extract_crypto_token(message)
            base_info.update(
                {"function": "_tool_function_get_token_price", "args": [token or "BTC"]}
            )
        elif tool_name == "CurrencyConverter":
            # Extract currency conversion info
            conversion_info = self._extract_currency_conversion(message)
            base_info.update(
                {"function": "_tool_function_convert_currency", "args": conversion_info}
            )
        elif tool_name == "CodeExecution":
            base_info.update(
                {"function": "_tool_function_execute_code", "args": [message]}
            )
        elif tool_name == "Memory":
            base_info.update(
                {
                    "function": "_tool_function_remember_fact",
                    "args": [message, "auto_detected"],
                }
            )

        return base_info

    def _extract_crypto_token(self, message: str) -> str:
        """Extract cryptocurrency token from message."""
        crypto_mapping = {
            "bitcoin": "1",
            "btc": "1",
            "ethereum": "1027",
            "eth": "1027",
            "solana": "5426",
            "sol": "5426",
            "dogecoin": "74",
            "doge": "74",
        }

        message_lower = message.lower()
        for token, coin_id in crypto_mapping.items():
            if token in message_lower:
                return coin_id

        return "BTC"  # Default

    def _extract_currency_conversion(self, message: str) -> List[str]:
        """Extract currency conversion parameters from message."""
        pattern = r"(\d+)\s*(usd|eur|jpy|gbp|cad|aud)\s*to\s*(usd|eur|jpy|gbp|cad|aud)"
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            return [match.group(1), match.group(2).upper(), match.group(3).upper()]

        return ["100", "USD", "EUR"]  # Default

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user's tool usage preferences."""
        return self.user_preferences.get(user_id, {})

    def reset_user_preferences(self, user_id: int):
        """Reset user preferences and activation history."""
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
        if user_id in self.last_activations:
            del self.last_activations[user_id]
        if user_id in self.activation_counts:
            del self.activation_counts[user_id]

    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration dynamically."""
        self.config.update(new_config)
        logging.info("Auto-tool detection configuration updated")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
