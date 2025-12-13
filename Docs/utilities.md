# Utilities

MSLib provides 180+ utility functions for common development tasks, from logging and debugging to Java interop and file operations.

## 📖 Overview

Utility categories:

- 📝 **Logging & Debugging** - build_log, format_exc, get_logs
- 🔤 **Text Processing** - escape_html, unescape_html, pluralization_string, link
- 📋 **Clipboard** - copy_to_clipboard
- 🔄 **Type Conversion** - arraylist_to_list, list_to_arraylist, cast_arg
- 🎨 **UI Helpers** - dp, sp, AndroidUtilities wrappers
- 🔧 **System** - runtime_exec, get_plugin
- 🌐 **Localization** - localise
- ⚡ **Async** - run_on_ui_thread, run_on_queue
- 📦 **Java Interop** - Java wrappers and callbacks
- 💾 **File System** - FileSystem class for file operations (NEW in v1.2.0)
- 🗜️ **Data Compression** - compress_and_encode, decode_and_decompress (NEW in v1.2.0)
- 📏 **Formatters** - format_size, format_duration (NEW in v1.2.0)

## 📚 API Reference

### Logging & Debugging

#### `build_log(tag, level=logging.INFO)`

Create a custom logger with tag.

**Parameters:**
- `tag` (str): Logger tag/name
- `level` (int): Log level (default: INFO)

**Returns:** logging.Logger instance

**Example:**

```python
from MSLib import build_log
import logging

# Create logger
logger = build_log("MyPlugin", logging.DEBUG)

# Use logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

**Full Example:**

```python
from MSLib import build_log, BulletinHelper
import logging

class DebugPlugin(BasePlugin):
    def on_plugin_load(self):
        # Create logger for this plugin
        self.logger = build_log("DebugPlugin", logging.DEBUG)
        self.logger.info("Plugin loaded")
    
    @command("debug")
    def toggle_debug(self, param, account):
        """Toggle debug mode"""
        current_level = self.logger.level
        
        if current_level == logging.DEBUG:
            self.logger.setLevel(logging.INFO)
            BulletinHelper.show_info("Debug mode: OFF")
        else:
            self.logger.setLevel(logging.DEBUG)
            BulletinHelper.show_info("Debug mode: ON")
        
        return HookResult()
    
    @command("test")
    def test_logging(self, param, account):
        """Test all log levels"""
        self.logger.debug("This is a debug message")
        self.logger.info("This is an info message")
        self.logger.warning("This is a warning")
        self.logger.error("This is an error")
        
        BulletinHelper.show_success("Check logs!")
        return HookResult()
```

#### `format_exc()`

Format current exception with full traceback.

**Returns:** Formatted exception string

**Example:**

```python
from MSLib import format_exc, logger

try:
    result = 10 / 0
except Exception:
    error_text = format_exc()
    logger.error(f"Exception occurred:\n{error_text}")
```

#### `format_exc_from(e)`

Format exception from exception object.

**Parameters:**
- `e` (Exception): Exception object

**Returns:** Formatted exception string

**Example:**

```python
from MSLib import format_exc_from, BulletinHelper

try:
    dangerous_operation()
except Exception as e:
    error_msg = format_exc_from(e)
    BulletinHelper.show_error(f"Error:\n{error_msg}")
```

#### `format_exc_only(e)`

Format exception message only (no traceback).

**Parameters:**
- `e` (Exception): Exception object

**Returns:** Exception message string

**Example:**

```python
from MSLib import format_exc_only, BulletinHelper

try:
    process_data()
except ValueError as e:
    msg = format_exc_only(e)
    BulletinHelper.show_error(msg)  # "ValueError: invalid data"
```

**Full Example:**

```python
from MSLib import format_exc, format_exc_from, format_exc_only, logger, BulletinHelper, command
from base_plugin import HookResult

class ErrorHandlerPlugin(BasePlugin):
    @command("testerror")
    def test_error_handling(self, param, account, mode: str = "full"):
        """Test error handling: .testerror [full|from|only]"""
        
        def risky_operation():
            return 10 / 0
        
        try:
            risky_operation()
        except Exception as e:
            if mode == "full":
                # Full traceback with current exception
                error = format_exc()
                logger.error(f"Full traceback:\n{error}")
                BulletinHelper.show_error("Check logs for full trace")
            
            elif mode == "from":
                # Format from exception object
                error = format_exc_from(e)
                logger.error(f"From exception:\n{error}")
                BulletinHelper.show_error("Check logs")
            
            elif mode == "only":
                # Just the message
                error = format_exc_only(e)
                BulletinHelper.show_error(f"Error: {error}")
            
            else:
                BulletinHelper.show_error("Mode must be: full, from, only")
        
        return HookResult()
    
    @command("safecall")
    def safe_call(self, param, account, *args: str):
        """Safely call a command with error handling"""
        
        try:
            # Risky operation
            if not args:
                raise ValueError("No arguments provided")
            
            # Process args
            result = " ".join(args).upper()
            BulletinHelper.show_success(f"Result: {result}")
            
        except ValueError as e:
            # User error - show friendly message
            BulletinHelper.show_error(format_exc_only(e))
        
        except Exception as e:
            # Unexpected error - log full trace
            logger.error(f"Unexpected error:\n{format_exc_from(e)}")
            BulletinHelper.show_error("An unexpected error occurred")
        
        return HookResult()
