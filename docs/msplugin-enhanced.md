# MSPlugin Enhanced Features (v1.2.0)

This guide covers the new features added to `MSPlugin` in MSLib v1.2.0.

## 📖 Overview

MSPlugin now includes additional helper methods for:

- 📝 **Logging** - Plugin-specific logger
- 📋 **Clipboard** - Copy to clipboard
- 🔔 **Notifications** - Show bulletins
- ⚡ **Async Operations** - Run async and scheduled tasks
- 🎨 **Formatting** - Format sizes, durations, HTML

## 🚀 Getting Started

```python
from base_plugin import BasePlugin
from MSLib import MSPlugin, command

class MyPlugin(MSPlugin, BasePlugin):
    """Enhanced plugin with MSLib utilities"""
    
    strings = {
        "en": {
            "hello": "Hello, {name}!",
            "loaded": "Plugin loaded successfully"
        },
        "ru": {
            "hello": "Привет, {name}!",
            "loaded": "Плагин загружен успешно"
        }
    }
    
    def on_plugin_load(self):
        super().on_plugin_load()
        # Auto-configured: self.db, self._logger
        
        # Use plugin methods
        self.plugin_info("Plugin initialized")
        self.show_bulletin(self.string("loaded"), "success")
```

## 📚 API Reference

### Logging Methods

#### `get_logger()`

Get plugin-specific logger instance.

**Returns:** logging.Logger

**Example:**

```python
class LoggingPlugin(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Get logger
        logger = self.get_logger()
        
        # Use logger
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
```

#### `plugin_log(message, level='INFO')`

Log message with plugin context.

**Parameters:**
- `message` (str): Log message
- `level` (str): Log level (DEBUG, INFO, WARNING, ERROR)

**Example:**

```python
self.plugin_log("Processing data...", "INFO")
self.plugin_log("Data processed", "DEBUG")
```

#### `plugin_debug(message)`, `plugin_info(message)`, `plugin_warn(message)`, `plugin_error(message)`

Convenience logging methods.

**Example:**

```python
class MyPlugin(MSPlugin, BasePlugin):
    @command("process")
    def process_data(self, param, account, *args):
        self.plugin_debug(f"Processing with args: {args}")
        
        try:
            # Process data
            result = self.do_processing(args)
            self.plugin_info(f"Processing complete: {result}")
            
        except ValueError as e:
            self.plugin_warn(f"Invalid data: {e}")
            return HookResult()
        
        except Exception as e:
            self.plugin_error(f"Processing failed: {e}")
            raise
        
        return HookResult()
```

### Clipboard Methods

#### `copy_to_clipboard(text, show_bulletin=True)`

Copy text to clipboard with optional notification.

**Parameters:**
- `text` (str): Text to copy
- `show_bulletin` (bool): Show success notification

**Returns:** bool (success)

**Example:**

```python
class ClipboardPlugin(MSPlugin, BasePlugin):
    @command("copy")
    def copy_text(self, param, account, *text_parts: str):
        """Copy text to clipboard: .copy Hello World"""
        
        if not text_parts:
            self.show_bulletin("No text provided", "error")
            return HookResult()
        
        text = " ".join(text_parts)
        
        # Copy with notification
        if self.copy_to_clipboard(text):
            self.plugin_info(f"Copied {len(text)} characters")
        
        return HookResult()
    
    @command("copysilent")
    def copy_silent(self, param, account, *text_parts: str):
        """Copy without notification"""
        
        text = " ".join(text_parts)
        
        # Copy silently
        success = self.copy_to_clipboard(text, show_bulletin=False)
        
        if success:
            self.plugin_info("Text copied silently")
        
        return HookResult()
```

### Notification Methods

#### `show_bulletin(message, level='info')`

Show bulletin notification with plugin name.

**Parameters:**
- `message` (str): Notification message
- `level` (str): Notification level ('info', 'success', 'error')

**Example:**

