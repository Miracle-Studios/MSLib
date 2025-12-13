# AutoUpdater

The AutoUpdater system automatically checks for plugin updates from Telegram channels and installs them without user intervention.

## 📖 Overview

MSLib's AutoUpdater:
- ✅ Monitors Telegram channels for plugin updates
- ✅ Downloads and installs updates automatically
- ✅ Supports multiple plugins simultaneously
- ✅ Configurable check intervals
- ✅ Manual force update checks
- ✅ Self-updating capability for MSLib itself

## 🚀 Quick Start

### Basic Setup

```python
from base_plugin import BasePlugin
from MSLib import add_autoupdater_task

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Register for auto-updates
        add_autoupdater_task(
            plugin_id="my_plugin",
            channel_id=-1001234567890,  # Your channel ID (negative for channels)
            message_id=123               # Message ID with .plugin file
        )
```

That's it! Your plugin will now check for updates automatically.

## 📚 API Reference

### Functions

#### `add_autoupdater_task(plugin_id, channel_id, message_id)`

Registers a plugin for automatic updates.

**Parameters:**
- `plugin_id` (str): Your plugin's ID (same as `__id__`)
- `channel_id` (int): Telegram channel ID (negative number)
- `message_id` (int): Message ID containing the .plugin file

**Example:**

```python
from MSLib import add_autoupdater_task

def on_plugin_load(self):
    add_autoupdater_task(
        plugin_id="awesome_plugin",
        channel_id=-1001234567890,
        message_id=456
    )
```

#### `remove_autoupdater_task(plugin_id)`

Removes a plugin from auto-update monitoring.

**Parameters:**
- `plugin_id` (str): Plugin ID to remove

**Example:**

```python
from MSLib import remove_autoupdater_task

def on_plugin_unload(self):
    remove_autoupdater_task("awesome_plugin")
```

### Classes

#### `AutoUpdater`

Main auto-update engine. Usually managed automatically by MSLib.

**Methods:**

##### `run()`

Starts the update checker thread.

```python
from MSLib import autoupdater

if autoupdater:
    autoupdater.run()
```

##### `force_stop()`

Stops the update checker thread.

```python
from MSLib import autoupdater

if autoupdater:
    autoupdater.force_stop()
```

##### `force_update_check()`

Triggers an immediate update check.

```python
from MSLib import autoupdater

if autoupdater:
    autoupdater.force_update_check()
```

##### `add_task(task)`

Adds an update task.

```python
from MSLib import UpdaterTask, autoupdater

task = UpdaterTask(
    plugin_id="my_plugin",
    channel_id=-1001234567890,
    message_id=123
)

if autoupdater:
    autoupdater.add_task(task)
```

##### `remove_task(task)` / `remove_task_by_id(plugin_id)`

Removes an update task.

```python
from MSLib import autoupdater

if autoupdater:
    autoupdater.remove_task_by_id("my_plugin")
```

#### `UpdaterTask`

Represents an auto-update task.

**Constructor:**

```python
from MSLib import UpdaterTask

task = UpdaterTask(
    plugin_id="my_plugin",
    channel_id=-1001234567890,
    message_id=123
)
```

**Attributes:**
- `plugin_id` (str): Plugin identifier
- `channel_id` (int): Telegram channel ID
- `message_id` (int): Message ID with plugin file

## 🎯 Usage Examples

### Example 1: Basic Auto-Update

```python
from base_plugin import BasePlugin
from MSLib import add_autoupdater_task, BulletinHelper

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Enable auto-updates
        add_autoupdater_task(
            plugin_id="my_plugin",
            channel_id=-1001234567890,
            message_id=100
        )
        
        BulletinHelper.show_success("Auto-updates enabled!")
```

### Example 2: Manual Update Check

```python
from base_plugin import BasePlugin, HookResult
from MSLib import command, autoupdater, BulletinHelper

class MyPlugin(BasePlugin):
    @command("update")
    def check_updates(self, param, account):
        """Manually check for updates"""
        if autoupdater and autoupdater.thread and autoupdater.thread.is_alive():
            autoupdater.force_update_check()
            BulletinHelper.show_success("Checking for updates...")
        else:
            BulletinHelper.show_error("AutoUpdater is not running")
        
        return HookResult()
```

### Example 3: Conditional Auto-Update

```python
from base_plugin import BasePlugin
from MSLib import add_autoupdater_task, remove_autoupdater_task

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Only enable auto-updates if user opted in
        if self.get_setting("enable_autoupdate", False):
            add_autoupdater_task(
                plugin_id="my_plugin",
                channel_id=-1001234567890,
                message_id=123
            )
    
    def on_setting_changed(self, key, value):
        if key == "enable_autoupdate":
            if value:
                add_autoupdater_task(
                    plugin_id="my_plugin",
                    channel_id=-1001234567890,
                    message_id=123
                )
            else:
                remove_autoupdater_task("my_plugin")
```

### Example 4: Multiple Plugin Updates

```python
from base_plugin import BasePlugin
from MSLib import add_autoupdater_task

class PluginManager(BasePlugin):
    PLUGINS = [
        ("plugin1", -1001111111111, 10),
        ("plugin2", -1001111111111, 20),
        ("plugin3", -1001111111111, 30),
    ]
    
    def on_plugin_load(self):
        # Register all plugins for updates
        for plugin_id, channel_id, message_id in self.PLUGINS:
            add_autoupdater_task(plugin_id, channel_id, message_id)
```

