class ToolManifest:
    tool_human_name = "Image Generation and Editing"
    image_generator_tool_description = "Generate or edit images using Pollinations.AI with advanced models like Flux, Kontext, and SDXL"

    def __init__(self):
        self.tool_schema = [
            {
                "name": "image_generator",
                "description": self.image_generator_tool_description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The detailed prompt describing the image you want to generate. Be specific about style, composition, colors, and mood.",
                        },
                        "url_context": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of image URLs to use as reference for image-to-image generation. The first image will be used as the base for editing/remixing.",
                        },
                    },
                    "required": ["prompt"],
                },
            }
        ]

        self.tool_schema_openai = [
            {"type": "function", "function": _schema} for _schema in self.tool_schema
        ]
