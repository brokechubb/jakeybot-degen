# Built in Tools
from .manifest import ToolManifest
from os import environ
import aiohttp
import discord
import logging


# Function implementations
class Tool(ToolManifest):
    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()

        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

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
        try:
            # Validate query parameter
            if not query or not query.strip():
                raise ValueError("query parameter is required and cannot be empty")

            # Validate searchType parameter
            valid_search_types = ["auto", "neural", "keyword"]
            if searchType not in valid_search_types:
                logging.warning(
                    f"Invalid searchType '{searchType}', defaulting to 'auto'"
                )
                searchType = "auto"

            # Validate numResults parameter
            if not isinstance(numResults, int) or numResults < 1 or numResults > 10:
                logging.warning(f"Invalid numResults {numResults}, defaulting to 5")
                numResults = 5

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
                f"Starting web search for query: '{query}' with type: {searchType}"
            )

            _header = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": _api_key,
            }

            # Construct params with proper validation
            _params = {
                "query": query.strip(),
                "type": searchType,
                "numResults": numResults,
            }

            # Add optional parameters if provided and valid
            if includeDomains and isinstance(includeDomains, list):
                _params["includeDomains"] = includeDomains
            if excludeDomains and isinstance(excludeDomains, list):
                _params["excludeDomains"] = excludeDomains
            if includeText and isinstance(includeText, list):
                _params["includeText"] = includeText
            if excludeText and isinstance(excludeText, list):
                _params["excludeText"] = excludeText

            # Add contents if needed
            if showHighlights or showSummary:
                _params["contents"] = {}
                if showHighlights:
                    _params["contents"]["highlights"] = True
                if showSummary:
                    _params["contents"]["summary"] = True

            # Endpoint
            _endpoint = "https://api.exa.ai/search"

            logging.info(f"Making request to Exa API with params: {_params}")

            # Make a request
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

            # Build output
            _output = {
                "guidelines": "You must always provide references and format links with [Page Title](Page URL). As possible, rank the most relevant and fresh sources based on dates.",
                "formatting_rules": "Do not provide links as [Page URL](Page URL), always provide a title as this [Page Title](Page URL), if it doesn't just directly send the URL",
                "formatting_reason": "Now the reason for this is Discord doesn't nicely format the links if you don't provide a title",
                "showLinks": "No need to list all references, only most relevant ones",
                "results": [],
            }

            for _results in _data["results"]:
                # Append the data
                _output["results"].append(
                    {
                        "title": _results.get("title"),
                        "url": _results["url"],
                        "summary": _results.get("summary"),
                        "highlights": _results.get("highlights"),
                        "publishedDate": _results.get("publishedDate"),
                    }
                )

            if not _output["results"]:
                raise Exception("No results fetched from the search response")

            # Embed that contains first 10 sources
            _sembed = discord.Embed(title="Web Sources")

            # Iterate description
            _desclinks = []
            for _results in _output["results"]:
                if len(_desclinks) <= 10:
                    _title_safe = _results.get("title", "(no title)").replace("/", " ")
                    _desclinks.append(f"- [{_title_safe}]({_results['url']})")
                else:
                    _desclinks.append("...and more results")
                    break
            _sembed.description = "\n".join(_desclinks)
            _sembed.set_footer(text="Used search tool powered by Exa to fetch results")
            await self.method_send(f"🔍 Searched for **{query}**", embed=_sembed)

            logging.info(f"Web search completed successfully for query: '{query}'")
            return _output

        except Exception as e:
            logging.error(f"Web search failed for query '{query}': {e}")
            raise

    # ------------------------------------------------------------------
    # Compatibility alias
    # ------------------------------------------------------------------
    # Some parts of the codebase expect the default tool entrypoint to be
    # called `_tool_function`.  Provide a thin wrapper that simply
    # forwards the call to the concrete implementation so that older
    # callers (e.g. aimodels.gemini.infer) continue to work even if they
    # do not append the function name.

    async def _tool_function(self, **kwargs):
        """Generic dispatcher for this tool.

        The Gemini agent sometimes invokes the generic `_tool_function`
        attribute instead of the more specific `_tool_function_<name>`
        variant.  To remain compatible we forward every call directly to
        ``_tool_function_web_search`` because this tool exposes only a
        single capability.
        """
        return await self._tool_function_web_search(**kwargs)
