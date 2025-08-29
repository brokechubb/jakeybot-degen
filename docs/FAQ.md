# Frequently Asked Questions (FAQ)

## General Questions

### What is JakeyBot?

JakeyBot is a Discord bot powered by advanced AI models, designed to provide intelligent responses, web search capabilities, image generation, and more. It's particularly known for its unique personality and comprehensive toolset.

### How do I get started with JakeyBot?

1. Invite JakeyBot to your Discord server
2. Set up the required environment variables (see Configuration section)
3. Start chatting! JakeyBot will automatically detect when you need web search, calculations, or other tools.

## Model and AI Questions

### Which AI models does JakeyBot support?

JakeyBot supports multiple AI models including:

- **Pollinations.AI models**: Evil (text), Flux (image generation), Kontext (image-to-image), SDXL (image generation)
- **OpenAI models**: GPT-4, GPT-3.5-turbo (if configured)
- **Anthropic models**: Claude (if configured)
- **Google models**: Gemini (if configured)

### How do I change the AI model?

Use the `/model` command followed by the model name:

- `/model pollinations::evil` - For text responses
- `/model pollinations::flux` - For image generation
- `/model pollinations::kontext` - For image-to-image generation

### Can I attach files to my messages?

**Yes, but only with specific models:**

- **Image files**: Use `/model pollinations::flux` or `/model pollinations::kontext` for image generation and processing
- **Text models**: The text models (like `pollinations::evil`) do not support file attachments

**Supported file types:**

- Images: PNG, JPG, JPEG, GIF, WebP
- Only image files are currently supported

**Error message**: If you get an error about file attachments not being supported, switch to an image generation model using `/model pollinations::flux`.

## Tool and Feature Questions

### What tools does JakeyBot have?

JakeyBot includes several powerful tools:

- **Web Search**: Automatically searches the internet for current information
- **Memory**: Remembers personal information and conversation context
- **Currency Converter**: Converts between different currencies
- **Crypto Price**: Gets real-time cryptocurrency prices
- **Code Execution**: Performs calculations and runs code
- **Image Generation**: Creates images from text descriptions

### How does the web search work?

JakeyBot automatically detects when you need web search and uses ExaSearch to find relevant, current information. It analyzes your query type and uses the most appropriate search strategy for better results.

### How does the memory system work?

JakeyBot can remember personal information you share, such as:

- Your name and preferences
- Important dates and events
- Personal interests and details
- Conversation context

The memory is private to each user and helps provide more personalized responses.

### Can JakeyBot generate images?

Yes! Use `/model pollinations::flux` and then describe the image you want. JakeyBot will generate images based on your description.

### Can JakeyBot process existing images?

Yes! Use `/model pollinations::kontext` and attach an image file. You can then describe modifications or variations you want to create.

## Configuration Questions

### What environment variables do I need?

Essential variables:

- `DISCORD_TOKEN` - Your Discord bot token
- `EXA_API_KEY` - For web search (optional but recommended)
- `POLLINATIONS_API_KEY` - For AI responses and image generation

Optional variables:

- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Claude models
- `GOOGLE_API_KEY` - For Gemini models

### How do I set up the bot?

1. Clone the repository
2. Copy `dev.env.template` to `dev.env`
3. Fill in your environment variables
4. Install dependencies: `pip install -r requirements.txt`
5. Run the bot: `python main.py`

## Troubleshooting

### The bot isn't responding

1. Check if the bot is online in Discord
2. Verify your environment variables are set correctly
3. Check the logs for error messages
4. Ensure the bot has proper permissions in your server

### Web search isn't working

1. Verify your `EXA_API_KEY` is set correctly
2. Check if the bot has internet access
3. Look for error messages in the logs
4. Try rephrasing your question

### Image generation isn't working

1. Make sure you're using an image generation model (`/model pollinations::flux`)
2. Verify your `POLLINATIONS_API_KEY` is set
3. Check that your prompt is descriptive enough
4. Look for error messages in the logs

### File attachments aren't working

1. **For images**: Use `/model pollinations::flux` or `/model pollinations::kontext`
2. **For text models**: File attachments are not supported
3. Ensure the file is an image (PNG, JPG, JPEG, GIF, WebP)
4. Check file size limits

### Memory isn't working

1. Make sure you're sharing personal information (names, preferences, etc.)
2. The memory system works automatically - no special commands needed
3. Check that the database is properly configured
4. Look for error messages in the logs

## Advanced Questions

### Can I customize the bot's personality?

Yes! The bot's personality is defined in the system prompts and can be modified in the configuration files.

### How do I add new tools?

Tools can be added by creating new tool modules in the `tools/` directory and updating the configuration files.

### Can I use my own AI models?

Yes, you can integrate custom AI models by creating new model handlers in the `aimodels/` directory.

### How do I monitor bot performance?

The bot includes comprehensive logging and performance monitoring. Check the logs for detailed information about tool usage, response times, and errors.

### Is the bot's memory private?

Yes, the memory system is designed to be private and secure. Each user's memories are stored separately and are not shared between users.

## Support

### Where can I get help?

- Check the documentation in the `docs/` directory
- Look at the logs for error messages
- Review the configuration files for settings
- Check the GitHub repository for issues and updates

### How do I report bugs?

Please report bugs through the GitHub repository with:

- A description of the issue
- Steps to reproduce
- Error messages from the logs
- Your configuration (without sensitive data)
