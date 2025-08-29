# 🔧 Auto-Tool Detection Sensitivity Guide

JakeyBot now features **configurable auto-tool detection sensitivity** to prevent over-triggering and provide a more controlled experience.

## 🎯 What is Auto-Tool Sensitivity?

The auto-tool detection system analyzes user messages to determine when tools should be automatically enabled. The sensitivity settings control how easily this detection triggers, allowing you to fine-tune the behavior.

### **Default Behavior (Conservative)**

- **Higher confidence thresholds** - Tools only activate when very confident
- **Explicit keyword requirements** - Requires clear tool-specific language
- **Cooldown periods** - Prevents rapid tool switching
- **Repetition penalties** - Reduces sensitivity for repeated usage

## 🛠️ Configuration Options

### **Global Settings**

- **`enabled`**: Master switch for auto-tool detection (true/false)
- **`confidence_threshold`**: Minimum confidence score (0.0-1.0, higher = less sensitive)
- **`min_message_length`**: Minimum words required to trigger detection
- **`require_explicit_keywords`**: Require clear tool-specific language
- **`fuzzy_matching`**: Enable approximate keyword matching

### **Tool-Specific Settings**

Each tool has its own sensitivity configuration:

#### **ExaSearch (Web Search)**

- **`confidence_threshold`**: 0.8 (default) - Higher = less sensitive
- **`strong_keywords`**: High-confidence triggers like "search for", "find information"
- **`weak_keywords`**: Lower-confidence triggers like "latest", "news", "current"
- **`min_weak_keywords`**: Number of weak keywords required (default: 2)
- **`require_sports_context`**: Require additional context for sports queries

#### **CryptoPrice**

- **`confidence_threshold`**: 0.9 (default) - Very conservative
- **`require_both_keywords`**: Require both price keyword AND crypto token

#### **CurrencyConverter**

- **`confidence_threshold`**: 0.85 (default) - Conservative
- **`require_conversion_format`**: Require explicit conversion format (e.g., "100 USD to EUR")

#### **CodeExecution**

- **`confidence_threshold`**: 0.95 (default) - Very conservative
- **`require_explicit_calc`**: Require explicit calculation request

#### **Memory**

- **`confidence_threshold`**: 0.7 (default) - More sensitive for personal info
- **`require_explicit_memory`**: Require explicit memory storage request

### **Advanced Settings**

- **`cooldown_period`**: Seconds between auto-tool activations (default: 60s)
- **`repetition_penalty`**: Penalty for repeated tool usage (default: 0.15)
- **`learn_user_preferences`**: Adjust sensitivity based on user behavior
- **`context_aware`**: Consider conversation history for detection

## 📋 Commands

### **View Current Settings**

```
/auto_tool_sensitivity action:view
```

**Example Output:**

```
🔧 Auto-Tool Detection Settings

Global Settings:
• Enabled: True
• Confidence Threshold: 0.80
• Min Message Length: 3
• Require Explicit Keywords: True

Tool-Specific Settings:
• ExaSearch: 0.80 threshold, enabled
• CryptoPrice: 0.90 threshold, enabled
• CurrencyConverter: 0.85 threshold, enabled
• CodeExecution: 0.95 threshold, enabled
• Memory: 0.70 threshold, enabled

Advanced Settings:
• Cooldown Period: 60s
• Repetition Penalty: 0.15
• Learn User Preferences: True
```

### **Adjust Global Settings**

```
/auto_tool_sensitivity action:set_global setting:confidence_threshold value:0.9
```

**Available Global Settings:**

- `enabled` (true/false)
- `confidence_threshold` (0.0-1.0)
- `min_message_length` (integer)
- `max_message_length` (integer, 0 = no limit)
- `require_explicit_keywords` (true/false)
- `fuzzy_matching` (true/false)

### **Adjust Tool-Specific Settings**

```
/auto_tool_sensitivity action:set_tool tool_name:ExaSearch setting:confidence_threshold value:0.9
```

**Available Tool Settings:**

- `enabled` (true/false)
- `confidence_threshold` (0.0-1.0)
- `require_both_keywords` (CryptoPrice only)
- `require_conversion_format` (CurrencyConverter only)
- `require_explicit_calc` (CodeExecution only)
- `require_explicit_memory` (Memory only)
- `require_sports_context` (ExaSearch only)
- `min_weak_keywords` (ExaSearch only)

### **Reset User Preferences**