```python
class NotificationPlugin(MSPlugin, BasePlugin):
    @command("notify")
    def show_notification(self, param, account, level: str, *msg_parts: str):
        """Show notification: .notify success Hello!"""
        
        if level not in ('info', 'success', 'error'):
            level = 'info'
        
        message = " ".join(msg_parts) if msg_parts else "Test notification"
        
        self.show_bulletin(message, level)
        return HookResult()
    
    @command("process")
    def process_with_feedback(self, param, account, data: str):
        """Process with user feedback"""
        
        self.show_bulletin("Processing started...", "info")
        
        try:
            # Process
            result = self.do_processing(data)
            self.show_bulletin(f"Success! Result: {result}", "success")
            
        except Exception as e:
            self.show_bulletin(f"Error: {e}", "error")
        
        return HookResult()
```

### Async Operations

#### `run_async(func, *args, **kwargs)`

Run function asynchronously in background thread.

**Parameters:**
- `func` (Callable): Function to run
- `*args`: Function arguments
- `**kwargs`: Function keyword arguments

**Returns:** Thread instance

**Example:**

```python
class AsyncPlugin(MSPlugin, BasePlugin):
    @command("fetch")
    def fetch_data(self, param, account, url: str):
        """Fetch data asynchronously: .fetch https://api.example.com"""
        
        def fetch_task():
            try:
                import requests
                response = requests.get(url, timeout=10)
                data = response.json()
                
                # Update on UI thread
                from MSLib import run_on_ui_thread
                run_on_ui_thread(
                    lambda: self.show_bulletin(
                        f"Fetched {len(data)} items", "success"
                    )
                )
                
            except Exception as e:
                self.plugin_error(f"Fetch failed: {e}")
                run_on_ui_thread(
                    lambda: self.show_bulletin("Fetch failed", "error")
                )
        
        # Run async
        self.run_async(fetch_task)
        self.show_bulletin("Fetching data...", "info")
        
        return HookResult()
```

#### `schedule_delayed(func, delay, *args, **kwargs)`

Schedule function to run after delay.

**Parameters:**
- `func` (Callable): Function to run
- `delay` (int): Delay in seconds
- `*args`: Function arguments
- `**kwargs`: Function keyword arguments

**Returns:** Thread instance

**Example:**

```python
class SchedulerPlugin(MSPlugin, BasePlugin):
    @command("remind")
    def set_reminder(self, param, account, seconds: int, *message_parts: str):
        """Set reminder: .remind 60 Take a break!"""
        
        message = " ".join(message_parts) if message_parts else "Reminder!"
        
        def show_reminder():
            from MSLib import run_on_ui_thread
            run_on_ui_thread(
                lambda: self.show_bulletin(message, "info")
            )
            self.plugin_info(f"Reminder shown: {message}")
        
        # Schedule
        self.schedule_delayed(show_reminder, seconds)
        
        self.show_bulletin(
            f"Reminder set for {seconds}s", "success"
        )
        
        return HookResult()
    
    @command("autopost")
    def auto_post(self, param, account, interval: int, count: int):
        """Auto-post messages: .autopost 10 5"""
        
        def post_message(index):
            msg = f"Auto-post #{index}/{count}"
            self.show_bulletin(msg, "info")
            
            if index < count:
                # Schedule next
                self.schedule_delayed(
                    post_message, interval, index + 1
                )
        
        # Start
        post_message(1)
        return HookResult()
```

### Formatting Methods

#### `escape_html(text)`

Escape HTML entities safely.

**Example:**

```python
class FormatterPlugin(MSPlugin, BasePlugin):
    @command("safe")
    def make_safe(self, param, account, *text_parts: str):
        """Escape HTML: .safe <script>alert('XSS')</script>"""
        
        text = " ".join(text_parts)
        safe_text = self.escape_html(text)
        
        self.show_bulletin(
            f"**Original:**\n{text}\n\n"
            f"**Safe:**\n`{safe_text}`",
            "info"
        )
        
        return HookResult()
```

#### `format_size(size_bytes)`

Format bytes to human readable size.

**Example:**

```python
class SizePlugin(MSPlugin, BasePlugin):
    @command("filesize")
    def show_file_size(self, param, account, bytes_count: int):
        """Format file size: .filesize 1048576"""
        
        formatted = self.format_size(bytes_count)
        
        self.show_bulletin(
            f"{bytes_count:,} bytes = {formatted}",
            "info"
        )
        
        return HookResult()
    
    @command("stats")
    def show_stats(self, param, account):
        """Show storage stats"""
        
        total_size = self.get_db("total_processed", 0)
        file_count = self.get_db("file_count", 0)
        
        avg_size = total_size // file_count if file_count > 0 else 0
        
        stats = (
            f"📊 **Statistics**\n\n"
            f"Files: {file_count:,}\n"
            f"Total: {self.format_size(total_size)}\n"
            f"Average: {self.format_size(avg_size)}"
        )
        
        self.show_bulletin(stats, "info")
        return HookResult()
```

