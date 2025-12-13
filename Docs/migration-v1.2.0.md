# Migration Guide: MSLib v1.1.0 → v1.2.0

This guide helps you upgrade from MSLib 1.1.0-beta to 1.2.0-beta.

## 📋 Summary

MSLib v1.2.0 is **100% backward compatible** with v1.1.0. All existing code will continue to work without any changes.

## ✨ What's New

### New Features Added

1. **Enhanced MSPlugin** - New helper methods
2. **FileSystem utilities** - Convenient file operations
3. **Data compression** - Built-in compress/decompress
4. **Extended Requests API** - Edit, forward, get full info
5. **Improved Markdown parser** - All Telegram formats
6. **Inline handler decorator** - Simplified button handling
7. **Enhanced JsonDB** - New methods
8. **Better callbacks** - Callback3 for three arguments
9. **Text formatters** - format_size, format_duration
10. **HTML utilities** - unescape_html

### No Breaking Changes

All existing APIs remain unchanged. New features are additions only.

## 🚀 Quick Start

### Step 1: Update MSLib.py

Replace your `MSLib.py` file with the new version.

### Step 2: (Optional) Update Your Plugins

You can start using new features immediately:

```python
# Old way (still works)
class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        logger.info("Plugin loaded")

# New way (enhanced)
from MSLib import MSPlugin

class MyPlugin(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        self.plugin_info("Plugin loaded")  # New method
        self.show_bulletin("Ready!", "success")  # New method
```

## 📦 New Imports Available

```python
# New utilities
from MSLib import (
    FileSystem,              # File operations
    compress_and_encode,     # Data compression
    decode_and_decompress,   # Data decompression
    format_size,             # Format bytes
    format_duration,         # Format seconds
    unescape_html,           # HTML decoding
    Callback3,               # 3-arg callback
    inline_handler,          # Decorator
)
```

## 🔄 Optional Enhancements

### 1. Use MSPlugin Base Class

**Before:**
```python
from base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Manual setup
        import logging
        self.logger = logging.getLogger(self.id)
        self.db = JsonDB(f"{self.id}_data.json")
```

**After:**
```python
from base_plugin import BasePlugin
from MSLib import MSPlugin

class MyPlugin(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        # Auto-configured: self.db, self._logger
        # Plus new methods available!
```

**Benefits:**
- ✅ Auto-configured database
- ✅ Plugin-specific logger
- ✅ Localization helpers
- ✅ Clipboard utilities
- ✅ Notification helpers
- ✅ Async operations
- ✅ Formatting utilities

### 2. Use FileSystem Instead of os.path

**Before:**
```python
import os
from MSLib import CACHE_DIRECTORY

cache_path = os.path.join(CACHE_DIRECTORY, "my_data.json")

with open(cache_path, 'r') as f:
    data = f.read()
```

**After:**
```python
from MSLib import FileSystem

cache_path = FileSystem.get_cache_dir("my_data.json")
data = FileSystem.read_file(cache_path)
```

**Benefits:**
- ✅ Shorter code
- ✅ Auto-creates directories
- ✅ Error handling built-in
- ✅ Encoding management

### 3. Use Compression for Large Data

**Before:**
```python
import json

# Large data storage
data = get_large_data()
json_str = json.dumps(data)

with open("data.json", "w") as f:
    f.write(json_str)
```

**After:**
```python
from MSLib import compress_and_encode, FileSystem
import json

# Compress before storage
data = get_large_data()
json_str = json.dumps(data)
compressed = compress_and_encode(json_str, level=9)

FileSystem.write_file("data.json.gz", compressed)

# Decompress when loading
from MSLib import decode_and_decompress
compressed = FileSystem.read_file("data.json.gz")
json_str = decode_and_decompress(compressed).decode('utf-8')
data = json.loads(json_str)
```

**Benefits:**
- ✅ Reduced storage size (often 80-90% smaller)
- ✅ Faster I/O operations
- ✅ Built-in base64 encoding

### 4. Use Format Utilities

**Before:**
```python
# Manual formatting
file_size = 1048576
if file_size < 1024:
    size_str = f"{file_size} B"
elif file_size < 1024 ** 2:
    size_str = f"{file_size / 1024:.1f} KB"
else:
    size_str = f"{file_size / 1024 ** 2:.1f} MB"

# Manual time formatting
seconds = 3661
hours = seconds // 3600
minutes = (seconds % 3600) // 60
secs = seconds % 60
time_str = f"{hours}h {minutes}m {secs}s"
```

**After:**
```python
from MSLib import format_size, format_duration

# Simple formatting
size_str = format_size(1048576)  # "1.0 MB"
time_str = format_duration(3661)  # "1h 1m 1s"
```

**Benefits:**
- ✅ Much shorter code
- ✅ Consistent formatting
- ✅ Handles edge cases

### 5. Use Enhanced Requests Methods