### Example 5: Update Notification Handler

```python
from base_plugin import BasePlugin
from MSLib import BulletinHelper, logger

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        add_autoupdater_task("my_plugin", -1001234567890, 123)
        
        # Log when updates are checked
        logger.info("Auto-update monitoring started")
    
    def on_plugin_unload(self):
        remove_autoupdater_task("my_plugin")
        logger.info("Auto-update monitoring stopped")
```

## ⚙️ Configuration

### MSLib Settings

AutoUpdater can be configured via MSLib settings:

1. **Enable AutoUpdater**: Toggle auto-update system on/off
2. **Update Interval**: Time between checks (default: 600 seconds)
3. **Disable Timestamp Check**: Update even if file hasn't changed
4. **Force Update Check**: Manual trigger button

### Programmatic Configuration

```python
from MSLib import MSLib_instance

# Get current timeout
timeout = MSLib_instance.get_setting("autoupdate_timeout", "600")

# Disable timestamp checking
MSLib_instance.save_setting("disable_timestamp_check", True)
```

## 🔍 How It Works

1. **Registration**: Plugin calls `add_autoupdater_task()`
2. **Monitoring**: AutoUpdater checks channel message periodically
3. **Detection**: Compares message edit timestamp
4. **Download**: Downloads .plugin file via FileLoader
5. **Installation**: Installs via PluginsController
6. **Notification**: Shows success/error bulletin

### Update Flow

```
┌─────────────────┐
│ Plugin Loads    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Register Task   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Wait (Timeout)  │◄──────┐
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ Check Message   │       │
└────────┬────────┘       │
         │                │
         ▼                │
    ┌────────┐            │
    │Updated?│────No──────┘
    └───┬────┘
        │Yes
        ▼
┌─────────────────┐
│ Download File   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Install Plugin  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Show Bulletin   │
└─────────────────┘
```

## 📝 Channel Setup

### Step 1: Create Update Channel

1. Create a Telegram channel
2. Make it public or private
3. Post your .plugin file as a document

### Step 2: Get Channel & Message IDs

```python
# Channel ID example: -1001234567890
# Message ID example: 123

# For public channels, you can use username
channel_id = -1001234567890

# Get message ID by right-clicking message → "Copy Message Link"
# Link format: https://t.me/c/1234567890/123
#                                    ↑        ↑
#                              channel_id  msg_id
```

### Step 3: Post Updates

1. Edit the message with new .plugin file
2. AutoUpdater detects the edit timestamp change
3. Downloads and installs automatically

**Important:** The message edit date is used for update detection, so editing the message triggers an update.

## 🎛️ Advanced Usage

### Custom Download Handler

```python
from MSLib import download_and_install_plugin

def custom_update_handler(msg, plugin_id):
    """Custom update logic"""
    download_and_install_plugin(
        msg=msg,
        plugin_id=plugin_id,
        max_tries=5  # Reduce retry attempts
    )
```

### Update Status Monitoring

```python
from MSLib import autoupdater, logger

def check_update_status():
    """Check AutoUpdater status"""
    if not autoupdater:
        logger.warning("AutoUpdater not initialized")
        return False
    
    if not autoupdater.thread:
        logger.warning("AutoUpdater thread not created")
        return False
    
    if not autoupdater.thread.is_alive():
        logger.warning("AutoUpdater thread not running")
        return False
    
    logger.info(f"AutoUpdater active with {len(autoupdater.tasks)} tasks")
    return True
```

### Retry Logic

The AutoUpdater automatically retries failed downloads up to 10 times with 1-second delays:

```python
# Built-in retry logic (automatic)
download_and_install_plugin(
    msg=message,
    plugin_id="my_plugin",
    max_tries=10,  # Max retry attempts
    is_queued=False,
    current_try=0
)
```

## ⚠️ Important Notes

1. **Channel ID Format**: Always use negative numbers for channels
2. **Message Edit**: Updates trigger on message edit date change
3. **File Type**: Message must contain a .plugin document
4. **Thread Safety**: AutoUpdater runs in a separate thread
5. **MSLib Dependency**: Your plugin needs MSLib installed
6. **Permissions**: Channel must be accessible by user

## 🐛 Troubleshooting

### Updates Not Working

```python
# Check if AutoUpdater is running
from MSLib import autoupdater, logger

if not autoupdater:
    logger.error("AutoUpdater not initialized - enable in MSLib settings")
elif not autoupdater.thread or not autoupdater.thread.is_alive():
    logger.error("AutoUpdater thread not running")
    autoupdater.run()  # Start it
else:
    logger.info("AutoUpdater is running normally")
```

### Force Update

```python
# Trigger immediate check
from MSLib import autoupdater, BulletinHelper

if autoupdater and autoupdater.thread and autoupdater.thread.is_alive():
    autoupdater.force_update_check()
    BulletinHelper.show_info("Update check triggered!")
```

### Debug Mode

```python
# Enable debug logging
from MSLib import logger
import logging

logger.setLevel(logging.DEBUG)
logger.debug("AutoUpdater debug mode enabled")
```

## 💡 Best Practices

1. ✅ Always check if `autoupdater` exists before using
2. ✅ Use proper error handling for network issues
3. ✅ Register tasks in `on_plugin_load()`
4. ✅ Unregister tasks in `on_plugin_unload()`
5. ✅ Keep update channel organized
6. ✅ Test updates in private channel first
7. ✅ Include version info in plugin file

---

**Next:** [Cache & Storage →](cache-storage.md)
