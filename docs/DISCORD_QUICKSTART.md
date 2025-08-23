# Discord Quickstart Guide

## Basic Commands

- `/help` - Show all available commands
- `/feature <tool>` - Enable specific tools (ImageGen, ExaSearch, etc.)
- `/quickstart` - Display this guide

## 🛠️ Core Features

### **AI Chat & Memory**

- **Default Tool**: Memory (personalized conversations)
- **Tool Switching**: Use `/feature <tool>` to access specialized tools
- **Auto-Return**: Tools automatically return to Memory after timeout

### **🔄 One Tool at a Time System**

**Important**: JakeyBot can only use **one tool at a time**. This ensures optimal performance and prevents conflicts.

- **Current Tool**: Only one tool is active at any moment
- **Tool Switching**: Use `/feature <tool>` to switch between tools
- **Auto-Return**: After a timeout, tools automatically return to Memory
- **Smart Management**: The system intelligently manages tool transitions

### **Smart Tool Management**

- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Timeout Control**:
  - `/timeout_status` - Check remaining time
  - `/extend_timeout <time>` - Add more time (e.g., `5m`, `2h`)
  - `/return_to_default` - Switch back to Memory immediately
- **System Status**: `/auto_return_status` for overview

### **Popular Tools**

- **ImageGen**: Generate and edit images
- **ExaSearch**: Web search and research
- **GitHub**: Repository analysis
- **CodeExecution**: Run Python code
- **AudioTools**: Audio manipulation and generation
- **YouTube**: Video summarization

## ⚡ Quick Workflows

### **Image Generation**

```
/feature ImageGen
generate a cute cat playing with yarn
```

*Auto-returns to Memory in 5 minutes*

### **Web Research**

```
/feature ExaSearch
search for latest AI developments 2025
```

*Auto-returns to Memory in 3 minutes*

### **Code Execution**

```
/feature CodeExecution
run this python code: print("Hello World")
```

*Auto-returns to Memory in 10 minutes*

## 🧠 Smart Features

### **Personal Reminders**

```
/remindme 2h check the crypto prices
/remindme tomorrow 9am team meeting
```

### **Time & Date**

- `/time` - Current time and DST status
- `/date` - Current date and timezone

### **Memory Management**

- `/memory_debug` - Troubleshoot memory issues
- `/memory_reindex` - Optimize memory performance

## 🔧 Advanced Usage

### **Tool Optimization**

- Use `/smart_suggestions` for personalized tips
- Extend sessions before timeouts
- Plan workflows to maximize tool usage

### **Customization**

- Tools auto-return to Memory (configurable default)
- Timeout durations optimized per tool type
- Activity-based intelligent suggestions

## 🆘 Need Help?

- **Commands**: `/help` for full command list
- **Quick Reference**: `/quickstart` for this guide
- **Smart Tips**: `/smart_suggestions` for optimization advice
- **System Status**: `/auto_return_status` for tool management overview

## 💡 Pro Tips

1. **Use Memory First**: Start with Memory tool for personalized conversations
2. **Switch Tools Strategically**: Enable specialized tools only when needed
3. **Extend Timeouts**: Use `/extend_timeout` for longer sessions
4. **Get Smart Tips**: Use `/smart_suggestions` for workflow optimization
5. **Monitor Time**: Check `/timeout_status` to plan your work
6. **Plan Your Workflow**: Since only one tool works at a time, plan your tool usage sequence

---

**🎯 That's it! Remember: one tool at a time for optimal performance!**