**Before:**
```python
from MSLib import Requests

# Manual edit implementation
def edit_message(msg_obj, new_text):
    # Complex manual setup
    request = TLRPC.TL_messages_editMessage()
    # ... many lines of setup ...
    Requests.send(request, callback)
```

**After:**
```python
from MSLib import Requests

# Simple edit
Requests.edit_message(msg_obj, new_text, callback=callback)

# Forward messages
Requests.forward_messages(from_peer, to_peer, [msg_id])

# Get full info
Requests.get_full_user(user_id, callback)
Requests.get_full_chat(chat_id, callback)
```

**Benefits:**
- ✅ Much simpler API
- ✅ Less boilerplate code
- ✅ Better error handling

### 6. Use Inline Handler Decorator

**Before:**
```python
class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Manual registration
        Inline.callbacks["myButton"] = self.handle_button
    
    def handle_button(self, params):
        # Handle click
        pass
```

**After:**
```python
from MSLib import inline_handler

class MyPlugin(BasePlugin):
    @inline_handler("myButton", support_long_click=True)
    def handle_button(self, params):
        # Automatically registered!
        if params.long_press:
            # Handle long press
            pass
```

**Benefits:**
- ✅ Auto-registration
- ✅ Cleaner code
- ✅ Long press support

### 7. Use Enhanced JsonDB

**Before:**
```python
db = JsonDB("data.json")

# Remove and save manually
value = db.get("key", "default")
if "key" in db:
    del db["key"]
    db.save()

# Manual bulk update
for key, value in items.items():
    db[key] = value
db.save()
```

**After:**
```python
db = JsonDB("data.json")

# Pop with auto-save
value = db.pop("key", "default")

# Bulk update with one save
db.update_from(key1="value1", key2="value2", key3="value3")
```

**Benefits:**
- ✅ Fewer save() calls
- ✅ More Pythonic
- ✅ Better performance

## 🧪 Testing Your Migration

### Test Checklist

- [ ] Plugin loads without errors
- [ ] Existing commands work
- [ ] Database reads/writes work
- [ ] Auto-updater functions (if used)
- [ ] UI elements display correctly
- [ ] No console errors

### Simple Test Plugin

```python
from base_plugin import BasePlugin, HookResult
from MSLib import MSPlugin, command

class TestPlugin(MSPlugin, BasePlugin):
    """Test v1.2.0 features"""
    
    def on_plugin_load(self):
        super().on_plugin_load()
        self.plugin_info("v1.2.0 test plugin loaded")
        self.show_bulletin("Test plugin ready!", "success")
    
    @command("test")
    def test_features(self, param, account):
        """Test new features: .test"""
        
        # Test logging
        self.plugin_debug("Debug test")
        self.plugin_info("Info test")
        
        # Test formatting
        from MSLib import format_size, format_duration
        size = format_size(1024 * 1024)
        duration = format_duration(3661)
        
        # Test clipboard
        self.copy_to_clipboard("Test data")
        
        # Test FileSystem
        from MSLib import FileSystem
        test_path = FileSystem.get_cache_dir("test.txt")
        FileSystem.write_file(test_path, "Hello v1.2.0!")
        content = FileSystem.read_file(test_path)
        
        # Show results
        self.show_bulletin(
            f"✅ All tests passed!\n\n"
            f"Size: {size}\n"
            f"Duration: {duration}\n"
            f"File: {content}",
            "success"
        )
        
        return HookResult()
```

## 🐛 Troubleshooting

### Issue: Import errors

**Problem:**
```python
ImportError: cannot import name 'FileSystem' from 'MSLib'
```

**Solution:**
Make sure you're using the new MSLib.py file. The old version doesn't have these exports.

### Issue: MSPlugin methods not working

**Problem:**
```python
AttributeError: 'MyPlugin' object has no attribute 'plugin_info'
```

**Solution:**
Make sure you:
1. Inherit from MSPlugin: `class MyPlugin(MSPlugin, BasePlugin)`
2. Call super in on_plugin_load: `super().on_plugin_load()`

### Issue: FileSystem paths not found

**Problem:**
```python
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:**
FileSystem auto-creates directories when writing, but not when reading. Check if file exists first:

```python
from MSLib import FileSystem

if FileSystem.file_exists(filepath):
    content = FileSystem.read_file(filepath)
```

## 📚 Additional Resources

- [MSPlugin Enhanced Features](msplugin-enhanced.md) - Full documentation
- [Utilities](utilities.md) - All utility functions
- [Requests API](requests.md) - Extended API reference
- [API Reference](api-reference.md) - Complete API docs

## 💬 Support

If you encounter any issues during migration:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [documentation](README.md)
3. Check the [CHANGELOG](../MSLib_CHANGELOG.md)
4. Contact @MiracleStudios

## ✅ Migration Complete!

Once you've tested your plugin and everything works, you're done! Enjoy the new features of MSLib v1.2.0! 🎉
