# Logging & Notifications

MSLib provides comprehensive logging and notification systems for informing users and debugging plugins.

## 📖 Overview

Two main systems:

- **Logger**: Debug logging to logcat
- **BulletinHelper**: User-facing notifications

## 📝 Logging

### Quick Start

```python
from MSLib import logger

logger.info("Plugin started")
logger.debug("Debug information")
logger.warning("Something suspicious")
logger.error("An error occurred")
```

### API Reference

#### `build_log(tag, level=logging.INFO)`

Creates a custom logger.

```python
from MSLib import build_log
import logging

my_logger = build_log("MyPlugin", level=logging.DEBUG)
my_logger.info("Custom logger")
```

#### `logger`

Global MSLib logger instance.

**Methods:**
- `logger.debug(msg)` - Debug messages
- `logger.info(msg)` - Informational messages  
- `logger.warning(msg)` - Warning messages
- `logger.error(msg)` - Error messages

### Usage Examples

#### Example 1: Basic Logging

```python
from MSLib import logger

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        logger.info("Plugin loaded successfully")
        logger.debug(f"Settings: {self.get_all_settings()}")
    
    def process_data(self, data):
        logger.debug(f"Processing data: {data}")
        
        try:
            result = self.complex_operation(data)
            logger.info(f"Operation successful: {result}")
            return result
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            logger.debug(f"Full error: {format_exc()}")
            return None
```

#### Example 2: Debug Mode

```python
from MSLib import logger
import logging

class DebuggablePlugin(BasePlugin):
    def on_plugin_load(self):
        # Enable debug mode from settings
        if self.get_setting("debug_mode", False):
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        else:
            logger.setLevel(logging.INFO)
    
    def detailed_operation(self):
        logger.debug("Step 1: Initialize")
        # ...
        logger.debug("Step 2: Process")
        # ...
        logger.debug("Step 3: Finalize")
        logger.info("Operation complete")
```

#### Example 3: Custom Logger

```python
from MSLib import build_log
import logging

class MultiLoggerPlugin(BasePlugin):
    def on_plugin_load(self):
        # Separate loggers for different components
        self.api_logger = build_log("MyPlugin.API", logging.DEBUG)
        self.db_logger = build_log("MyPlugin.DB", logging.INFO)
        self.ui_logger = build_log("MyPlugin.UI", logging.WARNING)
    
    def api_call(self):
        self.api_logger.debug("Making API request")
        # ...
        self.api_logger.info("API response received")
    
    def database_query(self):
        self.db_logger.info("Executing query")
        # ...
```

### `get_logs()`

Retrieve logcat logs.

**Signature:**

```python
get_logs(
    __id__: Optional[str] = None,
    times: Optional[int] = None,
    lvl: Optional[str] = None,
    as_list: bool = False
) -> Union[List[str], str]
```

**Parameters:**
- `__id__`: Filter by plugin ID
- `times`: Time range in seconds  
- `lvl`: Log level (DEBUG, INFO, WARN, ERROR)
- `as_list`: Return as list instead of string

**Examples:**

```python
from MSLib import get_logs

# Get all logs
all_logs = get_logs()

# Get plugin-specific logs
my_logs = get_logs(__id__="my_plugin")

# Get recent logs (last 60 seconds)
recent = get_logs(times=60)

# Get errors only
errors = get_logs(lvl="ERROR")

# Get as list
log_lines = get_logs(__id__="my_plugin", as_list=True)
for line in log_lines:
    print(line)
```

## 📢 Notifications

### BulletinHelper

User-facing notifications.

### API Reference

#### Basic Notifications

##### `show_info(message, fragment=None)`

```python
from MSLib import BulletinHelper

BulletinHelper.show_info("Information message")
```

##### `show_success(message, fragment=None)`

```python
BulletinHelper.show_success("Operation completed!")
```

##### `show_error(message, fragment=None)`

```python
BulletinHelper.show_error("Something went wrong")
```

#### Notifications with Copy Button

##### `show_info_with_copy(message, copy_text)`

```python
BulletinHelper.show_info_with_copy(
    "Error details",
    "Full error trace here"
)
```

##### `show_success_with_copy(message, copy_text)`

```python
BulletinHelper.show_success_with_copy(
    "API Key generated",
    "sk-1234567890abcdef"
)
```

##### `show_error_with_copy(message, copy_text)`

```python
BulletinHelper.show_error_with_copy(
    "Exception occurred",
    str(exception)
)
```

#### Notifications with Post Redirect

##### `show_info_with_post_redirect(message, button_text, peer_id, message_id)`

```python
BulletinHelper.show_info_with_post_redirect(
    "New message in channel",
    "Open",
    peer_id=-1001234567890,
    message_id=123
)
```

##### `show_success_with_post_redirect(message, button_text, peer_id, message_id)`

```python
BulletinHelper.show_success_with_post_redirect(
    "Post created",
    "View Post",
    peer_id=-1001234567890,
    message_id=456
)
```

##### `show_error_with_post_redirect(message, button_text, peer_id, message_id)`

```python
BulletinHelper.show_error_with_post_redirect(
    "Failed to send",
    "Retry",
    peer_id=-1001234567890,
    message_id=789
)
```

### InnerBulletinHelper

Bulletin with custom prefix.

