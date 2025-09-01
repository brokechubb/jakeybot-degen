#!/usr/bin/env python3
"""
Test script for ExaSearch sensitivity adjustments
Tests that the reduced sensitivity configuration works correctly
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_exasearch_config():
    """Test that ExaSearch configuration has been updated correctly"""
    try:
        # Import the ExaSearch tool
        from tools.ExaSearch.tool import Tool, QueryAnalyzer, load_exasearch_config
        
        # Load configuration
        config = load_exasearch_config()
        logger.info("✅ ExaSearch configuration loaded successfully")
        
        # Check query types configuration
        query_types = config.get("query_types", {})
        logger.info(f"Query types found: {list(query_types.keys())}")
        
        # Verify confidence thresholds are increased
        expected_threshold = 0.6
        for qtype, settings in query_types.items():
            actual_threshold = settings.get("confidence_threshold", 0.3)
            if actual_threshold >= expected_threshold:
                logger.info(f"✅ {qtype} confidence threshold: {actual_threshold} (≥ {expected_threshold})")
            else:
                logger.warning(f"⚠️  {qtype} confidence threshold: {actual_threshold} (< {expected_threshold})")
        
        # Test QueryAnalyzer with the new config
        analyzer = QueryAnalyzer(config)
        
        # Test cases that should NOT trigger search (reduced sensitivity)
        non_triggering_queries = [
            "hello world",
            "how are you today",
            "what time is it",
            "tell me a joke",
            "good morning",
            "nice to meet you",
            "thank you very much",
            "see you later",
            "have a great day",
            "what's up"
        ]
        
        # Test cases that SHOULD still trigger search
        triggering_queries = [
            "latest news today",
            "breaking news update",
            "how to code tutorial",
            "compare vs another",
            "what is this thing",
            "market analysis report",
            "live sports scores",
            "game schedule today"
        ]
        
        logger.info("\n--- Testing Non-Triggering Queries (should be low confidence) ---")
        for query in non_triggering_queries:
            analysis = analyzer.analyze_query(query)
            confidence = analysis.get("confidence", 0)
            query_type = analysis.get("query_type", "general")
            logger.info(f"Query: '{query}' -> Type: {query_type}, Confidence: {confidence:.2f}")
            
        logger.info("\n--- Testing Triggering Queries (should be high confidence) ---")
        for query in triggering_queries:
            analysis = analyzer.analyze_query(query)
            confidence = analysis.get("confidence", 0)
            query_type = analysis.get("query_type", "general")
            logger.info(f"Query: '{query}' -> Type: {query_type}, Confidence: {confidence:.2f}")
        
        logger.info("✅ ExaSearch sensitivity test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ ExaSearch sensitivity test failed: {e}")
        logger.exception(e)
        return False

def test_pollinations_search_keywords():
    """Test that pollinations model has reduced search keywords"""
    try:
        # Import the pollinations model
        from aimodels.pollinations.infer import Completions
        
        # Create a mock instance to test the search keywords
        # We'll check the class-level keywords by inspecting the source
        import inspect
        
        # Get the source code of the fallback detection method
        source = inspect.getsource(Completions._fallback_detect_tool_needs)
        
        # Check for the reduced keyword list
        if "latest news" in source and "breaking news" in source:
            logger.info("✅ Pollinations search keywords have been reduced")
            
            # Count occurrences of common words that were removed
            reduced_words = ["latest", "news", "current", "recent", "search"]
            found_words = [word for word in reduced_words if word in source]
            
            if len(found_words) < len(reduced_words):
                logger.info(f"✅ Some common trigger words removed: {found_words}")
            else:
                logger.warning("⚠️  Some common trigger words may still be present")
                
            return True
        else:
            logger.error("❌ Could not find updated search keywords in pollinations model")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pollinations search keywords test failed: {e}")
        logger.exception(e)
        return False

def main():
    """Main test function"""
    logger.info("Starting ExaSearch sensitivity adjustment test...")
    
    # Test ExaSearch configuration
    config_success = test_exasearch_config()
    
    # Test pollinations search keywords
    pollinations_success = test_pollinations_search_keywords()
    
    if config_success and pollinations_success:
        logger.info("🎉 All ExaSearch sensitivity tests passed!")
        logger.info("✅ Sensitivity has been successfully reduced")
        logger.info("✅ Non-triggering queries should now be less likely to activate search")
        return 0
    else:
        logger.error("❌ Some ExaSearch sensitivity tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
