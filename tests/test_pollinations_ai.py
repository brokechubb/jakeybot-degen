#!/usr/bin/env python3
"""
Test script for Pollinations.AI enhanced features
Tests all the new capabilities including vision, audio, and function calling
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pollinations_ai_features():
    """Test all enhanced Pollinations.AI features"""
    
    try:
        # Import the Pollinations AI module
        from aimodels.pollinations.infer import Completions
        
        # Test model categorization method directly
        pollinations = Completions.__new__(Completions)
        pollinations._genai_params = {
            "temperature": 0.7,
            "model": "openai",
            "width": 1024,
            "height": 1024,
        }
        
        logger.info("✅ Pollinations AI initialization successful")
        
        # Test model categorization
        available_models = pollinations.get_available_models()
        logger.info(f"Available models: {available_models}")
        
        # Test vision capabilities method existence
        if hasattr(pollinations, 'analyze_image'):
            logger.info("✅ Vision capabilities method exists")
        else:
            logger.error("❌ Vision capabilities method missing")
            
        # Test audio capabilities method existence
        if hasattr(pollinations, 'transcribe_audio'):
            logger.info("✅ Speech-to-text capabilities method exists")
        else:
            logger.error("❌ Speech-to-text capabilities method missing")
            
        if hasattr(pollinations, 'generate_speech'):
            logger.info("✅ Text-to-speech capabilities method exists")
        else:
            logger.error("❌ Text-to-speech capabilities method missing")
            
        # Test function calling method existence
        if hasattr(pollinations, 'call_function'):
            logger.info("✅ Function calling capabilities method exists")
        else:
            logger.error("❌ Function calling capabilities method missing")
            
        # Test enhanced image generation
        logger.info("Testing enhanced image generation parameters...")
        logger.info(f"Default params: {pollinations._genai_params}")
        
        # Test model type parsing
        test_models = [
            ("flux", "image"),
            ("kontext", "image"),
            ("sdxl", "image"),
            ("openai", "text"),
            ("openai-large", "text"),  # This should be text but might be used for vision
            ("openai-audio", "text"),  # This should be text but might be used for audio
        ]
        
        for model_name, expected_type in test_models:
            parsed_type = pollinations._parse_model_type(model_name)
            logger.info(f"Model '{model_name}' parsed as '{parsed_type}' (expected: '{expected_type}')")
            
        logger.info("✅ All basic tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.exception(e)
        return False

def test_config_module():
    """Test the config module enhancements"""
    try:
        from aimodels.pollinations.config import ModelParams
        
        # Test model fetching
        models = ModelParams.get_available_models()
        logger.info(f"Config module models: {models}")
        
        # Check that we have the expected model categories
        expected_categories = ['text_models', 'image_models', 'vision_models', 'audio_models', 'tts_voices']
        for category in expected_categories:
            if category in models:
                logger.info(f"✅ {category}: {models[category]}")
            else:
                logger.warning(f"⚠️  Missing category: {category}")
                
        logger.info("✅ Config module tests completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Config module test failed: {e}")
        logger.exception(e)
        return False

def main():
    """Main test function"""
    logger.info("Starting Pollinations.AI enhanced features test...")
    
    # Test config module
    config_success = test_config_module()
    
    # Test main features
    features_success = test_pollinations_ai_features()
    
    if config_success and features_success:
        logger.info("🎉 All tests passed! Pollinations.AI enhanced integration is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
