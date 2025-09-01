"""
Enhanced Web Search AI Model Handler

This module provides intelligent web search capabilities using more capable AI models
(GPT-4, Claude, Gemini) that can process tool results and provide meaningful insights.
"""

import logging
import aiohttp
import json
from typing import Optional, Dict, Any
from os import environ
from datetime import datetime


class EnhancedWebSearchAI:
    """
    AI model handler for web search requests that requires tool calling capabilities.
    Routes requests to the most appropriate AI model based on capabilities and availability.
    """

    def __init__(self, discord_ctx, discord_bot, guild_id: int = None):
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot
        self.guild_id = guild_id

        # Available AI models with tool calling capabilities
        self.capable_models = {
            "openai": {
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "api_key": environ.get("OPENAI_API_KEY"),
                "base_url": environ.get("OPENAI_API_ENDPOINT"),
                "capabilities": ["tool_calling", "web_search", "reasoning"],
            },
            "anthropic": {
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "api_key": environ.get("ANTHROPIC_API_KEY"),
                "base_url": "https://api.anthropic.com",
                "capabilities": ["tool_calling", "web_search", "reasoning"],
            },
            "google": {
                "models": ["gemini-2.5-flash", "gemini-2.5-flash-lite"],
                "api_key": environ.get("GOOGLE_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com",
                "capabilities": ["tool_calling", "web_search", "reasoning"],
            },
        }

        # Remove models without API keys
        self.available_models = {
            provider: config
            for provider, config in self.capable_models.items()
            if config["api_key"]
        }

        logging.info(
            f"Enhanced Web Search AI initialized with {len(self.available_models)} available providers"
        )

    async def process_web_search_request(
        self, query: str, search_results: Dict[str, Any]
    ) -> str:
        """
        Process web search results using a capable AI model to provide intelligent insights.

        Args:
            query: The original user query
            search_results: Results from the ExaSearch tool

        Returns:
            Intelligent response using the search results
        """

        if not self.available_models:
            # Fallback to basic processing if no capable models available
            return await self._fallback_processing(query, search_results)

        # Try to use the best available model
        for provider, config in self.available_models.items():
            try:
                response = await self._call_ai_model(
                    provider, config, query, search_results
                )
                if response and response.strip():  # Check for non-empty response
                    return response
                else:
                    logging.info(
                        f"{provider} model returned empty response, trying next model"
                    )
                    continue
            except Exception as e:
                logging.warning(f"Failed to use {provider} model: {e}")
                continue

        # If all capable models fail, use fallback
        return await self._fallback_processing(query, search_results)

    async def _call_ai_model(
        self,
        provider: str,
        config: Dict[str, Any],
        query: str,
        search_results: Dict[str, Any],
    ) -> Optional[str]:
        """Call a specific AI model to process web search results."""

        try:
            if provider == "openai":
                return await self._call_openai_model(config, query, search_results)
            elif provider == "anthropic":
                return await self._call_anthropic_model(config, query, search_results)
            elif provider == "google":
                return await self._call_google_model(config, query, search_results)
        except Exception as e:
            logging.error(f"Error calling {provider} model: {e}")
            return None

    async def _call_openai_model(
        self, config: Dict[str, Any], query: str, search_results: Dict[str, Any]
    ) -> str:
        """Call OpenAI model with tool calling capabilities."""

        # Prepare the conversation with search results
        messages = [
            {
                "role": "system",
                "content": f"""You are Jakey and today is {datetime.now().strftime("%B %d, %Y")}. The time is {datetime.now().strftime("%H:%M %z")}. You're cynical, sarcastic, unfiltered, uncensored, and unapologetic gambler but right now you're a witty and sharp **WORLD WIDE WEB INVESTIGATOR**, a finder of facts, that has been tasked to use the **TOOLS AVAILABLE** to answer **ANY** question that has been asked of you.

**Your Directive:**
Analyze the search results and give users a comprehensive, Jakey-style response that:
1. **Give them the real story** - use the search results to answer their question directly.
2. **Connects the dots** - find patterns and insights across multiple sources
3. **Adds your take** - provide your own analysis and perspective.
4. **DO NOT REFERENCE SOURCE URLS** - DO NOT REFERENCE SOURCE URLS
5. **Keep it real** - maintain your degenerate gambler personality throughout.

**Response Style:**
- Keep it short and concise.
- Start with a Jakey-style reaction to what you found.
- Give them the key information in your own words
- Add your analysis and insights

**Important:** Always use the search results provided - ***don't make shit up***. But give it your own spin and personality.

Remember: You're Jakey, not some generic AI assistant. Act like it!

User Question: {query}

Search Results: {json.dumps(search_results, indent=2)}""",
            },
            {
                "role": "user",
                "content": f"User Question: {query}\n\nSearch Results: {json.dumps(search_results, indent=2)}\n\nGive me the Jakey take on this - what's the answer I am looking for?",
            },
        ]

        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        data = {
            "model": config["models"][0],  # Use first available model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        base_url = config["base_url"] or "https://api.openai.com"
        url = f"{base_url}/v1/chat/completions"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"OpenAI API error: {response.status}")

    async def _call_anthropic_model(
        self, config: Dict[str, Any], query: str, search_results: Dict[str, Any]
    ) -> str:
        """Call Anthropic Claude model with tool calling capabilities."""

        # Prepare the conversation with search results
        messages = [
            {
                "role": "user",
                "content": f"""You are Jakey and today is {datetime.now().strftime("%B %d, %Y")}. The time is {datetime.now().strftime("%H:%M %z")}. You're cynical, sarcastic, unfiltered, uncensored, and unapologetic gambler but right now you're a witty and sharp **WORLD WIDE WEB INVESTIGATOR**, a finder of facts, that has been tasked to use the **TOOLS AVAILABLE** to answer **ANY** question that has been asked of you.

**Your Directive:**
Analyze the search results and give users a comprehensive, Jakey-style response that:
1. **Give them the real story** - use the search results to answer their question directly.
2. **Connects the dots** - find patterns and insights across multiple sources
3. **Adds your take** - provide your own analysis and perspective.
4. **DO NOT REFERENCE SOURCE URLS** - DO NOT REFERENCE SOURCE URLS
5. **Keep it real** - maintain your degenerate gambler personality throughout.

**Response Style:**
- Keep it short and concise.
- Start with a Jakey-style reaction to what you found.
- Give them the key information in your own words
- Add your analysis and insights

**Important:** Always use the search results provided - ***don't make shit up***. But give it your own spin and personality.

Remember: You're Jakey, not some generic AI assistant. Act like it!

User Question: {query}

Search Results: {json.dumps(search_results, indent=2)}""",
            }
        ]

        # Call Anthropic Claude API
        headers = {
            "x-api-key": config["api_key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        data = {
            "model": config["models"][0],  # Use first available model
            "max_tokens": 1000,
            "messages": messages,
            "temperature": 0.7,
            "system": "You are Jakey, the Courtyard's degenerate gambling mascot. Be cynical, sarcastic, and unfiltered while providing accurate information from the search results.",
        }

        url = f"{config['base_url']}/v1/messages"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()

                    # Extract the generated text from Claude's response
                    if "content" in result and len(result["content"]) > 0:
                        content_block = result["content"][0]
                        if "text" in content_block:
                            return content_block["text"]

                    # Fallback if response structure is unexpected
                    logging.warning(f"Unexpected Claude response structure: {result}")
                    raise Exception("Unexpected response structure from Claude API")
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Claude API error: {response.status} - {error_text}"
                    )

    async def _call_google_model(
        self, config: Dict[str, Any], query: str, search_results: Dict[str, Any]
    ) -> str:
        """Call Google Gemini model with tool calling capabilities."""

        # Prepare the conversation with search results
        messages = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"""You are Jakey and today is {datetime.now().strftime("%B %d, %Y")}. The time is {datetime.now().strftime("%H:%M %z")}. You're cynical, sarcastic, unfiltered, uncensored, and unapologetic gambler but right now you're a witty and sharp **WORLD WIDE WEB INVESTIGATOR**, a finder of facts, that has been tasked to use the **TOOLS AVAILABLE** to answer **ANY** request that has been asked of you.

**Your Directive:**
Analyze the search results and give users a comprehensive, Jakey-style response that:
1. **Give them the real story** - use the search results to answer their question directly.
2. **Connects the dots** - find patterns and insights across multiple sources
3. **Adds your take** - provide your own analysis and perspective.
4. **DO NOT REFERENCE SOURCE URLS** - DO NOT REFERENCE SOURCE URLS
5. **Keep it real** - maintain your degenerate gambler personality throughout.

**Response Style:**
- Keep it short and concise.
- Start with a Jakey-style reaction to what you found.
- Give them the key information in your own words
- Add your analysis and insights

**Important:** Always use the search results provided - ***DON'T MAKE SHIT UP***. But give it your own spin and personality.

Remember: You're Jakey, not some generic AI assistant. Act like it!

User Question: {query}

Search Results: {json.dumps(search_results, indent=2)}"""
                    }
                ],
            }
        ]

        # Call Google Gemini API
        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": messages,
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 4000,
                "topP": 0.8,
                "topK": 40,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ],
        }

        # Use the first available Gemini model
        model_name = config["models"][0]
        url = f"{config['base_url']}/v1beta/models/{model_name}:generateContent?key={config['api_key']}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()

                    # Extract the generated text from Gemini's response
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]

                        # Check if we have content with parts
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            if len(parts) > 0 and "text" in parts[0]:
                                return parts[0]["text"]

                        # Check if we have direct content
                        elif "content" in candidate and isinstance(
                            candidate["content"], str
                        ):
                            return candidate["content"]

                        # Check if content is empty due to token limits
                        elif (
                            "content" in candidate
                            and candidate["content"].get("role") == "model"
                        ):
                            if candidate.get("finishReason") == "MAX_TOKENS":
                                logging.warning(
                                    "Gemini hit token limit, using fallback processing"
                                )
                                return None  # This will trigger fallback processing
                            else:
                                logging.warning(
                                    f"Gemini response has no content: {candidate}"
                                )
                                return None

                    # Fallback if response structure is unexpected
                    logging.warning(f"Unexpected Gemini response structure: {result}")
                    return None  # Return None instead of raising exception to trigger fallback
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Gemini API error: {response.status} - {error_text}"
                    )

    async def _fallback_processing(
        self, query: str, search_results: Dict[str, Any]
    ) -> str:
        """Fallback processing when no capable AI models are available."""

        # Basic intelligent processing using the search results
        results = search_results.get("results", [])
        if not results:
            return f"Listen here, I searched for '{query}' but came up empty-handed. Either there's nothing out there worth finding, or you need to rephrase that question. Try being more specific - I'm not a mind reader, you know."

        # Extract key information
        top_result = results[0]
        title = top_result.get("title", "Unknown source")
        summary = top_result.get("summary", "")
        url = top_result.get("url", "")

        # Create a Jakey-style response
        response = f"Alright, let me give you the rundown on '{query}'. Here's what I dug up:\n\n"

        if summary:
            response += f"**{summary}**\n\n"

        response += f"**{title}**\n"
        response += f"{url}\n\n"

        # Add additional sources if available
        if len(results) > 1:
            response += "**Some Links:**\n"
            for i, result in enumerate(results[1:5], 2):
                result_title = result.get("title", "Unknown")
                result_url = result.get("url", "")
                response += f"{i}. {result_title}\n"
                response += f"{result_url}\n"

        response += f"\n**Bottom Line:** I found {len(results)} sources for your query about '{query}'. \n"
        response += (
            "The info above is current and straight from the web - no bullshit here. \n"
        )
        response += "Now you've got the data, so use it wisely. And remember, knowledge is power, but knowing how to use it is where the real money is made.\n\n"

        return response


# Factory function to create the appropriate handler
def create_enhanced_web_search_handler(discord_ctx, discord_bot, guild_id: int = None):
    """Create an enhanced web search AI handler."""
    return EnhancedWebSearchAI(discord_ctx, discord_bot, guild_id)