```python
from MSLib import InnerBulletinHelper

# Create prefixed helper
helper = InnerBulletinHelper("MyPlugin")

helper.show_info("Info message")
# Shows: "MyPlugin: Info message"

helper.show_error("Error occurred")
# Shows: "MyPlugin: Error occurred"
```

### Usage Examples

#### Example 1: Command Feedback

```python
from MSLib import command, BulletinHelper
from base_plugin import HookResult

class FeedbackPlugin(BasePlugin):
    @command("save")
    def save_cmd(self, param, account, data: str):
        """Save data"""
        try:
            # Save logic
            self.db.set("data", data)
            BulletinHelper.show_success("Data saved successfully!")
        except Exception as e:
            BulletinHelper.show_error(f"Failed to save: {e}")
        
        return HookResult()
```

#### Example 2: Progress Notifications

```python
from MSLib import BulletinHelper
import time

class ProcessorPlugin(BasePlugin):
    def process_batch(self, items):
        BulletinHelper.show_info(f"Processing {len(items)} items...")
        
        for i, item in enumerate(items):
            self.process_item(item)
            
            # Progress update
            if (i + 1) % 10 == 0:
                BulletinHelper.show_info(f"Processed {i + 1}/{len(items)}")
        
        BulletinHelper.show_success("Batch processing complete!")
```

#### Example 3: Error with Details

```python
from MSLib import BulletinHelper, logger, format_exc

class ErrorHandlingPlugin(BasePlugin):
    def risky_operation(self):
        try:
            # Some risky code
            result = 10 / 0
        except Exception as e:
            error_trace = format_exc()
            logger.error(f"Operation failed: {error_trace}")
            
            BulletinHelper.show_error_with_copy(
                "Operation failed. Tap to copy error details.",
                error_trace
            )
```

#### Example 4: API Key Display

```python
from MSLib import BulletinHelper

class APIPlugin(BasePlugin):
    @command("getkey")
    def get_api_key(self, param, account):
        """Generate API key"""
        key = self.generate_key()
        
        BulletinHelper.show_success_with_copy(
            "Your API key (tap to copy):",
            key
        )
        
        return HookResult()
    
    def generate_key(self):
        import secrets
        return secrets.token_hex(32)
```

#### Example 5: Channel Notifications

```python
from MSLib import BulletinHelper

class ChannelMonitor(BasePlugin):
    def on_new_post(self, channel_id, message_id):
        BulletinHelper.show_info_with_post_redirect(
            "New post in monitored channel!",
            "Open Post",
            peer_id=channel_id,
            message_id=message_id
        )
```

#### Example 6: Custom Prefix Helper

```python
from MSLib import InnerBulletinHelper

class PrefixedPlugin(BasePlugin):
    def on_plugin_load(self):
        self.bulletin = InnerBulletinHelper("MyPlugin")
    
    def notify_user(self, message_type, message):
        if message_type == "info":
            self.bulletin.show_info(message)
        elif message_type == "success":
            self.bulletin.show_success(message)
        elif message_type == "error":
            self.bulletin.show_error(message)
```

## 🎯 Comparison

| Feature | Logger | BulletinHelper |
|---------|--------|----------------|
| **Purpose** | Debugging | User notifications |
| **Visibility** | Logcat only | On-screen popup |
| **Persistence** | Logged to file | Temporary display |
| **Best For** | Development | Production |
| **User-facing** | No | Yes |

## 💡 Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug("Variable value: {value}")  # Development only
logger.info("User action completed")      # General info
logger.warning("Unusual condition")       # Potential issues
logger.error("Operation failed")          # Errors

# ❌ Bad
logger.error("Button clicked")  # Not an error
logger.debug("Critical failure") # Should be error
```

### 2. Log Before Exceptions

```python
# ✅ Good
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    BulletinHelper.show_error("Operation failed")

# ❌ Bad
try:
    result = risky_operation()
except:
    pass  # Silent failure - bad!
```

### 3. Don't Spam Notifications

```python
# ✅ Good
processed = 0
for item in items:
    process(item)
    processed += 1

BulletinHelper.show_success(f"Processed {processed} items")

# ❌ Bad
for item in items:
    process(item)
    BulletinHelper.show_info("Item processed")  # Too many!
```

### 4. Provide Actionable Errors

```python
# ✅ Good
BulletinHelper.show_error("Failed to connect. Check your internet connection.")

# ❌ Bad  
BulletinHelper.show_error("Error 500")  # Not helpful
```

### 5. Use Copy for Long Text

```python
# ✅ Good
BulletinHelper.show_error_with_copy(
    "Error occurred. Tap to copy details.",
    long_error_message
)

# ❌ Bad
BulletinHelper.show_error(long_error_message)  # Too long for popup
```

## 🐛 Troubleshooting

### Logs Not Appearing

```python
# Enable debug level
from MSLib import logger
import logging

logger.setLevel(logging.DEBUG)
logger.debug("This should appear now")
```

### Bulletin Not Showing

```python
# Check if on UI thread
from android_utils import run_on_ui_thread

@run_on_ui_thread
def show_notification():
    BulletinHelper.show_info("Now it works!")

show_notification()
```

### Too Many Notifications

```python
# Debounce notifications
import time

class Plugin(BasePlugin):
    def __init__(self):
        self.last_notification = 0
    
    def notify(self, message):
        now = time.time()
        if now - self.last_notification > 1:  # Max 1 per second
            BulletinHelper.show_info(message)
            self.last_notification = now
```

---

**Next:** [Requests API →](requests.md)