#### `format_duration(seconds)`

Format seconds to human readable duration.

**Example:**

```python
class DurationPlugin(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        import time
        self.start_time = time.time()
    
    @command("uptime")
    def show_uptime(self, param, account):
        """Show plugin uptime"""
        
        import time
        uptime_seconds = int(time.time() - self.start_time)
        uptime = self.format_duration(uptime_seconds)
        
        self.show_bulletin(
            f"⏱️ **Uptime:** {uptime}",
            "info"
        )
        
        return HookResult()
    
    @command("timer")
    def show_timer(self, param, account, seconds: int):
        """Show formatted timer: .timer 3661"""
        
        formatted = self.format_duration(seconds)
        
        self.show_bulletin(
            f"{seconds}s = {formatted}",
            "info"
        )
        
        return HookResult()
```

## 🎯 Complete Examples

### Example 1: Data Processor

```python
from MSLib import MSPlugin, command, FileSystem
from base_plugin import BasePlugin, HookResult
import time

class DataProcessor(MSPlugin, BasePlugin):
    strings = {
        "en": {
            "processing": "Processing {count} items...",
            "complete": "Processing complete!",
            "error": "Processing failed: {error}"
        }
    }
    
    def on_plugin_load(self):
        super().on_plugin_load()
        self.start_time = time.time()
        self.processed_count = 0
        self.total_bytes = 0
    
    @command("process")
    def process_data(self, param, account, *items: str):
        """Process data items: .process item1 item2 item3"""
        
        if not items:
            self.show_bulletin("No items to process", "error")
            return HookResult()
        
        # Show start
        msg = self.string("processing", count=len(items))
        self.show_bulletin(msg, "info")
        self.plugin_info(f"Starting processing of {len(items)} items")
        
        def process_task():
            try:
                for i, item in enumerate(items, 1):
                    # Simulate processing
                    time.sleep(0.5)
                    
                    # Update stats
                    self.processed_count += 1
                    self.total_bytes += len(item.encode('utf-8'))
                    
                    self.plugin_debug(f"Processed {i}/{len(items)}: {item}")
                
                # Save to DB
                self.set_db("processed_count", self.processed_count)
                self.set_db("total_bytes", self.total_bytes)
                
                # Show completion on UI thread
                from MSLib import run_on_ui_thread
                run_on_ui_thread(
                    lambda: self.show_bulletin(
                        self.string("complete"), "success"
                    )
                )
                
            except Exception as e:
                self.plugin_error(f"Processing error: {e}")
                from MSLib import run_on_ui_thread
                run_on_ui_thread(
                    lambda: self.show_bulletin(
                        self.string("error", error=str(e)), "error"
                    )
                )
        
        # Run async
        self.run_async(process_task)
        return HookResult()
    
    @command("stats")
    def show_stats(self, param, account):
        """Show processing statistics"""
        
        uptime = self.format_duration(int(time.time() - self.start_time))
        total_size = self.format_size(self.total_bytes)
        
        stats = (
            f"📊 **Statistics**\n\n"
            f"⏱️ Uptime: {uptime}\n"
            f"📝 Processed: {self.processed_count:,}\n"
            f"💾 Total Size: {total_size}"
        )
        
        self.show_bulletin(stats, "info")
        return HookResult()
    
    @command("export")
    def export_stats(self, param, account):
        """Export statistics to file"""
        
        stats_data = {
            "processed_count": self.processed_count,
            "total_bytes": self.total_bytes,
            "uptime": int(time.time() - self.start_time)
        }
        
        # Save to file
        import json
        filepath = FileSystem.get_cache_dir("stats.json")
        FileSystem.write_file(
            filepath,
            json.dumps(stats_data, indent=2)
        )
        
        # Copy path to clipboard
        self.copy_to_clipboard(filepath, show_bulletin=False)
        
        self.show_bulletin(
            f"Stats exported to:\n`{filepath}`\n\n"
            "✅ Path copied to clipboard",
            "success"
        )
        
        return HookResult()
```