```

#### `get_logs(__id__=None, times=None, lvl=None, as_list=False)`

Get application logs with filtering.

**Parameters:**
- `__id__` (str, optional): Filter by plugin ID
- `times` (int, optional): Number of recent lines
- `lvl` (str, optional): Filter by level ("debug", "info", "warning", "error")
- `as_list` (bool): Return as list instead of string

**Returns:** String or List of log lines

**Example:**

```python
from MSLib import get_logs, BulletinHelper

# Get all logs
all_logs = get_logs()

# Get last 50 lines
recent = get_logs(times=50)

# Get only errors
errors = get_logs(lvl="error")

# Get logs for specific plugin
plugin_logs = get_logs(__id__="my_plugin")

# Get as list
log_lines = get_logs(times=10, as_list=True)
for line in log_lines:
    print(line)
```

**Full Example:**

```python
from MSLib import get_logs, command, BulletinHelper, copy_to_clipboard
from base_plugin import HookResult

class LogViewerPlugin(BasePlugin):
    @command("logs")
    def view_logs(self, param, account, count: int = 50, level: str = "all"):
        """View logs: .logs [count] [level]"""
        
        # Get logs
        if level == "all":
            logs = get_logs(times=count)
        else:
            logs = get_logs(times=count, lvl=level)
        
        if not logs:
            BulletinHelper.show_info("No logs found")
            return HookResult()
        
        # Show preview
        lines = logs.split("\n")
        preview = "\n".join(lines[-10:])  # Last 10 lines
        
        msg = f"**Last {len(lines)} log lines:**\n\n```\n{preview}\n```"
        
        if len(lines) > 10:
            msg += f"\n\n... and {len(lines) - 10} more lines"
        
        BulletinHelper.show_info(msg)
        return HookResult()
    
    @command("errorlogs")
    def view_errors(self, param, account):
        """View only error logs"""
        errors = get_logs(lvl="error", as_list=True)
        
        if not errors:
            BulletinHelper.show_success("No errors! 🎉")
            return HookResult()
        
        # Show error summary
        msg = f"**Found {len(errors)} errors:**\n\n"
        
        for i, error in enumerate(errors[-5:], 1):
            # Truncate long errors
            preview = error[:100] + "..." if len(error) > 100 else error
            msg += f"{i}. {preview}\n"
        
        if len(errors) > 5:
            msg += f"\n... and {len(errors) - 5} more errors"
        
        BulletinHelper.show_error(msg)
        return HookResult()
    
    @command("copylogs")
    def copy_logs(self, param, account, count: int = 100):
        """Copy logs to clipboard: .copylogs 100"""
        logs = get_logs(times=count)
        
        if logs:
            copy_to_clipboard(logs, show_bulletin=False)
            BulletinHelper.show_success(f"Copied {count} log lines")
        else:
            BulletinHelper.show_error("No logs to copy")
        
        return HookResult()
```

### Text Processing

#### `escape_html(text)`

Escape HTML special characters.

**Parameters:**
- `text` (str): Text to escape

**Returns:** Escaped string

**Example:**

```python
from MSLib import escape_html

# Escape HTML
text = "<b>Bold</b> & <i>Italic</i>"
escaped = escape_html(text)
# Result: "&lt;b&gt;Bold&lt;/b&gt; &amp; &lt;i&gt;Italic&lt;/i&gt;"

# Safe for display
user_input = "<script>alert('XSS')</script>"
safe_text = escape_html(user_input)
# Result: "&lt;script&gt;alert('XSS')&lt;/script&gt;"
```

#### `link(url, text=None)`

Create Markdown link.

**Parameters:**
- `url` (str): Link URL
- `text` (str, optional): Link text (default: URL)

**Returns:** Markdown link string

**Example:**

```python
from MSLib import link

# URL as text
github = link("https://github.com")
# Result: "[https://github.com](https://github.com)"

# Custom text
docs = link("https://docs.example.com", "Documentation")
# Result: "[Documentation](https://docs.example.com)"
```

#### `pluralization_string(count, variants)`

Get correct plural form for Russian language.

**Parameters:**
- `count` (int): Number to pluralize
- `variants` (Tuple[str, str, str]): Three forms (1, 2-4, 5+)

**Returns:** Correct variant string

**Example:**

```python
from MSLib import pluralization_string

# Russian pluralization
forms = ("файл", "файла", "файлов")

print(f"1 {pluralization_string(1, forms)}")    # "1 файл"
print(f"2 {pluralization_string(2, forms)}")    # "2 файла"
print(f"5 {pluralization_string(5, forms)}")    # "5 файлов"
print(f"21 {pluralization_string(21, forms)}")  # "21 файл"
print(f"22 {pluralization_string(22, forms)}")  # "22 файла"
print(f"25 {pluralization_string(25, forms)}")  # "25 файлов"
```

**Full Example:**

```python
from MSLib import pluralization_string, BulletinHelper, command
from base_plugin import HookResult

