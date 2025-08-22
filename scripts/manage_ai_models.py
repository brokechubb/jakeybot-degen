#!/usr/bin/env python3
"""
AI Model Management Script for JakeyBot

This script helps you manage AI models - view available models,
check configuration status, and get setup guidance.

Usage:
    python scripts/manage_ai_models.py                    # Show all models
    python scripts/manage_ai_models.py status <model>     # Show model status
    python scripts/manage_ai_models.py config <model>     # Show config requirements
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_available_ai_models():
    """Get list of available AI models from the aimodels directory"""
    aimodels_dir = Path("aimodels")
    if not aimodels_dir.exists():
        return []

    available_models = []
    for model_dir in aimodels_dir.iterdir():
        if model_dir.is_dir() and (model_dir / "__init__.py").exists():
            available_models.append(model_dir.name)

    return sorted(available_models)


def get_model_info(model_name):
    """Get information about a specific AI model"""
    model_dir = Path("aimodels") / model_name
    if not model_dir.exists():
        return None

    info = {
        "name": model_name,
        "exists": True,
        "files": [],
        "config_file": None,
        "init_file": None,
    }

    # Check files
    for file_path in model_dir.iterdir():
        if file_path.is_file():
            info["files"].append(file_path.name)

    # Check for config file
    if "config.py" in info["files"]:
        info["config_file"] = True

    # Check for init file
    if "__init__.py" in info["files"]:
        info["init_file"] = True

    return info


def get_model_config_requirements(model_name):
    """Get configuration requirements for a specific model"""
    config_requirements = {
        "openai": {
            "env_vars": ["OPENAI_API_KEY"],
            "description": "OpenAI GPT models (GPT-4, GPT-3.5-turbo)",
            "setup_url": "https://platform.openai.com/api-keys",
        },
        "claude": {
            "env_vars": ["CLAUDE_API_KEY"],
            "description": "Anthropic Claude models",
            "setup_url": "https://console.anthropic.com/",
        },
        "gemini": {
            "env_vars": ["GOOGLE_API_KEY"],
            "description": "Google Gemini models",
            "setup_url": "https://makersuite.google.com/app/apikey",
        },
        "google": {
            "env_vars": ["GOOGLE_API_KEY"],
            "description": "Google AI models",
            "setup_url": "https://makersuite.google.com/app/apikey",
        },
        "kimi": {
            "env_vars": ["KIMI_API_KEY"],
            "description": "Kimi AI models",
            "setup_url": "https://kimi.moonshot.cn/",
        },
        "xai": {
            "env_vars": ["XAI_API_KEY"],
            "description": "xAI Grok models",
            "setup_url": "https://console.x.ai/",
        },
        "openrouter": {
            "env_vars": ["OPENROUTER_API_KEY"],
            "description": "OpenRouter (access to multiple models)",
            "setup_url": "https://openrouter.ai/keys",
        },
        "azure_foundry": {
            "env_vars": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
            "description": "Azure OpenAI models",
            "setup_url": "https://azure.microsoft.com/en-us/products/cognitive-services/openai-service",
        },
    }

    return config_requirements.get(
        model_name.lower(),
        {
            "env_vars": ["UNKNOWN_API_KEY"],
            "description": "Unknown model type",
            "setup_url": "Check model documentation",
        },
    )


def check_model_configuration(model_name):
    """Check if a model is properly configured"""
    config_req = get_model_config_requirements(model_name)
    missing_vars = []

    for env_var in config_req["env_vars"]:
        if not os.getenv(env_var):
            missing_vars.append(env_var)

    return {
        "configured": len(missing_vars) == 0,
        "missing_vars": missing_vars,
        "config_req": config_req,
    }


def show_model_status(model_name):
    """Show detailed status of a specific AI model"""
    model_info = get_model_info(model_name)
    if not model_info:
        print(f"❌ AI Model '{model_name}' not found")
        return

    print(f"\n🤖 AI Model Status: {model_name}")
    print("=" * 50)

    # File status
    print("📁 Files:")
    for file in sorted(model_info["files"]):
        status = "✅" if file in ["__init__.py", "config.py", "infer.py"] else "📄"
        print(f"   {status} {file}")

    # Configuration status
    config_status = check_model_configuration(model_name)
    print(f"\n⚙️  Configuration:")
    if config_status["configured"]:
        print("   ✅ Fully configured")
    else:
        print("   ❌ Missing configuration")
        print("   Missing environment variables:")
        for var in config_status["missing_vars"]:
            print(f"     - {var}")

    # Configuration requirements
    config_req = config_status["config_req"]
    print(f"\n📋 Requirements:")
    print(f"   Description: {config_req['description']}")
    print(f"   Environment variables: {', '.join(config_req['env_vars'])}")
    print(f"   Setup URL: {config_req['setup_url']}")


def show_all_models_status():
    """Show status of all available AI models"""
    models = get_available_ai_models()
    if not models:
        print("❌ No AI models found in aimodels/ directory")
        return

    print("🤖 JakeyBot AI Models Status")
    print("=" * 50)

    configured_count = 0
    for model in models:
        config_status = check_model_configuration(model)
        status_icon = "✅" if config_status["configured"] else "❌"
        print(
            f"{status_icon} {model:<20} {'Configured' if config_status['configured'] else 'Not configured'}"
        )
        if config_status["configured"]:
            configured_count += 1

    print(f"\n📊 Total models: {len(models)}")
    print(f"✅ Configured: {configured_count}")
    print(f"❌ Not configured: {len(models) - configured_count}")


def show_model_config_help(model_name):
    """Show configuration help for a specific model"""
    config_req = get_model_config_requirements(model_name)

    print(f"\n🔧 Configuration Help: {model_name}")
    print("=" * 50)
    print(f"Description: {config_req['description']}")
    print(f"Setup URL: {config_req['setup_url']}")

    print(f"\n📝 Required environment variables:")
    for env_var in config_req["env_vars"]:
        print(f"   {env_var}")

    print(f"\n💡 Add these to your .env file:")
    for env_var in config_req["env_vars"]:
        print(f"   {env_var}=your_api_key_here")

    print(f"\n🔒 Security reminder:")
    print("   - Never commit your .env file to version control")
    print("   - Keep your API keys secure and private")
    print("   - Run 'python scripts/security_check.py' to verify security")


def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Show all models status
        show_all_models_status()
        return

    command = sys.argv[1].lower()

    if command == "status" and len(sys.argv) == 3:
        model_name = sys.argv[2]
        show_model_status(model_name)
    elif command == "config" and len(sys.argv) == 3:
        model_name = sys.argv[2]
        show_model_config_help(model_name)
    else:
        print("Usage:")
        print(
            "  python scripts/manage_ai_models.py                    # Show all models"
        )
        print(
            "  python scripts/manage_ai_models.py status <model>     # Show model status"
        )
        print(
            "  python scripts/manage_ai_models.py config <model>     # Show config help"
        )
        print("\nExamples:")
        print("  python scripts/manage_ai_models.py status openai")
        print("  python scripts/manage_ai_models.py config claude")
        print("\nAvailable models:")
        models = get_available_ai_models()
        for model in models:
            print(f"   - {model}")


if __name__ == "__main__":
    main()