### Example 2: Auto-Backup System

```python
from MSLib import MSPlugin, command, FileSystem, compress_and_encode
from base_plugin import BasePlugin, HookResult
import time

class AutoBackup(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Start auto-backup
        interval = self.get_db("backup_interval", 3600)  # 1 hour
        self.schedule_backup(interval)
    
    def schedule_backup(self, interval):
        """Schedule next backup"""
        
        def backup_task():
            self.perform_backup()
            # Schedule next
            self.schedule_delayed(
                lambda: self.schedule_backup(interval),
                interval
            )
        
        self.schedule_delayed(backup_task, interval)
        self.plugin_info(f"Backup scheduled in {interval}s")
    
    def perform_backup(self):
        """Perform backup"""
        
        self.plugin_info("Starting backup...")
        
        try:
            # Collect data
            data = {
                "timestamp": int(time.time()),
                "db": dict(self.db),
                "settings": self.get_all_settings()
            }
            
            # Compress
            import json
            json_data = json.dumps(data)
            compressed = compress_and_encode(json_data, level=9)
            
            # Save
            filename = f"backup_{int(time.time())}.json.gz"
            filepath = FileSystem.get_cache_dir("backups", filename)
            FileSystem.write_file(filepath, compressed)
            
            # Update stats
            size = FileSystem.get_file_size(filepath)
            self.set_db("last_backup", int(time.time()))
            self.set_db("last_backup_size", size)
            
            self.plugin_info(
                f"Backup complete: {filename} ({self.format_size(size)})"
            )
            
        except Exception as e:
            self.plugin_error(f"Backup failed: {e}")
    
    @command("backup")
    def manual_backup(self, param, account):
        """Trigger manual backup"""
        
        self.show_bulletin("Starting backup...", "info")
        
        def backup_task():
            self.perform_backup()
            
            from MSLib import run_on_ui_thread
            run_on_ui_thread(
                lambda: self.show_bulletin("Backup complete!", "success")
            )
        
        self.run_async(backup_task)
        return HookResult()
    
    @command("backupstats")
    def backup_stats(self, param, account):
        """Show backup statistics"""
        
        last_backup = self.get_db("last_backup", 0)
        last_size = self.get_db("last_backup_size", 0)
        
        if last_backup == 0:
            self.show_bulletin("No backups yet", "info")
            return HookResult()
        
        # Calculate time since last backup
        elapsed = int(time.time() - last_backup)
        elapsed_str = self.format_duration(elapsed)
        
        stats = (
            f"💾 **Backup Status**\n\n"
            f"Last backup: {elapsed_str} ago\n"
            f"Size: {self.format_size(last_size)}"
        )
        
        self.show_bulletin(stats, "info")
        return HookResult()
```

## 💡 Best Practices

### 1. Always call super().on_plugin_load()

```python
# ✅ Good
def on_plugin_load(self):
    super().on_plugin_load()  # Initialize MSPlugin features
    # Your code here

# ❌ Bad
def on_plugin_load(self):
    # Missing super() call - features won't work!
    pass
```

### 2. Use appropriate logging levels

```python
# ✅ Good
self.plugin_debug("Detailed info for debugging")
self.plugin_info("Normal operation info")
self.plugin_warn("Something unexpected but handled")
self.plugin_error("Critical error occurred")

# ❌ Bad
self.plugin_info("Error: Something failed")  # Wrong level
```

### 3. Handle async operations properly

```python
# ✅ Good
def async_task():
    result = heavy_computation()
    
    # Update UI on UI thread
    from MSLib import run_on_ui_thread
    run_on_ui_thread(
        lambda: self.show_bulletin(f"Done: {result}", "success")
    )

self.run_async(async_task)

# ❌ Bad
def async_task():
    result = heavy_computation()
    self.show_bulletin(f"Done: {result}", "success")  # UI from wrong thread!
```

### 4. Use formatting utilities

```python
# ✅ Good
size_str = self.format_size(file_size)
duration_str = self.format_duration(elapsed)

# ❌ Bad
size_str = f"{file_size} bytes"  # Not human readable
duration_str = f"{elapsed}s"  # Not formatted nicely
```

---

**Related Documentation:**
- [Getting Started](getting-started.md)
- [Utilities](utilities.md)
- [API Reference](api-reference.md)
