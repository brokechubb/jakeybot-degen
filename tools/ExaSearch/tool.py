# Built in Tools
from .manifest import ToolManifest
from os import environ
import aiohttp
import discord
import logging
import re
from datetime import datetime, timezone
import hashlib
from functools import lru_cache
import time
from typing import Dict, List, Tuple, Optional
import json
import yaml
import os


def extract_clean_query(query: str) -> str:
    """
    Extract a clean search query by removing metadata tags and formatting.

    Args:
        query: The raw query string that may contain metadata tags

    Returns:
        Clean query string suitable for web search
    """
    if not query:
        return "latest information"

    # Remove reply_metadata tags and their content
    query = re.sub(r"<reply_metadata>.*?</reply_metadata>", "", query, flags=re.DOTALL)

    # Remove extra_metadata tags and their content
    query = re.sub(r"<extra_metadata>.*?</extra_metadata>", "", query, flags=re.DOTALL)

    # Remove other common metadata tags
    query = re.sub(
        r"<\|begin_msg_contexts\|diff>.*?<\|end_msg_contexts\|diff>",
        "",
        query,
        flags=re.DOTALL,
    )
    query = re.sub(r"<constraints>.*?</constraints>", "", query, flags=re.DOTALL)

    # Remove any remaining XML-like tags
    query = re.sub(r"<[^>]+>", "", query)

    # Clean up whitespace and newlines
    query = re.sub(r"\n+", " ", query)
    query = re.sub(r"\s+", " ", query)

    # Remove leading/trailing whitespace
    query = query.strip()

    # If the query is empty after cleaning, return a default
    if not query:
        return "latest information"

    return query


def load_exasearch_config() -> Dict:
    """Load ExaSearch configuration from file"""
    config_path = "data/exasearch_config.yaml"

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                logging.info("Loaded ExaSearch configuration from file")
                return config
        else:
            logging.warning(
                f"ExaSearch config file not found at {config_path}, using defaults"
            )
            return {}
    except Exception as e:
        logging.error(f"Error loading ExaSearch config: {e}")
        return {}