class CounterPlugin(BasePlugin):
    def on_plugin_load(self):
        self.message_count = 0
        self.file_count = 0
    
    @command("stats")
    def show_stats(self, param, account):
        """Show statistics"""
        
        # Plural forms
        msg_forms = ("сообщение", "сообщения", "сообщений")
        file_forms = ("файл", "файла", "файлов")
        
        # Build message
        stats = "**Статистика:**\n\n"
        stats += f"{self.message_count} {pluralization_string(self.message_count, msg_forms)}\n"
        stats += f"{self.file_count} {pluralization_string(self.file_count, file_forms)}"
        
        BulletinHelper.show_info(stats)
        return HookResult()
    
    @command("addmsg")
    def add_messages(self, param, account, count: int = 1):
        """Add messages: .addmsg 5"""
        self.message_count += count
        
        forms = ("сообщение", "сообщения", "сообщений")
        msg = f"Добавлено {count} {pluralization_string(count, forms)}"
        
        BulletinHelper.show_success(msg)
        return HookResult()
```

### Clipboard

#### `copy_to_clipboard(text, show_bulletin=True)`

Copy text to clipboard.

**Parameters:**
- `text` (str): Text to copy
- `show_bulletin` (bool): Show notification (default: True)

**Returns:** bool (success)

**Example:**

```python
from MSLib import copy_to_clipboard

# Copy with notification
copy_to_clipboard("Hello World!")

# Copy silently
copy_to_clipboard("Secret data", show_bulletin=False)

# Check result
success = copy_to_clipboard("Important text")
if success:
    print("Copied successfully")
```

### Type Conversion

#### `arraylist_to_list(jarray)`

Convert Java ArrayList to Python list.

**Parameters:**
- `jarray` (ArrayList): Java ArrayList object

**Returns:** Python list or None

**Example:**

```python
from MSLib import arraylist_to_list
from java.util import ArrayList

# Java ArrayList
java_list = ArrayList()
java_list.add("Hello")
java_list.add("World")

# Convert to Python
python_list = arraylist_to_list(java_list)
# Result: ["Hello", "World"]

# None handling
result = arraylist_to_list(None)  # Returns None
```

#### `list_to_arraylist(python_list, int_auto_convert=True)`

Convert Python list to Java ArrayList.

**Parameters:**
- `python_list` (List): Python list
- `int_auto_convert` (bool): Auto-convert int to Long (default: True)

**Returns:** ArrayList or None

**Example:**

```python
from MSLib import list_to_arraylist

# Python list
python_list = ["Hello", "World", 123]

# Convert to Java
java_list = list_to_arraylist(python_list)

# Without int conversion
java_list2 = list_to_arraylist([1, 2, 3], int_auto_convert=False)
```

**Full Example:**

```python
from MSLib import arraylist_to_list, list_to_arraylist, BulletinHelper, command
from base_plugin import HookResult
from java.util import ArrayList

class JavaInteropPlugin(BasePlugin):
    @command("convert")
    def convert_lists(self, param, account):
        """Test list conversion"""
        
        # Python → Java
        python_list = ["apple", "banana", "cherry", 42]
        java_list = list_to_arraylist(python_list)
        
        BulletinHelper.show_info(
            f"Python list: {python_list}\n"
            f"Java ArrayList size: {java_list.size()}"
        )
        
        # Java → Python
        converted_back = arraylist_to_list(java_list)
        BulletinHelper.show_success(
            f"Converted back: {converted_back}"
        )
        
        return HookResult()
```

#### `cast_arg(arg, target_type)`

Cast string argument to target type.

**Parameters:**
- `arg` (str): String argument
- `target_type` (type): Target Python type (str, int, float, bool)

**Returns:** Casted value

**Raises:** ValueError if cast fails

**Example:**

```python
from MSLib import cast_arg

# Cast to int
num = cast_arg("42", int)  # 42

# Cast to float
price = cast_arg("19.99", float)  # 19.99

# Cast to bool
flag = cast_arg("true", bool)  # True
flag2 = cast_arg("false", bool)  # False
flag3 = cast_arg("yes", bool)  # True

# String (no casting)
text = cast_arg("hello", str)  # "hello"
```

### System

#### `runtime_exec(cmd, return_list_lines=False, raise_errors=True)`

Execute shell command.

**Parameters:**
- `cmd` (List[str]): Command with arguments
- `return_list_lines` (bool): Return list of lines (default: False)
- `raise_errors` (bool): Raise exception on error (default: True)

**Returns:** String output or List of lines

**Example:**

```python
from MSLib import runtime_exec

# Simple command
output = runtime_exec(["ls", "-la"])
print(output)

# Get as list
lines = runtime_exec(["ps", "aux"], return_list_lines=True)
for line in lines:
    print(line)

