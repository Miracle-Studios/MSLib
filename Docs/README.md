<img src="https://i.ibb.co/PvN5Q0Zt/MS-TEAM-1.png" align="left">

# MSLib Documentation

**Version:** 1.2.0-beta  
**Last Updated:** December 8, 2025

Welcome to the **MSLib** documentation! MSLib is a powerful utility library for exteraGram plugin development that provides a comprehensive set of tools for building feature-rich Telegram plugins.

## 🆕 What's New in v1.2.0

- ✨ **Enhanced MSPlugin** - New helper methods for async operations, formatting, and clipboard
- 🗂️ **FileSystem utilities** - Convenient file operations with auto-path resolution
- 📦 **Data compression** - Built-in compress/decompress with base64 encoding
- 🔧 **Extended Requests API** - Edit messages, forward, get full user/chat info
- 📝 **Improved Markdown parser** - Support for all Telegram formatting options
- 🎯 **Inline handler decorator** - Simplified inline button handling
- 🔄 **Enhanced JsonDB** - New `pop()` and `update_from()` methods
- ⚡ **Better callbacks** - Added Callback3 for three-argument callbacks

**Migrating from v1.1.0?** See the [Migration Guide](migration-v1.2.0.md) →

## 📚 Table of Contents

- [Getting Started](getting-started.md)
- [MSPlugin Enhanced Features](msplugin-enhanced.md) ⭐ NEW
- [AutoUpdater](autoupdater.md)
- [Cache & Storage](cache-storage.md)
- [Commands System](commands.md)
- [Logging & Notifications](logging-notifications.md)
- [Requests API](requests.md)
- [UI Components](ui-components.md)
- [Parsers](parsers.md)
- [Utilities](utilities.md)
- [Integrated Plugins](integrated-plugins.md)
- [API Reference](api-reference.md)

## 🚀 Quick Start

```python
from base_plugin import BasePlugin
from MSLib import (
    AutoUpdater, 
    add_autoupdater_task,
    BulletinHelper,
    command,
    JsonDB
)

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Enable auto-updates
        add_autoupdater_task(
            plugin_id="my_plugin",
            channel_id=-1001234567890,
            message_id=123
        )
        
        # Show notification
        BulletinHelper.show_success("Plugin loaded!")
        
        # Use database
        self.db = JsonDB("my_plugin.json")
        self.db.set("initialized", True)
    
    @command("hello")
    def hello_cmd(self, param, account):
        BulletinHelper.show_info("Hello, World!")
        return HookResult()
```

## 🎯 Key Features

### ⚡ AutoUpdater
Automatic plugin updates from Telegram channels with smart polling and self-update capability.

### 💾 Storage Solutions
- **JsonDB**: Key-value database
- **JsonCacheFile**: Compressed JSON cache
- **CacheFile**: Binary file caching

### 🎮 Command System
Powerful command routing with type validation, decorators, and custom prefix support.

### 📢 Notifications
Rich bulletin system with copy buttons, post redirects, and custom styling.

### 🌐 Telegram API
Simplified wrappers for common Telegram operations: messages, users, chats, moderation.

### 🎨 UI Components
Ready-to-use dialogs, spinners, and settings builders.

### 🔧 Utilities
170+ helper functions for common tasks: logging, parsing, file operations, and more.

## 📖 Version

Current version: **1.1.0-beta**

## 🔗 Links

- [GitHub Repository](https://github.com/Miracle-Studios/MS-Plugins/)
- [Telegram Channel](https://t.me/MiracleStudios)
- [Author](https://t.me/Imrcle)

## 📝 License

Please do not copy this code without notifying the author.

---

**Happy coding! 🚀**
