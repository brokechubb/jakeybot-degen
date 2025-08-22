class ToolManifest:
    tool_human_name = "Memory Recall"
    memory_recall_description = "Automatically remember and recall information from previous conversations. Use this to store facts about users, preferences, or any information that should be remembered for future conversations."

    def __init__(self):
        self.tool_schema = [
            {
                "name": "remember_fact",
                "description": "Store a new fact in memory for future recall",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fact": {
                            "type": "string",
                            "description": "The fact or information to remember (e.g., 'User likes pizza', 'User's favorite color is blue')",
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category for organizing the fact (e.g., 'preferences', 'personal_info', 'interests')",
                        },
                        "expires_in": {
                            "type": "string",
                            "description": "Optional expiration time (e.g., '1d', '2h', '30m', 'never' for permanent)",
                        },
                    },
                    "required": ["fact"],
                },
            },
            {
                "name": "recall_fact",
                "description": "Search for and retrieve relevant facts from memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant facts (e.g., 'user name', 'favorite food', 'preferences')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of facts to return (default: 3, max: 10)",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "list_facts",
                "description": "List all facts in a specific category or all facts if no category specified",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Optional category to filter facts by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of facts to return (default: 10, max: 20)",
                        },
                    },
                    "required": [],
                },
            },
        ]

        self.tool_schema_openai = [
            {"type": "function", "function": _schema} for _schema in self.tool_schema
        ]

        # Basic schema for Gemini models (without the OpenAI wrapper)
        self.tool_schema_basic = self.tool_schema