# Don't raise on error
result = runtime_exec(["invalid_cmd"], raise_errors=False)
```

**Full Example:**

```python
from MSLib import runtime_exec, BulletinHelper, command
from base_plugin import HookResult

class ShellPlugin(BasePlugin):
    @command("shell")
    def exec_shell(self, param, account, *cmd_parts: str):
        """Execute shell command: .shell ls -la"""
        
        if not cmd_parts:
            BulletinHelper.show_error("No command provided")
            return HookResult()
        
        try:
            # Execute command
            output = runtime_exec(list(cmd_parts))
            
            # Show output (truncated)
            preview = output[:500]
            if len(output) > 500:
                preview += "\n... (truncated)"
            
            BulletinHelper.show_info(f"```\n{preview}\n```")
            
        except Exception as e:
            BulletinHelper.show_error(f"Command failed: {e}")
        
        return HookResult()
    
    @command("sysinfo")
    def system_info(self, param, account):
        """Show system info"""
        
        try:
            # Get system info
            uname = runtime_exec(["uname", "-a"])
            uptime = runtime_exec(["uptime"])
            
            info = f"**System Info:**\n\n{uname}\n\n**Uptime:**\n{uptime}"
            BulletinHelper.show_info(info)
            
        except Exception as e:
            BulletinHelper.show_error(f"Failed: {e}")
        
        return HookResult()
```

#### `get_plugin(plugin_id)`

Get loaded plugin instance by ID.

**Parameters:**
- `plugin_id` (str): Plugin ID

**Returns:** Plugin instance or None

**Example:**

```python
from MSLib import get_plugin, logger

# Get plugin
mslib = get_plugin("mslib")
if mslib:
    logger.info(f"MSLib version: {mslib.__version__}")

# Check if plugin loaded
other_plugin = get_plugin("other_plugin")
if other_plugin:
    # Use plugin
    other_plugin.do_something()
else:
    logger.warning("Plugin not loaded")
```

### Localization

#### `localise(key)`

Get localized string.

**Parameters:**
- `key` (str): Localization key

**Returns:** Localized string

**Example:**

```python
from MSLib import localise

# Get localized string
cancel = localise("Cancel")  # Uses system locale
ok = localise("OK")

# Use in UI
button_text = localise("Send")
```

### Async Operations

#### `run_on_ui_thread(func, *args, **kwargs)`

Run function on UI thread.

**Parameters:**
- `func` (Callable): Function to run
- `*args`: Function arguments
- `**kwargs`: Function keyword arguments

**Example:**

```python
from MSLib import run_on_ui_thread, BulletinHelper

def update_ui():
    BulletinHelper.show_info("UI updated!")

# Run on UI thread
run_on_ui_thread(update_ui)

# With arguments
def show_message(msg):
    BulletinHelper.show_info(msg)

run_on_ui_thread(show_message, "Hello from UI thread!")
```

#### `run_on_queue(func, account=0)`

Run function on Telegram queue.

**Parameters:**
- `func` (Callable): Function to run
- `account` (int): Account index

**Example:**

```python
from MSLib import run_on_queue

def send_message_task():
    # Send message
    pass

# Run on queue
run_on_queue(send_message_task, account=0)
```

## 🎯 Complete Usage Examples

### Example 1: Debug Tool

```python
from MSLib import (build_log, get_logs, format_exc, runtime_exec,
                    BulletinHelper, command, copy_to_clipboard)
from base_plugin import HookResult
import logging

