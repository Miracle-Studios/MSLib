# Getting Started with MSLib

This guide will help you start using MSLib in your exteraGram plugins.

## 📦 Installation

MSLib is distributed as a plugin file (`MSLib.plugin`). Install it like any other exteraGram plugin:

1. Download `MSLib.plugin`
2. Open exteraGram
3. Go to Settings → Plugins
4. Install the plugin file
5. Enable MSLib

## 📥 Importing MSLib

### Basic Import

```python
from MSLib import (
    # Core classes
    MSLib,
    MSPlugin,
    
    # AutoUpdater
    AutoUpdater,
    add_autoupdater_task,
    
    # Storage
    JsonDB,
    JsonCacheFile,
    
    # Notifications
    BulletinHelper,
    
    # Commands
    command,
    Dispatcher,
    
    # Utilities
    logger,
    localise
)
```

### Import Everything

```python
from MSLib import *
```

⚠️ **Note**: While `import *` is supported, it's recommended to import only what you need for better code clarity.

## 🏗️ Plugin Structure

### Method 1: Using MSPlugin Mixin

The easiest way to use MSLib is to inherit from `MSPlugin`:

```python
from base_plugin import BasePlugin, HookResult
from MSLib import MSPlugin, command, BulletinHelper

class MyPlugin(MSPlugin, BasePlugin):
    """My awesome plugin with MSLib support"""
    
    strings = {
        "en": {
            "plugin_loaded": "Plugin loaded successfully!",
            "hello": "Hello, {name}!"
        },
        "ru": {
            "plugin_loaded": "Плагин загружен успешно!",
            "hello": "Привет, {name}!"
        }
    }
    
    def on_plugin_load(self):
        # MSPlugin automatically initializes logger and database
        super().on_plugin_load()
        
        # Use localized strings
        BulletinHelper.show_success(self.string("plugin_loaded"))
        
        # Use database
        self.set_db("load_count", self.get_db("load_count", 0) + 1)
        self.plugin_info(f"Plugin loaded {self.get_db('load_count')} times")
    
    @command("hello")
    def hello_command(self, param, account):
        """Say hello to the user"""
        name = param.args[0] if param.args else "World"
        BulletinHelper.show_info(self.string("hello", name=name))
        return HookResult()
```

**MSPlugin provides:**
- `self.db` - JsonDB instance
- `self.logger` - Configured logger
- `self.string(key, **kwargs)` - Localization
- `self.get_db(key, default)` - Get database value
- `self.set_db(key, value)` - Set database value
- `self.plugin_log()`, `self.plugin_info()`, `self.plugin_debug()`, etc.

### Method 2: Manual Setup

If you prefer manual control:

```python
from base_plugin import BasePlugin, HookResult
from MSLib import (
    JsonDB,
    build_log,
    BulletinHelper,
    command,
    Dispatcher,
    CACHE_DIRECTORY
)
import os

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.logger = build_log("MyPlugin")
        self.db_path = os.path.join(CACHE_DIRECTORY, "myplugin.json")
        self.db = JsonDB(self.db_path)
        self.dispatcher = Dispatcher("myplugin", prefix=".")
    
    def on_plugin_load(self):
        self.logger.info("Plugin loaded")
        BulletinHelper.show_success("Plugin loaded!")
        
        # Register commands manually
        @self.dispatcher.register_command("test")
        def test_cmd(param, account):
            BulletinHelper.show_info("Test command executed!")
            return HookResult()
```

## 🎯 Common Patterns

### 1. Auto-Updates

```python
from MSLib import add_autoupdater_task

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Register for auto-updates
        add_autoupdater_task(
            plugin_id="my_plugin",
            channel_id=-1001234567890,  # Your channel ID
            message_id=123               # Message with .plugin file
        )
```

### 2. Settings UI