```
/auto_tool_sensitivity action:reset_user
```

Resets the current user's tool usage history and preferences.

### **Reset All User Preferences**

```
/auto_tool_sensitivity action:reset_all
```

Resets all users' tool usage history and preferences.

## 🎛️ Sensitivity Adjustment Examples

### **Make Detection More Conservative (Less Sensitive)**

```bash
# Increase global confidence threshold
/auto_tool_sensitivity action:set_global setting:confidence_threshold value:0.9

# Make ExaSearch less sensitive
/auto_tool_sensitivity action:set_tool tool_name:ExaSearch setting:confidence_threshold value:0.9

# Require explicit keywords
/auto_tool_sensitivity action:set_global setting:require_explicit_keywords value:true
```

### **Make Detection More Sensitive**

```bash
# Decrease global confidence threshold
/auto_tool_sensitivity action:set_global setting:confidence_threshold value:0.6

# Make CryptoPrice more sensitive
/auto_tool_sensitivity action:set_tool tool_name:CryptoPrice setting:confidence_threshold value:0.7

# Allow fuzzy matching
/auto_tool_sensitivity action:set_global setting:fuzzy_matching value:true
```

### **Disable Specific Tools**

```bash
# Disable ExaSearch auto-detection
/auto_tool_sensitivity action:set_tool tool_name:ExaSearch setting:enabled value:false

# Disable all auto-detection
/auto_tool_sensitivity action:set_global setting:enabled value:false
```

## 🔍 Understanding Confidence Scores

The confidence score (0.0-1.0) represents how certain the system is that a tool is needed:

- **0.0-0.3**: Very low confidence - tool won't activate
- **0.3-0.6**: Low confidence - tool activates only with low thresholds
- **0.6-0.8**: Medium confidence - typical activation range
- **0.8-0.9**: High confidence - conservative activation
- **0.9-1.0**: Very high confidence - very conservative activation

### **How Confidence is Calculated**

#### **ExaSearch Example:**

- Strong keyword match: +0.8 confidence
- Weak keyword matches: +0.3 per match (requires minimum)
- Sports context: +0.4 (if context-aware enabled)

#### **CryptoPrice Example:**

- Price keyword + crypto token: 0.9 confidence
- Only price keyword: 0.0 confidence (if require_both_keywords enabled)

## ⚙️ Configuration File

The sensitivity settings are stored in `data/auto_tool_config.yaml` and can be edited directly:

```yaml
global:
  enabled: true
  confidence_threshold: 0.8
  min_message_length: 3
  require_explicit_keywords: true

tools:
  ExaSearch:
    enabled: true
    confidence_threshold: 0.8
    strong_keywords: ["search for", "find information about"]
    weak_keywords: ["latest", "news", "current"]
    min_weak_keywords: 2
    require_sports_context: true

  CryptoPrice:
    enabled: true
    confidence_threshold: 0.9
    require_both_keywords: true

advanced:
  cooldown_period: 60
  repetition_penalty: 0.15
  learn_user_preferences: true
```

## 🚀 Best Practices

### **For Active Communities**

- Use lower confidence thresholds (0.6-0.7)
- Enable fuzzy matching
- Reduce cooldown periods (30-45 seconds)

### **For Professional/Work Environments**

- Use higher confidence thresholds (0.8-0.9)
- Require explicit keywords
- Increase cooldown periods (90-120 seconds)

### **For Mixed Use Cases**

- Use medium confidence thresholds (0.7-0.8)
- Enable user preference learning
- Monitor usage patterns and adjust accordingly

## 🔧 Troubleshooting

### **Tools Not Activating**

1. Check if auto-detection is enabled: `/auto_tool_sensitivity action:view`
2. Lower confidence thresholds for specific tools
3. Check if explicit keywords are required
4. Verify tool-specific settings

### **Tools Activating Too Often**

1. Increase confidence thresholds
2. Enable explicit keyword requirements
3. Increase cooldown periods
4. Enable repetition penalties

### **Reset to Defaults**

```bash
# Reset all settings to defaults
/auto_tool_sensitivity action:reset_all
```

## 📊 Monitoring

Use the view command regularly to monitor your settings:

```bash
/auto_tool_sensitivity action:view
```

The system will log sensitivity adjustments and tool activations for debugging purposes.

---

**Note**: Only administrators can adjust auto-tool sensitivity settings. Regular users will still benefit from the optimized detection without needing to manage the settings.