class DebugToolPlugin(BasePlugin):
    def on_plugin_load(self):
        self.logger = build_log("DebugTool", logging.DEBUG)
        self.error_count = 0
    
    @command("debuginfo")
    def debug_info(self, param, account):
        """Show debug information"""
        
        try:
            # System info
            python_version = runtime_exec(["python", "--version"])
            
            # Log stats
            all_logs = get_logs(as_list=True)
            errors = get_logs(lvl="error", as_list=True)
            warnings = get_logs(lvl="warning", as_list=True)
            
            # Build info
            info = (
                "🔍 **Debug Information**\n\n"
                f"**Python:** {python_version}\n"
                f"**Total Logs:** {len(all_logs)}\n"
                f"**Errors:** {len(errors)}\n"
                f"**Warnings:** {len(warnings)}\n"
                f"**Error Count:** {self.error_count}"
            )
            
            BulletinHelper.show_info(info)
            
        except Exception as e:
            self.error_count += 1
            error_msg = format_exc()
            self.logger.error(f"Debug info failed:\n{error_msg}")
            BulletinHelper.show_error("Failed to get debug info")
        
        return HookResult()
    
    @command("exportlogs")
    def export_logs(self, param, account, level: str = "all"):
        """Export logs: .exportlogs [all|error|warning]"""
        
        try:
            # Get logs
            if level == "all":
                logs = get_logs()
            else:
                logs = get_logs(lvl=level)
            
            if not logs:
                BulletinHelper.show_info("No logs to export")
                return HookResult()
            
            # Save to file
            import os
            from MSLib import CACHE_DIRECTORY
            
            filename = f"logs_{level}_{int(time.time())}.txt"
            filepath = os.path.join(CACHE_DIRECTORY, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(logs)
            
            BulletinHelper.show_success(
                f"Logs exported to:\n`{filepath}`"
            )
            
        except Exception as e:
            BulletinHelper.show_error(f"Export failed: {format_exc_only(e)}")
        
        return HookResult()
    
    @command("testcrash")
    def test_crash(self, param, account):
        """Test crash reporting"""
        
        try:
            # Intentional error
            result = 10 / 0
        
        except Exception as e:
            self.error_count += 1
            
            # Log full traceback
            full_trace = format_exc()
            self.logger.error(f"Test crash:\n{full_trace}")
            
            # Show user-friendly message
            user_msg = format_exc_only(e)
            BulletinHelper.show_error(
                f"Crash test successful!\n\n{user_msg}\n\nCheck logs for details."
            )
        
        return HookResult()
```

### Example 2: Text Tools

```python
from MSLib import (escape_html, link, pluralization_string, copy_to_clipboard,
                    BulletinHelper, command)
from base_plugin import HookResult

class TextToolsPlugin(BasePlugin):
    @command("escape")
    def escape_text(self, param, account, *text_parts: str):
        """Escape HTML: .escape <b>Hello</b>"""
        
        if not text_parts:
            BulletinHelper.show_error("No text provided")
            return HookResult()
        
        text = " ".join(text_parts)
        escaped = escape_html(text)
        
        copy_to_clipboard(escaped, show_bulletin=False)
        
        result = (
            "**Original:**\n"
            f"{text}\n\n"
            "**Escaped:**\n"
            f"`{escaped}`\n\n"
            "✅ Copied to clipboard"
        )
        
        BulletinHelper.show_info(result)
        return HookResult()
    
    @command("makelink")
    def make_link(self, param, account, url: str, *text_parts: str):
        """Create link: .makelink https://example.com Example Site"""
        
        if not text_parts:
            # URL as text
            result = link(url)
        else:
            # Custom text
            text = " ".join(text_parts)
            result = link(url, text)
        
        copy_to_clipboard(result, show_bulletin=False)
        
        BulletinHelper.show_success(
            f"Link created:\n{result}\n\n✅ Copied to clipboard"
        )
        
        return HookResult()
    
    @command("count")
    def count_items(self, param, account, count: int, item: str = "item"):
        """Count with pluralization: .count 5 файл"""
        
        # Russian plural forms for common words
        plurals = {
            "файл": ("файл", "файла", "файлов"),
            "день": ("день", "дня", "дней"),
            "час": ("час", "часа", "часов"),
            "минута": ("минута", "минуты", "минут"),
            "секунда": ("секунда", "секунды", "секунд"),
        }
        
        if item in plurals:
            forms = plurals[item]
            result = f"{count} {pluralization_string(count, forms)}"
        else:
            result = f"{count} {item}"
        
        BulletinHelper.show_info(result)
        return HookResult()
```

### Example 3: System Monitor

```python
from MSLib import (runtime_exec, get_logs, build_log, BulletinHelper,
                    JsonDB, CACHE_DIRECTORY, command)
from base_plugin import HookResult
import os
import time

class SystemMonitorPlugin(BasePlugin):
    def on_plugin_load(self):
        self.logger = build_log("SysMon")
        self.stats_db = JsonDB(os.path.join(CACHE_DIRECTORY, "system_stats.json"))
    
    @command("sysmon")
    def system_monitor(self, param, account):
        """Show system monitor"""
        
        try:
            # Get system stats
            uptime = runtime_exec(["uptime"])
            df = runtime_exec(["df", "-h"])
            free = runtime_exec(["free", "-h"])
            
            # Parse and format
            stats = (
                "📊 **System Monitor**\n\n"
                f"**Uptime:**\n{uptime}\n\n"
                f"**Disk:**\n```\n{df[:200]}...\n```\n\n"
                f"**Memory:**\n```\n{free[:200]}...\n```"
            )
            
            BulletinHelper.show_info(stats)
            
            # Save stats
            self.stats_db.set("last_check", {
                "time": int(time.time()),
                "uptime": uptime,
                "disk": df,
                "memory": free
            })
            
        except Exception as e:
            self.logger.error(f"System monitor failed: {e}")
            BulletinHelper.show_error("Failed to get system stats")
        
        return HookResult()
    
    @command("appstats")
    def app_stats(self, param, account):
        """Show app statistics"""
        
        # Get log stats
        all_logs = get_logs(as_list=True)
        errors = get_logs(lvl="error", as_list=True)
        warnings = get_logs(lvl="warning", as_list=True)
        
        # Calculate percentages
        total = len(all_logs)
        error_pct = (len(errors) / total * 100) if total > 0 else 0
        warn_pct = (len(warnings) / total * 100) if total > 0 else 0
        
        # Build stats
        stats = (
            "📈 **App Statistics**\n\n"
            f"**Total Logs:** {total:,}\n"
            f"**Errors:** {len(errors):,} ({error_pct:.1f}%)\n"
            f"**Warnings:** {len(warnings):,} ({warn_pct:.1f}%)\n\n"
        )
        
        # Health indicator
        if error_pct < 1:
            stats += "✅ **Health:** Excellent"
        elif error_pct < 5:
            stats += "⚠️ **Health:** Good"
        else:
            stats += "❌ **Health:** Poor"
        
        BulletinHelper.show_info(stats)
        return HookResult()
```

## 💡 Best Practices

### 1. Always Use Logging

```python
# ✅ Good
from MSLib import build_log

logger = build_log("MyPlugin")
logger.info("Plugin loaded")
logger.error(f"Error: {e}")

# ❌ Bad
print("Plugin loaded")  # Not logged
```

### 2. Handle Exceptions Properly

```python
# ✅ Good
from MSLib import format_exc, logger

try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed:\n{format_exc()}")

# ❌ Bad
try:
    risky_operation()
except:
    pass  # Silent failure
```

### 3. Use Type Conversion Safely

```python
# ✅ Good
from MSLib import arraylist_to_list

java_list = get_java_list()
python_list = arraylist_to_list(java_list)
if python_list:
    process(python_list)

# ❌ Bad
python_list = arraylist_to_list(None)  # Returns None
process(python_list)  # May crash
```

## 🐛 Troubleshooting

### Logging Not Working

```python
# Make sure logger is created
from MSLib import build_log
import logging

logger = build_log("MyPlugin", logging.DEBUG)
logger.debug("This should appear in logs")

# Check log level
logger.setLevel(logging.DEBUG)
```

---

## 🆕 New in v1.2.0

### FileSystem Utilities

The `FileSystem` class provides convenient file operations with automatic path resolution.

#### `FileSystem.get_cache_dir(*path)`

Get cache directory path.

**Parameters:**
- `*path` (str): Path components to join

**Returns:** Absolute cache directory path

**Example:**

```python
from MSLib import FileSystem

# Get cache root
cache_root = FileSystem.get_cache_dir()
# /data/data/org.telegram.messenger/cache/mslib_cache

# Get cache subdirectory
my_cache = FileSystem.get_cache_dir("my_plugin", "data")
# /data/data/org.telegram.messenger/cache/mslib_cache/my_plugin/data

# Use for file storage
db_path = FileSystem.get_cache_dir("my_plugin", "database.json")
```

#### `FileSystem.get_plugins_dir(*path)`

Get plugins directory path.

**Parameters:**
- `*path` (str): Path components

**Returns:** Absolute plugins directory path

**Example:**

```python
from MSLib import FileSystem

# Get plugins root
plugins_root = FileSystem.get_plugins_dir()

# Get specific plugin file
my_plugin = FileSystem.get_plugins_dir("my_plugin.py")
```

#### `FileSystem.read_file(filepath, mode='r', encoding='utf-8')`

Read file content safely.

**Parameters:**
- `filepath` (str): File path
- `mode` (str): Read mode ('r' or 'rb')
- `encoding` (str): Text encoding (default: 'utf-8')

**Returns:** File content (str or bytes)

**Example:**

```python
from MSLib import FileSystem

# Read text file
text = FileSystem.read_file("/path/to/file.txt")
if text:
    print(text)

# Read binary file
data = FileSystem.read_file("/path/to/file.bin", mode='rb')

# Custom encoding
content = FileSystem.read_file("/path/to/file.txt", encoding='cp1251')
```

#### `FileSystem.write_file(filepath, content, mode='w', encoding='utf-8')`

Write content to file (creates directories if needed).

**Parameters:**
- `filepath` (str): File path
- `content` (str or bytes): Content to write
- `mode` (str): Write mode ('w' or 'wb')
- `encoding` (str): Text encoding

**Example:**

```python
from MSLib import FileSystem

# Write text file
FileSystem.write_file("/path/to/file.txt", "Hello World!")

# Write binary file
FileSystem.write_file("/path/to/file.bin", b"binary data", mode='wb')

# Auto-creates directories
FileSystem.write_file("/deep/nested/path/file.txt", "content")
```

#### `FileSystem.file_exists(filepath)`

Check if file exists.

**Example:**

```python
from MSLib import FileSystem

if FileSystem.file_exists("/path/to/file.txt"):
    content = FileSystem.read_file("/path/to/file.txt")
```

#### `FileSystem.get_file_size(filepath)`

Get file size in bytes.

**Example:**

```python
from MSLib import FileSystem

size = FileSystem.get_file_size("/path/to/file.txt")
print(f"File size: {size} bytes")
```

**Complete FileSystem Example:**

```python
from MSLib import FileSystem, BulletinHelper, command, format_size
from base_plugin import HookResult

class FileManagerPlugin(BasePlugin):
    @command("savefile")
    def save_file(self, param, account, filename: str, *content_parts: str):
        """Save file: .savefile myfile.txt Hello World"""
        
        if not content_parts:
            BulletinHelper.show_error("No content provided")
            return HookResult()
        
        # Build file path in cache
        filepath = FileSystem.get_cache_dir("files", filename)
        
        # Write content
        content = " ".join(content_parts)
        FileSystem.write_file(filepath, content)
        
        # Get size
        size = FileSystem.get_file_size(filepath)
        
        BulletinHelper.show_success(
            f"File saved: {filename}\n"
            f"Size: {format_size(size)}\n"
            f"Path: {filepath}"
        )
        
        return HookResult()
    
    @command("readfile")
    def read_file(self, param, account, filename: str):
        """Read file: .readfile myfile.txt"""
        
        filepath = FileSystem.get_cache_dir("files", filename)
        
        if not FileSystem.file_exists(filepath):
            BulletinHelper.show_error(f"File not found: {filename}")
            return HookResult()
        
        content = FileSystem.read_file(filepath)
        size = FileSystem.get_file_size(filepath)
        
        # Show preview (max 200 chars)
        preview = content[:200]
        if len(content) > 200:
            preview += "..."
        
        BulletinHelper.show_info(
            f"**{filename}** ({format_size(size)})\n\n"
            f"```\n{preview}\n```"
        )
        
        return HookResult()
```

### Data Compression & Encoding

#### `compress_and_encode(data, level=6)`

Compress and base64 encode data.

**Parameters:**
- `data` (str or bytes): Data to compress
- `level` (int): Compression level 0-9 (default: 6)

**Returns:** Base64 encoded compressed string

**Example:**

```python
from MSLib import compress_and_encode

# Compress text
text = "Large text data " * 1000
compressed = compress_and_encode(text, level=9)

# Compress binary data
binary_data = b"Binary content"
compressed = compress_and_encode(binary_data)

# Size comparison
print(f"Original: {len(text)} bytes")
print(f"Compressed: {len(compressed)} bytes")
# Original: 16000 bytes
# Compressed: ~100 bytes (depending on data)
```

#### `decode_and_decompress(encoded_data)`

Decode base64 and decompress data.

**Parameters:**
- `encoded_data` (str or bytes): Base64 encoded compressed data

**Returns:** Decompressed bytes

**Example:**

```python
from MSLib import compress_and_encode, decode_and_decompress

# Compress
original = "Important data"
compressed = compress_and_encode(original)

# Decompress
decompressed = decode_and_decompress(compressed)
restored = decompressed.decode('utf-8')

print(restored)  # "Important data"
```

**Complete Compression Example:**

```python
from MSLib import (compress_and_encode, decode_and_decompress, 
                    FileSystem, BulletinHelper, command, format_size)
from base_plugin import HookResult

class CompressionPlugin(BasePlugin):
    @command("compress")
    def compress_text(self, param, account, *text_parts: str):
        """Compress text: .compress Hello World"""
        
        if not text_parts:
            BulletinHelper.show_error("No text provided")
            return HookResult()
        
        text = " ".join(text_parts)
        
        # Compress
        compressed = compress_and_encode(text, level=9)
        
        # Calculate compression ratio
        original_size = len(text.encode('utf-8'))
        compressed_size = len(compressed)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        # Show results
        result = (
            f"**Compression Results:**\n\n"
            f"Original: {format_size(original_size)}\n"
            f"Compressed: {format_size(compressed_size)}\n"
            f"Ratio: {ratio:.1f}% saved\n\n"
            f"Compressed data:\n```\n{compressed[:100]}...\n```"
        )
        
        BulletinHelper.show_success(result)
        return HookResult()
    
    @command("savecompressed")
    def save_compressed(self, param, account, filename: str, *text_parts: str):
        """Save compressed file: .savecompressed data.txt.gz Hello World"""
        
        if not text_parts:
            BulletinHelper.show_error("No content provided")
            return HookResult()
        
        text = " ".join(text_parts)
        
        # Compress
        compressed = compress_and_encode(text)
        
        # Save compressed data
        filepath = FileSystem.get_cache_dir("compressed", filename)
        FileSystem.write_file(filepath, compressed)
        
        # Calculate sizes
        original_size = len(text.encode('utf-8'))
        file_size = FileSystem.get_file_size(filepath)
        
        BulletinHelper.show_success(
            f"Compressed file saved!\n\n"
            f"Original: {format_size(original_size)}\n"
            f"Compressed: {format_size(file_size)}\n"
            f"Path: {filepath}"
        )
        
        return HookResult()
    
    @command("loadcompressed")
    def load_compressed(self, param, account, filename: str):
        """Load compressed file: .loadcompressed data.txt.gz"""
        
        filepath = FileSystem.get_cache_dir("compressed", filename)
        
        if not FileSystem.file_exists(filepath):
            BulletinHelper.show_error(f"File not found: {filename}")
            return HookResult()
        
        # Read and decompress
        compressed = FileSystem.read_file(filepath)
        decompressed = decode_and_decompress(compressed)
        text = decompressed.decode('utf-8')
        
        # Show preview
        preview = text[:200]
        if len(text) > 200:
            preview += "..."
        
        BulletinHelper.show_info(
            f"**{filename}**\n\n"
            f"Decompressed size: {format_size(len(text))}\n\n"
            f"```\n{preview}\n```"
        )
        
        return HookResult()
```

### Text Formatting Utilities

#### `format_size(size_bytes)`

Format bytes to human readable size.

**Parameters:**
- `size_bytes` (int): Size in bytes

**Returns:** Formatted string (e.g., "1.5 MB")

**Example:**

```python
from MSLib import format_size

print(format_size(1024))           # "1.0 KB"
print(format_size(1024 * 1024))    # "1.0 MB"
print(format_size(1536 * 1024))    # "1.5 MB"
print(format_size(1024 ** 3))      # "1.0 GB"
print(format_size(500))            # "500.0 B"
```

#### `format_duration(seconds)`

Format seconds to human readable duration.

**Parameters:**
- `seconds` (int): Duration in seconds

**Returns:** Formatted string (e.g., "1h 30m 45s")

**Example:**

```python
from MSLib import format_duration

print(format_duration(30))          # "30s"
print(format_duration(90))          # "1m 30s"
print(format_duration(3661))        # "1h 1m 1s"
print(format_duration(7200))        # "2h 0m 0s"
print(format_duration(86400))       # "24h 0m 0s"
```

#### `unescape_html(text)`

Unescape HTML entities.

**Parameters:**
- `text` (str): HTML-escaped text

**Returns:** Unescaped string

**Example:**

```python
from MSLib import unescape_html

escaped = "&lt;b&gt;Hello&lt;/b&gt; &amp; World"
original = unescape_html(escaped)
print(original)  # "<b>Hello</b> & World"
```

**Formatting Utilities Example:**

```python
from MSLib import (format_size, format_duration, unescape_html,
                    BulletinHelper, command)
from base_plugin import HookResult
import time

class FormatPlugin(BasePlugin):
    def on_plugin_load(self):
        self.start_time = time.time()
        self.bytes_processed = 0
    
    @command("stats")
    def show_stats(self, param, account):
        """Show formatted statistics"""
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time)
        uptime = format_duration(uptime_seconds)
        
        # Format data size
        data_size = format_size(self.bytes_processed)
        
        stats = (
            f"📊 **Statistics**\n\n"
            f"**Uptime:** {uptime}\n"
            f"**Data Processed:** {data_size}\n"
            f"**Operations:** {self.operation_count:,}"
        )
        
        BulletinHelper.show_info(stats)
        return HookResult()
    
    @command("formatsize")
    def format_size_demo(self, param, account, bytes_count: int):
        """Format bytes: .formatsize 1048576"""
        
        formatted = format_size(bytes_count)
        
        BulletinHelper.show_info(
            f"**{bytes_count:,} bytes** = **{formatted}**"
        )
        
        return HookResult()
    
    @command("formattime")
    def format_time_demo(self, param, account, seconds: int):
        """Format seconds: .formattime 3661"""
        
        formatted = format_duration(seconds)
        
        BulletinHelper.show_info(
            f"**{seconds} seconds** = **{formatted}**"
        )
        
        return HookResult()