```python
from MSLib import localise
from ui.settings import Header, Switch, Input, Divider

class MyPlugin(BasePlugin):
    def create_settings(self):
        def on_toggle(value):
            BulletinHelper.show_success(f"Feature {'enabled' if value else 'disabled'}")
        
        return [
            Header(text="My Plugin Settings"),
            Switch(
                key="enable_feature",
                text="Enable Feature",
                subtext="Enables the awesome feature",
                default=False,
                icon="msg_smile",
                on_change=on_toggle
            ),
            Input(
                key="api_key",
                text="API Key",
                subtext="Your secret API key",
                default="",
                icon="msg_key"
            ),
            Divider()
        ]
```

### 3. Notifications

```python
from MSLib import BulletinHelper

# Simple notifications
BulletinHelper.show_info("Information message")
BulletinHelper.show_success("Operation successful!")
BulletinHelper.show_error("Something went wrong")

# With copy button
BulletinHelper.show_info_with_copy("Error details", "Error trace here")

# With post redirect
BulletinHelper.show_info_with_post_redirect(
    "Check this message",
    "Open",
    peer_id=-1001234567890,
    message_id=123
)
```

### 4. Commands

```python
from MSLib import command
from base_plugin import HookResult

class MyPlugin(MSPlugin, BasePlugin):
    @command("greet")
    def greet_command(self, param, account):
        """Greet the user"""
        name = param.args[0] if param.args else "User"
        BulletinHelper.show_success(f"Hello, {name}!")
        return HookResult()
    
    @command("calc", aliases=["c"])
    def calculator(self, param, account, a: int, b: int):
        """Add two numbers: .calc 5 10"""
        result = a + b
        BulletinHelper.show_info(f"{a} + {b} = {result}")
        return HookResult()
```

### 5. Storage

```python
from MSLib import JsonDB, JsonCacheFile

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Simple key-value storage
        self.db = JsonDB("myplugin.json")
        self.db.set("user_count", 100)
        count = self.db.get("user_count", 0)
        
        # Cached data with compression
        self.cache = JsonCacheFile(
            filename="cache.json",
            default={"data": []},
            compress=True
        )
        self.cache.json_content["data"].append("new_item")
        self.cache.write()
```

## 🔍 Debugging

### Enable Debug Mode

```python
from MSLib import logger
import logging

# Enable debug logging
logger.setLevel(logging.DEBUG)

# Or use the setting in MSLib settings UI
```

### View Logs

```python
from MSLib import get_logs

# Get all logs
all_logs = get_logs()

# Get plugin-specific logs
my_logs = get_logs(__id__="my_plugin")

# Get recent logs (last 60 seconds)
recent = get_logs(times=60)

# Get error logs only
errors = get_logs(lvl="ERROR")
```

## 📋 Next Steps

- [AutoUpdater Guide](autoupdater.md) - Set up automatic updates
- [Commands System](commands.md) - Build powerful commands
- [Storage Guide](cache-storage.md) - Persist data
- [UI Components](ui-components.md) - Create beautiful interfaces
- [API Reference](api-reference.md) - Complete function reference

## 💡 Tips

1. **Always call `super().on_plugin_load()`** when using MSPlugin
2. **Use localization** with `self.string()` for multi-language support
3. **Handle errors gracefully** with try-except blocks
4. **Test on real devices** - emulator behavior may differ
5. **Check MSLib settings** for debug mode and other options

## ❓ Common Issues

### Import Error

```python
# ❌ Wrong
from MSLib import NonExistentFunction

# ✅ Correct - check __all__ exports
from MSLib import logger, BulletinHelper
```

### Database Path Issues

```python
# ❌ Wrong - relative path
db = JsonDB("data.json")

# ✅ Correct - use CACHE_DIRECTORY
from MSLib import CACHE_DIRECTORY
import os
db = JsonDB(os.path.join(CACHE_DIRECTORY, "data.json"))
```

### Command Not Working

```python
# ❌ Wrong - missing return
@command("test")
def test_cmd(self, param, account):
    BulletinHelper.show_info("Test")
    # Missing return!

# ✅ Correct
@command("test")
def test_cmd(self, param, account):
    BulletinHelper.show_info("Test")
    return HookResult()  # Always return HookResult
```

---

Ready to build amazing plugins? Continue to [AutoUpdater →](autoupdater.md)