class QueryAnalyzer:
    """Advanced query analysis for better search targeting"""

    def __init__(self, config: Dict = None):
        self.config = config or {}

        # Load query patterns from config or use defaults
        query_types_config = self.config.get("query_types", {})

        # Query type patterns with configurable settings
        self.query_patterns = {
            "news": {
                "keywords": query_types_config.get("news", {}).get(
                    "keywords",
                    ["news", "latest", "breaking", "update", "announcement", "recent"],
                ),
                "search_type": query_types_config.get("news", {}).get(
                    "search_type", "neural"
                ),
                "num_results": query_types_config.get("news", {}).get("num_results", 7),
                "enhancements": query_types_config.get("news", {}).get(
                    "enhancements", ["2025", "current events"]
                ),
                "confidence_threshold": query_types_config.get("news", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
            "technical": {
                "keywords": query_types_config.get("technical", {}).get(
                    "keywords",
                    [
                        "how to",
                        "tutorial",
                        "guide",
                        "code",
                        "programming",
                        "api",
                        "framework",
                    ],
                ),
                "search_type": query_types_config.get("technical", {}).get(
                    "search_type", "keyword"
                ),
                "num_results": query_types_config.get("technical", {}).get(
                    "num_results", 5
                ),
                "enhancements": query_types_config.get("technical", {}).get(
                    "enhancements", ["tutorial", "guide", "documentation"]
                ),
                "confidence_threshold": query_types_config.get("technical", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
            "comparison": {
                "keywords": query_types_config.get("comparison", {}).get(
                    "keywords",
                    ["vs", "versus", "compare", "difference", "better", "which"],
                ),
                "search_type": query_types_config.get("comparison", {}).get(
                    "search_type", "neural"
                ),
                "num_results": query_types_config.get("comparison", {}).get(
                    "num_results", 6
                ),
                "enhancements": query_types_config.get("comparison", {}).get(
                    "enhancements", ["comparison", "analysis"]
                ),
                "confidence_threshold": query_types_config.get("comparison", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
            "factual": {
                "keywords": query_types_config.get("factual", {}).get(
                    "keywords", ["what is", "who is", "when", "where", "why", "how"]
                ),
                "search_type": query_types_config.get("factual", {}).get(
                    "search_type", "auto"
                ),
                "num_results": query_types_config.get("factual", {}).get(
                    "num_results", 4
                ),
                "enhancements": query_types_config.get("factual", {}).get(
                    "enhancements", ["definition", "information"]
                ),
                "confidence_threshold": query_types_config.get("factual", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
            "sports": {
                "keywords": query_types_config.get("sports", {}).get(
                    "keywords",
                    [
                        "sports",
                        "football",
                        "basketball",
                        "baseball",
                        "soccer",
                        "game",
                        "match",
                    ],
                ),
                "search_type": query_types_config.get("sports", {}).get(
                    "search_type", "neural"
                ),
                "num_results": query_types_config.get("sports", {}).get(
                    "num_results", 5
                ),
                "enhancements": query_types_config.get("sports", {}).get(
                    "enhancements", ["live", "scores", "results"]
                ),
                "confidence_threshold": query_types_config.get("sports", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
            "financial": {
                "keywords": query_types_config.get("financial", {}).get(
                    "keywords",
                    [
                        "price",
                        "stock",
                        "market",
                        "crypto",
                        "bitcoin",
                        "ethereum",
                        "investment",
                    ],
                ),
                "search_type": query_types_config.get("financial", {}).get(
                    "search_type", "neural"
                ),
                "num_results": query_types_config.get("financial", {}).get(
                    "num_results", 6
                ),
                "enhancements": query_types_config.get("financial", {}).get(
                    "enhancements", ["current", "live", "market data"]
                ),
                "confidence_threshold": query_types_config.get("financial", {}).get(
                    "confidence_threshold", 0.3
                ),
            },
        }

    def analyze_query(self, query: str) -> Dict:
        """Analyze query to determine optimal search parameters"""
        query_lower = query.lower()

        # Determine query type
        query_type = "general"
        confidence = 0.0

        for qtype, pattern in self.query_patterns.items():
            matches = sum(
                1 for keyword in pattern["keywords"] if keyword in query_lower
            )
            if matches > 0:
                confidence = matches / len(pattern["keywords"])
                threshold = pattern.get("confidence_threshold", 0.3)
                if confidence > threshold:  # Use configurable threshold
                    query_type = qtype
                    break

        # Get base parameters for detected type
        base_params = self.query_patterns.get(
            query_type, {"search_type": "auto", "num_results": 5, "enhancements": []}
        )

        # Adjust based on query complexity
        word_count = len(query.split())
        if word_count <= 2:
            base_params["num_results"] = min(base_params["num_results"], 3)
        elif word_count >= 8:
            base_params["num_results"] = min(base_params["num_results"] + 2, 10)

        return {
            "query_type": query_type,
            "confidence": confidence,
            "word_count": word_count,
            "search_type": base_params["search_type"],
            "num_results": base_params["num_results"],
            "enhancements": base_params["enhancements"],
        }


class ResultScorer:
    """Advanced result scoring for better relevance ranking"""

    def __init__(self, config: Dict = None):
        self.config = config or {}

        # Load scoring weights from config
        scoring_weights = self.config.get("scoring_weights", {})

        # Domain authority weights from config or defaults
        domain_weights_config = self.config.get("domain_weights", {})
        self.domain_weights = {
            ".edu": domain_weights_config.get(".edu", 3.0),
            ".gov": domain_weights_config.get(".gov", 3.0),
            "wikipedia.org": domain_weights_config.get("wikipedia.org", 2.5),
            ".org": domain_weights_config.get(".org", 2.0),
            ".com": domain_weights_config.get(".com", 1.0),
            ".net": domain_weights_config.get(".net", 1.0),
            ".io": domain_weights_config.get(".io", 1.5),
            "github.com": domain_weights_config.get("github.com", 2.0),
            "stackoverflow.com": domain_weights_config.get("stackoverflow.com", 2.5),
            "reddit.com": domain_weights_config.get("reddit.com", 1.5),
            "twitter.com": domain_weights_config.get("twitter.com", 1.0),
            "youtube.com": domain_weights_config.get("youtube.com", 1.5),
            "medium.com": domain_weights_config.get("medium.com", 1.5),
            "dev.to": domain_weights_config.get("dev.to", 1.5),
            "hashnode.dev": domain_weights_config.get("hashnode.dev", 1.5),
        }

        # Content quality indicators from config
        content_filters = self.config.get("content_filters", {})
        self.quality_indicators = {
            "min_title_length": content_filters.get("min_title_length", 10),
            "min_summary_length": content_filters.get("min_summary_length", 50),
            "max_title_length": content_filters.get("max_title_length", 200),
            "max_summary_length": content_filters.get("max_summary_length", 500),
        }

        # Scoring weights
        self.title_relevance_weight = scoring_weights.get("title_relevance", 4.0)
        self.summary_quality_weight = scoring_weights.get("summary_quality", 3.0)
        self.date_freshness_weight = scoring_weights.get("date_freshness", 3.0)
        self.domain_authority_weight = scoring_weights.get("domain_authority", 3.0)
        self.content_bonus_weight = scoring_weights.get("content_bonus", 0.5)

    def score_result(self, result: dict, query: str) -> float:
        """Score a search result based on multiple factors"""
        score = 0.0
        query_lower = query.lower()

        # Title relevance (0-4 points)
        title = result.get("title", "").lower()
        if title:
            # Exact phrase matches
            if query_lower in title:
                score += self.title_relevance_weight
            # Word overlap
            query_words = set(query_lower.split())
            title_words = set(title.split())
            overlap = len(query_words.intersection(title_words))
            score += min(overlap * 0.5, self.title_relevance_weight * 0.75)

            # Title length quality
            if len(result["title"]) >= self.quality_indicators["min_title_length"]:
                score += 1

        # Summary quality (0-3 points)
        summary = result.get("summary", "")
        if summary:
            if len(summary) >= self.quality_indicators["min_summary_length"]:
                score += self.summary_quality_weight * 0.67
            # Summary relevance
            if any(word in summary.lower() for word in query_lower.split()):
                score += self.summary_quality_weight * 0.33

        # Date freshness (0-3 points)
        if result.get("publishedDate"):
            try:
                pub_date = datetime.fromisoformat(
                    result["publishedDate"].replace("Z", "+00:00")
                )
                days_old = (datetime.now(timezone.utc) - pub_date).days
                if days_old <= 1:
                    score += self.date_freshness_weight
                elif days_old <= 7:
                    score += self.date_freshness_weight * 0.83
                elif days_old <= 30:
                    score += self.date_freshness_weight * 0.67
                elif days_old <= 90:
                    score += self.date_freshness_weight * 0.33
            except:
                pass

        # Domain authority (0-3 points)
        url = result.get("url", "").lower()
        for domain, weight in self.domain_weights.items():
            if domain in url:
                score += weight
                break

        # Content type bonus
        if result.get("highlights"):
            score += self.content_bonus_weight

        # Penalize very short or very long content based on config
        content_filters = self.config.get("content_filters", {})
        if content_filters.get("penalize_short_titles", True):
            if len(result.get("title", "")) < 5:
                score -= 1
        if content_filters.get("penalize_long_titles", True):
            if len(result.get("title", "")) > 300:
                score -= 0.5

        return max(0, score)  # Ensure non-negative score


# Function implementations
class Tool(ToolManifest):
    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()

        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

        # Load configuration
        self.config = load_exasearch_config()

        # Initialize advanced components with config
        self.query_analyzer = QueryAnalyzer(self.config)
        self.result_scorer = ResultScorer(self.config)

        # Initialize cache for repeated searches
        self._search_cache = {}

        # Get cache settings from config
        search_behavior = self.config.get("search_behavior", {})
        self._cache_ttl = search_behavior.get(
            "cache_ttl", int(environ.get("EXA_SEARCH_CACHE_TTL", "3600"))
        )
        self._max_cache_size = search_behavior.get("max_cache_size", 1000)

        # Performance tracking
        self._search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "query_types": {},
            "success_rate": 0.0,
        }

    async def _enhance_search_query(self, query: str, analysis: Dict) -> str:
        """Enhanced query enhancement based on analysis"""
        # Check if query enhancement is enabled
        query_enhancement = self.config.get("query_enhancement", {})
        if not query_enhancement.get("enabled", True):
            return query

        enhanced_query = query

        # Add type-specific enhancements
        for enhancement in analysis.get("enhancements", []):
            if enhancement not in enhanced_query.lower():
                enhanced_query += f" {enhancement}"

        # Add temporal context for news/financial queries
        if query_enhancement.get("add_temporal_context", True):
            if analysis.get("query_type") in ["news", "financial"]:
                if (
                    "2025" not in enhanced_query
                    and "current" not in enhanced_query.lower()
                ):
                    enhanced_query += " 2025"

        # Add technical context for programming queries
        if query_enhancement.get("add_technical_context", True):
            if analysis.get("query_type") == "technical":
                if (
                    "tutorial" not in enhanced_query.lower()
                    and "guide" not in enhanced_query.lower()
                ):
                    enhanced_query += " tutorial guide"

        # Smart query expansion for short queries
        if query_enhancement.get("expand_short_queries", True):
            if analysis.get("word_count", 0) <= 2:
                # Add context words based on query type
                if analysis.get("query_type") == "factual":
                    enhanced_query += " information details"
                elif analysis.get("query_type") == "news":
                    enhanced_query += " latest news"

        # Limit enhanced query length
        max_length = query_enhancement.get("max_enhanced_length", 200)
        if len(enhanced_query) > max_length:
            enhanced_query = enhanced_query[:max_length].rsplit(" ", 1)[0]

        logging.info(
            f"Enhanced query from '{query}' to '{enhanced_query}' (type: {analysis.get('query_type')})"
        )
        return enhanced_query

    def _get_optimal_search_params(self, analysis: Dict, **kwargs) -> Dict:
        """Get optimal search parameters based on query analysis"""
        params = kwargs.copy()

        # Get default settings from config
        search_behavior = self.config.get("search_behavior", {})

        # Use analysis-based defaults
        if "searchType" not in params:
            params["searchType"] = analysis.get(
                "search_type", search_behavior.get("default_search_type", "auto")
            )

        if "numResults" not in params or params["numResults"] < 1:
            params["numResults"] = analysis.get(
                "num_results", search_behavior.get("default_num_results", 5)
            )

        # Enable highlights and summary by default for better AI processing
        if "showHighlights" not in params:
            params["showHighlights"] = search_behavior.get("enable_highlights", True)
        if "showSummary" not in params:
            params["showSummary"] = search_behavior.get("enable_summaries", True)

        # Validate searchType
        valid_search_types = ["auto", "neural", "keyword"]
        if params["searchType"] not in valid_search_types:
            params["searchType"] = "auto"

        return params

    async def _smart_fallback_search(
        self, query: str, original_error: Exception, analysis: Dict
    ) -> dict:
        """Intelligent fallback search with multiple strategies"""
        # Check if fallback is enabled
        fallback_config = self.config.get("fallback_strategies", {})
        if not fallback_config.get("enabled", True):
            raise original_error

        # Get strategies from config or use defaults
        strategies = fallback_config.get(
            "strategies",
            [
                {
                    "name": "simplified_query",
                    "action": "first_three_words",
                    "params": {"numResults": 3, "searchType": "auto"},
                },
                {
                    "name": "keyword_search",
                    "action": "same_query",
                    "params": {"numResults": 3, "searchType": "keyword"},
                },
                {
                    "name": "neural_search",
                    "action": "same_query",
                    "params": {"numResults": 3, "searchType": "neural"},
                },
                {
                    "name": "broader_search",
                    "action": "first_two_words",
                    "params": {"numResults": 5, "searchType": "auto"},
                },
            ],
        )

        for strategy in strategies:
            try:
                logging.info(f"Trying fallback strategy: {strategy['name']}")

                # Apply strategy action
                action = strategy["action"]
                if action == "first_three_words":
                    modified_query = " ".join(query.split()[:3])
                elif action == "first_two_words":
                    modified_query = " ".join(query.split()[:2])
                elif action == "same_query":
                    modified_query = query
                else:
                    modified_query = query

                if modified_query != query:
                    logging.info(f"Modified query: '{query}' -> '{modified_query}'")

                # Merge strategy params with analysis-based params
                strategy_params = self._get_optimal_search_params(
                    analysis, **strategy["params"]
                )

                result = await self._tool_function_web_search(
                    query=modified_query, **strategy_params
                )

                if result and result.get("results"):
                    logging.info(f"Fallback strategy '{strategy['name']}' succeeded")
                    return result

            except Exception as e:
                logging.warning(f"Fallback strategy '{strategy['name']}' failed: {e}")
                continue

        # If all fallbacks fail, raise original error
        raise original_error

    async def _validate_and_enhance_params(self, **kwargs) -> dict:
        """Validate and enhance search parameters with smart defaults"""
        params = kwargs.copy()

        # Smart numResults based on query complexity
        if "numResults" not in params or params["numResults"] < 1:
            query_words = len(params.get("query", "").split())
            if query_words <= 2:
                params["numResults"] = 3
            elif query_words <= 5:
                params["numResults"] = 5
            else:
                params["numResults"] = 7

        # Enable highlights and summary by default for better AI processing
        if "showHighlights" not in params:
            params["showHighlights"] = True
        if "showSummary" not in params:
            params["showSummary"] = True

        # Validate searchType
        valid_search_types = ["auto", "neural", "keyword"]
        if "searchType" not in params or params["searchType"] not in valid_search_types:
            params["searchType"] = "auto"

        return params

    def _format_for_ai_model(self, output: dict) -> dict:
        """Format search results specifically for AI model consumption"""
        ai_output = output.copy()

        # Add structured insights
        ai_output["key_insights"] = []
        for result in output["results"][:3]:
            insight = {
                "topic": result.get("title", ""),
                "key_points": result.get("highlights", []),
                "relevance_score": self.result_scorer.score_result(
                    result, output.get("query", "")
                ),
            }
            ai_output["key_insights"].append(insight)

        # Add search context
        query_lower = output.get("query", "").lower()
        ai_output["search_context"] = {
            "query_type": "informational" if "what" in query_lower else "research",
            "expected_response_length": "brief"
            if output.get("numResults", 5) <= 3
            else "detailed",
            "search_strategy": "enhanced" if len(query_lower.split()) > 3 else "basic",
        }

        return ai_output

    async def _track_search_performance(
        self, query: str, start_time: float, analysis: Dict
    ):
        """Track search performance metrics with query analysis"""
        # Check if performance tracking is enabled
        performance_config = self.config.get("performance", {})
        if not performance_config.get("enabled", True):
            return

        duration = time.time() - start_time

        # Update statistics
        self._search_stats["total_searches"] += 1
        current_avg = self._search_stats["average_response_time"]
        total_searches = self._search_stats["total_searches"]
        self._search_stats["average_response_time"] = (
            current_avg * (total_searches - 1) + duration
        ) / total_searches

        # Track query types if enabled
        if performance_config.get("track_query_types", True):
            query_type = analysis.get("query_type", "general")
            self._search_stats["query_types"][query_type] = (
                self._search_stats["query_types"].get(query_type, 0) + 1
            )

        logging.info(
            f"Search performance - Query: '{query[:50]}...', Type: {analysis.get('query_type', 'general')}, Duration: {duration:.2f}s, Avg: {self._search_stats['average_response_time']:.2f}s"
        )

        # Log slow searches
        slow_threshold = performance_config.get("slow_search_threshold", 5.0)
        if duration > slow_threshold:
            logging.warning(f"Slow search detected: {duration:.2f}s for query: {query}")

    def _generate_query_hash(self, query: str, params: dict) -> str:
        """Generate hash for caching based on query and parameters"""
        # Sort parameters for consistent hashing
        sorted_params = sorted(params.items())
        query_string = f"{query}:{str(sorted_params)}"
        return hashlib.md5(query_string.encode()).hexdigest()

    def _get_cached_search(self, query_hash: str) -> dict:
        """Get cached search results if available and not expired"""
        if query_hash in self._search_cache:
            cache_entry = self._search_cache[query_hash]
            if time.time() - cache_entry["timestamp"] < self._cache_ttl:
                self._search_stats["cache_hits"] += 1
                logging.info(f"Cache hit for query hash: {query_hash}")
                return cache_entry["data"]
            else:
                # Remove expired cache entry
                del self._search_cache[query_hash]
        return None

    def _cache_search_results(self, query_hash: str, data: dict):
        """Cache search results with timestamp"""
        # Check cache size limit
        if len(self._search_cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = min(
                self._search_cache.keys(),
                key=lambda k: self._search_cache[k]["timestamp"],
            )
            del self._search_cache[oldest_key]

        self._search_cache[query_hash] = {"data": data, "timestamp": time.time()}
        logging.info(f"Cached search results for query hash: {query_hash}")

    async def _summarize_results(self, results: list, query: str) -> str:
        """Generate a concise summary of search results"""
        if not results:
            return f"No results found for '{query}'"

        # Extract key information
        titles = [r.get("title", "") for r in results[:3]]
        summaries = [r.get("summary", "") for r in results[:3] if r.get("summary")]

        # Create natural summary
        summary = f"Found {len(results)} results for '{query}':\n"
        summary += "• " + "\n• ".join(titles[:3])

        if summaries:
            summary += f"\n\nKey insights: {' '.join(summaries[:2])}"

        return summary

    async def _tool_function_web_search(
        self,
        query: str = None,
        searchType: str = "auto",
        numResults: int = 5,
        includeDomains: list = None,
        excludeDomains: list = None,
        includeText: list = None,
        excludeText: list = None,
        showHighlights: bool = False,
        showSummary: bool = False,
    ):
        start_time = time.time()

        try:
            # Validate query parameter
            if not query or not query.strip():
                raise ValueError("query parameter is required and cannot be empty")

            # Clean the query by removing metadata tags
            clean_query = extract_clean_query(query)

            # Analyze the query for optimal search parameters
            analysis = self.query_analyzer.analyze_query(clean_query)

            # Enhance the query based on analysis
            enhanced_query = await self._enhance_search_query(clean_query, analysis)

            # Log the original and cleaned query for debugging
            if clean_query != query.strip():
                logging.info(
                    f"Query cleaned from '{query[:100]}...' to '{clean_query}'"
                )

            # Get optimal search parameters based on analysis
            params = self._get_optimal_search_params(
                analysis,
                query=enhanced_query,
                searchType=searchType,
                numResults=numResults,
                includeDomains=includeDomains,
                excludeDomains=excludeDomains,
                includeText=includeText,
                excludeText=excludeText,
                showHighlights=showHighlights,
                showSummary=showSummary,
            )

            # Check cache first
            query_hash = self._generate_query_hash(enhanced_query, params)
            cached_result = self._get_cached_search(query_hash)
            if cached_result:
                await self._track_search_performance(
                    enhanced_query, start_time, analysis
                )
                return cached_result

            # Check if aiohttp session is available
            if not hasattr(self.discord_bot, "_aiohttp_main_client_session"):
                raise Exception(
                    "aiohttp client session for get requests not initialized and web browsing cannot continue, please check the bot configuration"
                )

            _session: aiohttp.ClientSession = (
                self.discord_bot._aiohttp_main_client_session
            )

            # Check Exa API Key
            _api_key = environ.get("EXA_API_KEY")
            if not _api_key:
                raise ValueError(
                    "EXA_API_KEY key not set. Please set this environment variable to use the web search tool."
                )

            logging.info(
                f"Starting web search for query: '{enhanced_query}' with type: {params['searchType']} (analysis: {analysis['query_type']})"
            )

            _header = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": _api_key,
            }

            # Construct params with proper validation using enhanced query
            _params = {
                "query": enhanced_query,
                "type": params["searchType"],
                "numResults": params["numResults"],
            }

            # Add optional parameters if provided and valid
            if params.get("includeDomains") and isinstance(
                params["includeDomains"], list
            ):
                _params["includeDomains"] = params["includeDomains"]
            if params.get("excludeDomains") and isinstance(
                params["excludeDomains"], list
            ):
                _params["excludeDomains"] = params["excludeDomains"]
            if params.get("includeText") and isinstance(params["includeText"], list):
                _params["includeText"] = params["includeText"]
            if params.get("excludeText") and isinstance(params["excludeText"], list):
                _params["excludeText"] = params["excludeText"]

            # Add contents if needed
            if params.get("showHighlights") or params.get("showSummary"):
                _params["contents"] = {}
                if params.get("showHighlights"):
                    _params["contents"]["highlights"] = True
                if params.get("showSummary"):
                    _params["contents"]["summary"] = True

            # Endpoint
            _endpoint = "https://api.exa.ai/search"

            logging.info(f"Making request to Exa API with params: {_params}")

            # Make a request
            _data = None
            try:
                async with _session.post(
                    _endpoint, headers=_header, json=_params
                ) as _response:
                    # Check if the response is successful
                    if _response.status != 200:
                        _error_text = await _response.text()
                        logging.error(
                            f"Exa API returned status {_response.status}: {_response.reason}. Response: {_error_text}"
                        )
                        raise Exception(
                            f"Exa API returned status code {_response.status}: {_response.reason}"
                        )

                    _data = await _response.json()
                    logging.info(
                        f"Received response from Exa API with {len(_data.get('results', []))} results"
                    )

                    # Check if the data is empty or invalid
                    if not _data or not _data.get("results"):
                        raise Exception("No search results found for the query")

            except aiohttp.ClientConnectionError as e:
                logging.error(f"Connection error to Exa API: {e}")
                raise Exception(f"Failed to connect to Exa API: {str(e)}")
            except aiohttp.ClientError as e:
                logging.error(f"HTTP request failed: {e}")
                raise Exception(f"HTTP request failed: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error during web search: {e}")
                raise Exception(f"Unexpected error during web search: {str(e)}")

            # Ensure we have data before proceeding
            if not _data:
                raise Exception("Failed to retrieve data from Exa API")

            # Build output
            _output = {
                "guidelines": "You must always provide references and format links with [Page Title](Page URL). As possible, rank the most relevant and fresh sources based on dates.",
                "formatting_rules": "Do not provide links as [Page URL](Page URL), always provide a title as this [Page Title](Page URL), if it doesn't just directly send the URL",
                "formatting_reason": "Now the reason for this is Discord doesn't nicely format the links if you don't provide a title",
                "showLinks": "No need to list all references, only most relevant ones",
                "results": [],
                "query": enhanced_query,
                "search_metadata": {
                    "search_type": params["searchType"],
                    "num_results": params["numResults"],
                    "enhanced_query": enhanced_query != clean_query,
                    "query_analysis": analysis,
                },
            }

            # Score and sort results by quality using advanced scoring
            scored_results = []
            for _results in _data["results"]:
                result_data = {
                    "title": _results.get("title"),
                    "url": _results["url"],
                    "summary": _results.get("summary"),
                    "highlights": _results.get("highlights"),
                    "publishedDate": _results.get("publishedDate"),
                }
                score = self.result_scorer.score_result(result_data, enhanced_query)
                scored_results.append((score, result_data))

            # Sort by score (highest first) and take top results
            scored_results.sort(key=lambda x: x[0], reverse=True)
            _output["results"] = [
                result for score, result in scored_results[: params["numResults"]]
            ]

            if not _output["results"]:
                raise Exception("No results fetched from the search response")

            # Cache the results
            self._cache_search_results(query_hash, _output)

            # Format for AI model consumption
            ai_formatted_output = self._format_for_ai_model(_output)

            # Embed that contains first 10 sources
            _sembed = discord.Embed(title="Web Sources")

            # Create a more informative response that includes key insights
            response_text = f"🔍 **Search Results for: {enhanced_query}**\n\n"

            # Add comprehensive information from all results
            if _output["results"]:
                # Always provide key information from the top result
                top_result = _output["results"][0]
                response_text += (
                    f"**Top Result:** {top_result.get('title', 'No title available')}\n"
                )

                if top_result.get("summary"):
                    response_text += f"**Key Finding:** {top_result['summary']}\n\n"
                else:
                    # If no summary, provide the URL and encourage user to visit
                    response_text += (
                        f"**Source:** {top_result.get('url', 'No URL available')}\n"
                    )
                    response_text += (
                        "**Note:** Visit the source for detailed information.\n\n"
                    )

                # Add highlights if available, otherwise use title as key points
                if top_result.get("highlights"):
                    highlights = top_result["highlights"][:5]  # Top 5 highlights
                    response_text += "**Key Points:**\n"
                    for highlight in highlights:
                        response_text += f"• {highlight}\n"
                    response_text += "\n"
                else:
                    # Create key points from the title if no highlights
                    title = top_result.get("title", "")
                    if title:
                        response_text += "**Key Points:**\n"
                        response_text += f"• {title}\n"
                        response_text += (
                            "• Visit the source for comprehensive details\n\n"
                        )

                # Add information from additional results if available
                if len(_output["results"]) > 1:
                    response_text += "**Additional Sources:**\n"
                    for i, result in enumerate(
                        _output["results"][1:4], 2
                    ):  # Results 2-4
                        title = result.get("title", "Untitled Source")
                        url = result.get("url", "")
                        summary = result.get("summary", "")

                        response_text += f"**{i}. {title}**\n"
                        if summary:
                            response_text += f"{summary[:200]}...\n"
                        else:
                            response_text += f"Source: {url}\n"
                        response_text += "\n"

                # Add comprehensive source list with descriptions
                response_text += "**All Sources:**\n"
                for i, result in enumerate(_output["results"][:5], 1):  # Top 5 sources
                    title = result.get("title", "(no title)")
                    url = result.get("url", "")
                    summary = result.get("summary", "")

                    # Use plain text format to avoid link previews
                    response_text += f"{i}. **{title}**\n"
                    response_text += f"   Source: {url}\n"
                    if summary:
                        response_text += f"   {summary[:150]}...\n"
                    response_text += "\n"

                # Add search metadata and guidance
                response_text += f"**Search Info:** Found {len(_output['results'])} relevant sources using {params['searchType']} search.\n"
                response_text += "**Next Steps:** Use the information above to answer your question, or ask me follow-up questions about specific aspects.\n"
                response_text += "All information above is current and sourced directly from the web."
            else:
                response_text += "No results found for your query. Try rephrasing or using different keywords."

            # Try to use enhanced AI processing if available
            try:
                from aimodels.enhanced_web_search import (
                    create_enhanced_web_search_handler,
                )

                # Check if enhanced AI is enabled in config
                enhanced_ai_config = self.config.get("enhanced_ai", {})
                if enhanced_ai_config.get("enabled", True):
                    # Create enhanced AI handler
                    enhanced_handler = create_enhanced_web_search_handler(
                        self.discord_ctx, self.discord_bot
                    )

                    # Process the search results with enhanced AI
                    enhanced_response = (
                        await enhanced_handler.process_web_search_request(
                            enhanced_query, ai_formatted_output
                        )
                    )

                    if enhanced_response and enhanced_response != response_text:
                        # Convert any markdown links in the enhanced response to plain text
                        import re

                        # Replace markdown links [text](url) with just the text and URL on separate lines
                        cleaned_response = re.sub(
                            r"\[([^\]]+)\]\(([^)]+)\)",
                            r"\1\n   Source: \2",
                            enhanced_response,
                        )

                        # Send the enhanced AI response as text (skip basic results)
                        await self.method_send(
                            content=cleaned_response,  # Send as text content
                        )
                        logging.info("Enhanced AI processing completed successfully")
                        # Return early to avoid sending basic results
                        await self._track_search_performance(
                            enhanced_query, start_time, analysis
                        )
                        return ai_formatted_output

            except ImportError:
                logging.info(
                    "Enhanced AI handler not available, using basic search results"
                )
            except Exception as e:
                logging.warning(f"Enhanced AI processing failed: {e}")
                # Check if we should fallback to basic results
                if not enhanced_ai_config.get("fallback_to_basic", True):
                    raise e

            # Only send basic results if enhanced AI failed or wasn't available
            # Create a Discord embed for basic results too
            basic_embed = discord.Embed(
                title="🔍 Web Search Results",
                description=response_text,
                color=0x0099FF,  # Blue color for basic results
                timestamp=discord.utils.utcnow(),
            )

            # Add footer for basic results
            basic_embed.set_footer(
                text="🔍 Basic search results • Links are clickable but won't show previews"
            )

            await self.method_send(
                content=None,  # No content, just the embed
                embed=basic_embed,
            )

            # Track performance
            await self._track_search_performance(enhanced_query, start_time, analysis)

            logging.info(
                f"Web search completed successfully for query: '{enhanced_query}'"
            )
            return ai_formatted_output

        except Exception as e:
            logging.error(f"Web search failed for query '{clean_query}': {e}")

            # Try smart fallback search if primary search fails
            try:
                logging.info("Attempting smart fallback search...")
                fallback_result = await self._smart_fallback_search(
                    clean_query, e, analysis
                )
                await self._track_search_performance(clean_query, start_time, analysis)
                return fallback_result
            except Exception as fallback_e:
                logging.error(f"Smart fallback search also failed: {fallback_e}")
                raise e

    # ------------------------------------------------------------------
    # Compatibility alias
    # ------------------------------------------------------------------
    # Some parts of the codebase expect the default tool entrypoint to be
    # called `_tool_function`.  Provide a thin wrapper that simply
    # forwards the call to the concrete implementation so that older
    # callers continue to work even if they
    # do not append the function name.

    async def _tool_function(self, query: str = None, **kwargs):
        """Generic dispatcher for this tool.

        Some agents sometimes invoke the generic `_tool_function`
        attribute instead of the more specific `_tool_function_<name>`
        variant.  To remain compatible we forward every call directly to
        ``_tool_function_web_search`` because this tool exposes only a
        single capability.
        """
        # Handle both positional and keyword arguments for compatibility
        if query is None and "query" in kwargs:
            query = kwargs["query"]
        elif query is None:
            query = kwargs.get("query", "latest information")

        # Forward to the main implementation
        return await self._tool_function_web_search(query=query, **kwargs)

    async def get_search_stats(self) -> dict:
        """Get search performance statistics"""
        return {
            "total_searches": self._search_stats["total_searches"],
            "cache_hits": self._search_stats["cache_hits"],
            "cache_hit_rate": (
                self._search_stats["cache_hits"]
                / max(self._search_stats["total_searches"], 1)
            )
            * 100,
            "average_response_time": self._search_stats["average_response_time"],
            "cache_size": len(self._search_cache),
            "query_types": self._search_stats["query_types"],
            "success_rate": self._search_stats.get("success_rate", 0.0),
        }