```

### Enhanced Callbacks

#### `Callback3`

Callback with three arguments.

**Example:**

```python
from MSLib import Callback3

def my_callback(arg1, arg2, arg3):
    print(f"Args: {arg1}, {arg2}, {arg3}")

# Create callback
callback = Callback3(my_callback)

# Use in Java code
some_java_object.setCallback(callback)
```

### Inline Handler Decorator

#### `@inline_handler(method, support_long_click=False)`

Decorator for inline button click handlers.

**Parameters:**
- `method` (str): Handler method name
- `support_long_click` (bool): Support long press (default: False)

**Example:**

```python
from MSLib import inline_handler, Inline, BulletinHelper, command
from base_plugin import HookResult, BasePlugin

class ButtonPlugin(BasePlugin):
    @command("buttons")
    def show_buttons(self, param, account):
        """Show inline buttons"""
        
        markup = Inline.Markup()
        markup.add_row(
            Inline.button("Click me", callback_data="myButton")
        )
        
        # Send message with buttons
        # (implementation depends on your setup)
        
        return HookResult()
    
    @inline_handler("myButton", support_long_click=True)
    def handle_button(self, params):
        """Handle button click"""
        
        if params.long_press:
            BulletinHelper.show_info("Long press detected!")
        else:
            BulletinHelper.show_success("Button clicked!")
        
        return HookResult()
```

---

### Runtime Exec Fails

```python
# Use list for command
from MSLib import runtime_exec

# ✅ Good
output = runtime_exec(["ls", "-la"])

# ❌ Bad
output = runtime_exec("ls -la")  # Should be list
```

### Type Conversion Issues

```python
# Handle None values
from MSLib import arraylist_to_list

java_list = get_list()  # May return None
python_list = arraylist_to_list(java_list) or []
```

---

**Next:** [Integrated Plugins →](integrated-plugins.md)
