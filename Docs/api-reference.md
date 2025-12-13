# API Reference

Complete reference for all MSLib functions, classes, and constants.

## 📦 Exports

MSLib exports 180+ functions and 38 classes through `__all__`.

## 🆕 New in v1.2.0

- `FileSystem` - File system utilities class
- `compress_and_encode()` - Compress and base64 encode data
- `decode_and_decompress()` - Decode and decompress data
- `format_size()` - Format bytes to human readable
- `format_duration()` - Format seconds to human readable
- `unescape_html()` - Unescape HTML entities
- `Callback3` - Callback with 3 arguments
- `inline_handler()` - Decorator for inline button handlers
- Enhanced `MSPlugin` with new methods
- Extended `Requests` API methods

## 🎯 Quick Navigation

- [Classes](#classes)
- [Functions](#functions)
- [Constants](#constants)
- [Decorators](#decorators)
- [Enums](#enums)

## Classes

### Core Classes

#### `MSPlugin`
Base class for plugins with MSLib integration.

```python
class MyPlugin(MSPlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        # Auto-configured: self.db, self.logger, self.loc
```

**Inherited attributes:**
- `db` - JsonDB instance for plugin data
- `logger` - Logger instance
- `loc` - Localization helper

---

#### `JsonDB`
Auto-saving JSON key-value database.

```python
db = JsonDB(filepath)
db.set("key", value)
value = db.get("key", default=None)
db.delete("key")
db.clear()
```

**Methods:**
- `set(key, value)` - Set value
- `get(key, default=None)` - Get value
- `delete(key)` - Delete key
- `clear()` - Clear all data
- `keys()` - Get all keys
- `values()` - Get all values
- `items()` - Get key-value pairs

---

#### `JsonCacheFile`
Compressed JSON cache with lazy loading.

```python
cache = JsonCacheFile(filepath)
cache.set("key", value)
value = cache.get("key")
cache.save()
```

**Methods:**
- `set(key, value)` - Set value (in memory)
- `get(key, default=None)` - Get value
- `delete(key)` - Delete key
- `clear()` - Clear cache
- `save()` - Save to disk
- `load()` - Load from disk

---

#### `CacheFile`
Raw binary cache file.

```python
cache = CacheFile(filepath)
cache.set(b"data")
data = cache.get()
```

**Methods:**
- `set(data: bytes)` - Set binary data
- `get() -> bytes` - Get binary data
- `clear()` - Clear cache

---

#### `Logger`
Custom logger with Telegram log integration.

```python
logger = build_log("tag")
logger.debug("Debug msg")
logger.info("Info msg")
logger.warning("Warning")
logger.error("Error")
```

---

#### `BulletinHelper`
Show Telegram notifications.

```python
BulletinHelper.show_success("Success!")
BulletinHelper.show_error("Error!")
BulletinHelper.show_info("Info")
BulletinHelper.show_loading("Loading...")
```

**Methods:**
- `show_success(message, with_copy=False, post_id=None)`
- `show_error(message, with_copy=False, post_id=None)`
- `show_info(message, with_copy=False, post_id=None)`
- `show_loading(message)`

---

#### `InnerBulletinHelper`
BulletinHelper with custom prefix.

```python
helper = build_bulletin_helper("[MyPlugin]")
helper.show_success("Done!")
```

**Methods:** Same as BulletinHelper

---

#### `Dispatcher`
Command dispatcher.

```python
dispatcher = Dispatcher(prefix=".")
dispatcher.register_command(command_obj)
result = dispatcher.dispatch(message, param, account)
```

**Methods:**
- `register_command(command)` - Register command
- `unregister_command(name)` - Unregister command
- `dispatch(message, param, account)` - Execute command
- `get_command(name)` - Get command by name
- `get_all_commands()` - Get all commands

---

#### `Command`
Command object.

```python
cmd = Command(
    name="test",
    func=handler,
    aliases=["t"],
    doc="Test command",
    enabled=True
)
```

**Attributes:**
- `name` - Command name
- `func` - Handler function
- `aliases` - Alternative names
- `doc` - Documentation
- `enabled` - Enable/disable flag
- `args` - Argument specifications

---

#### `AutoUpdater`
Auto-update manager.

```python
updater = AutoUpdater.get_instance()
updater.run()
updater.force_stop()
updater.force_update_check()
```

**Methods:**
- `get_instance()` - Get singleton instance
- `run()` - Start updater thread
- `force_stop()` - Stop updater
- `force_update_check()` - Check updates now
- `add_task(task)` - Add update task
- `remove_task(plugin_id)` - Remove task

---

#### `UpdaterTask`
Update task for a plugin.

```python
task = UpdaterTask(
    plugin_id="my_plugin",
    channel_id=-1001234567890,
    message_id=123
)
```

**Attributes:**
- `plugin_id` - Plugin identifier
- `channel_id` - Update channel ID
- `message_id` - Update message ID
- `last_check` - Last check timestamp

---

#### `Spinner`
Loading dialog context manager.

```python
with Spinner("Loading...") as spinner:
    spinner.update("Step 1...")
    do_work()
```

**Methods:**
- `update(message)` - Update message
- `cancel()` - Cancel spinner
- `is_active()` - Check if active

---

#### `UI`
UI dialog helpers.

```python
UI.show_alert("Title", "Message")
UI.show_confirm("Title", "Message", "Yes", "No", callback)
```

**Methods:**
- `show_alert(title, message, callback, account)`
- `show_confirm(title, message, pos_btn, neg_btn, callback, account)`

---

#### `AlertDialogBuilder`
Custom alert builder.

```python
builder = AlertDialogBuilder("Title", "Message")
builder.set_positive_button("OK", callback)
builder.set_negative_button("Cancel", callback)
builder.set_neutral_button("Later", callback)
builder.show(account)
```

**Methods:**
- `set_positive_button(text, callback)`
- `set_negative_button(text, callback)`
- `set_neutral_button(text, callback)`
- `show(account)`

---

#### `Requests`
Telegram API request wrapper.

```python
Requests.send(request, callback, account)
Requests.get_user(user_id, callback, account)
Requests.get_chat(chat_id, callback, account)
Requests.get_message(channel_id, msg_id, callback, account)
Requests.search_messages(peer_id, query, callback, limit, account)
Requests.delete_messages(msg_ids, peer_id, callback, revoke, account)
Requests.ban(chat_id, user_id, until, callback, account)
Requests.unban(chat_id, user_id, callback, account)
Requests.change_slowmode(chat_id, seconds, callback, account)
Requests.get_chat_participant(chat_id, user_id, callback, account)
Requests.reload_admins(chat_id, account)
```

---

#### `HTML`
HTML parser.

```python
text, entities = HTML.parse("<b>Bold</b>")
html = HTML.unparse(text, entities)
```

**Methods:**
- `parse(html_text) -> (text, entities)`
- `unparse(text, entities) -> html`

---

#### `Markdown`
Markdown parser.

```python
text, entities = Markdown.parse("**Bold**")
md = Markdown.unparse(text, entities)
```

**Methods:**
- `parse(md_text) -> (text, entities)`
- `unparse(text, entities) -> markdown`

---

#### `RawEntity`
Text entity.

```python
entity = RawEntity(
    type=TLEntityType.BOLD,
    offset=0,
    length=5,
    url="https://example.com",
    user_id=123,
    language="python"
)
```

**Attributes:**
- `type` - Entity type (TLEntityType)
- `offset` - Start position
- `length` - Entity length
- `url` - Link URL (for TEXT_LINK)
- `user_id` - User ID (for MENTION)
- `language` - Code language (for PRE)

---

### UI Settings Components

#### `Header`
Settings section header.

```python
Header("Section Title")
```

---

#### `Switch`
Toggle switch.

```python
Switch(
    title="Enable feature",
    description="Feature description",
    value_getter=lambda: config.enabled,
    value_setter=lambda v: setattr(config, 'enabled', v)
)
```

---

#### `Input`
Text input field.

```python
Input(
    title="Username",
    hint="Enter username",
    value_getter=lambda: config.username,
    value_setter=lambda v: setattr(config, 'username', v)
)
```

---

#### `Text`
Static text.

```python
Text("Information text")
```

---

#### `Divider`
Visual separator.

```python
Divider()
```

---

## Functions

### Auto-Update

```python
add_autoupdater_task(plugin_id, channel_id, message_id)
remove_autoupdater_task(plugin_id)
download_and_install_plugin(msg, plugin_id, max_tries, is_queued, current_try)
get_plugin(plugin_id)
```

### Logging

```python
build_log(tag, level=logging.INFO) -> Logger
format_exc() -> str
format_exc_from(e: Exception) -> str
format_exc_only(e: Exception) -> str
get_logs(__id__=None, times=None, lvl=None, as_list=False) -> Union[str, List]
```

### Text Processing

```python
escape_html(text: str) -> str
link(url: str, text: str = None) -> str
pluralization_string(count: int, variants: Tuple[str, str, str]) -> str
add_surrogates(text: str) -> str
remove_surrogates(text: str) -> str
```

### Clipboard

```python
copy_to_clipboard(text: str, show_bulletin: bool = True) -> bool
```

### Type Conversion

```python
arraylist_to_list(jarray: ArrayList) -> List
list_to_arraylist(python_list: List, int_auto_convert: bool = True) -> ArrayList
cast_arg(arg: str, target_type: type) -> Any
smart_cast(arg, annotation) -> Any
```

### Localization

```python
localise(key: str) -> str
```

### System

```python
runtime_exec(cmd: List[str], return_list_lines: bool = False, raise_errors: bool = True) -> Union[str, List]
```

### Async

```python
run_on_ui_thread(func, *args, **kwargs)
run_on_queue(func, account=0)
```

### Bulletin Helpers

```python
build_bulletin_helper(prefix: str = None) -> InnerBulletinHelper
```

### Command Helpers

```python
create_command(func: Callable, name: str) -> Command
parse_args(raw_args: List[str], command_args: List) -> Tuple
is_allowed_type(arg_type) -> bool
```

### Request Helpers

```python
request_callback_factory(custom_callback: Callable) -> Callable
```

## Constants

### Directories

```python
CACHE_DIRECTORY: str  # MSLib cache directory
PLUGINS_DIRECTORY: str  # Plugins directory
```

### Locale

```python
LOCALE: str  # System locale ("en", "ru", etc.)
```

### Premium Types

```python
NOT_PREMIUM = 0
TELEGRAM_PREMIUM = 1
MSLIB_GLOBAL_PREMIUM = 2
```

### Settings Defaults

```python
DEFAULT_AUTOUPDATE_TIMEOUT = "600"  # 10 minutes
DEFAULT_DISABLE_TIMESTAMP_CHECK = False
DEFAULT_DEBUG_MODE = False
```

### MSLib Auto-Update

```python
MSLIB_AUTOUPDATE_CHANNEL_ID = -1003314084396
MSLIB_AUTOUPDATE_MSG_ID = 3
```

### Command Types

```python
ALLOWED_ARG_TYPES = (str, int, float, bool, Any)
ALLOWED_ORIGIN = (Union, Optional)
```

## Decorators

### `@command`

Register command.

```python
@command()
def my_command(self, param, account):
    """Default command name from function"""
    pass

@command("custom")
def handler(self, param, account):
    """Custom command name"""
    pass

@command("test", aliases=["t"], doc="Test cmd")
def test(self, param, account, arg: str):
    """With arguments"""
    pass
```

**Parameters:**
- `cmd` - Command name (optional, defaults to function name)
- `aliases` - List of aliases
- `doc` - Documentation string
- `enabled` - Enable/disable command

---

### `@uri`

Register URI handler.

```python
@uri("myapp://action")
def handle_uri(self, param, account):
    """Handle myapp://action"""
    pass
```

---

### `@message_uri`

Register message URI handler.

```python
@message_uri("msg://action", support_long_click=True)
def handle_message_uri(self, param, account):
    """Handle msg://action in messages"""
    pass
```

---

### `@watcher`

Register message watcher.

```python
@watcher()
def on_message(self, message, param, account):
    """Called for every message"""
    if "keyword" in message:
        # React to message
        pass
```

---

## Enums

### `TLEntityType`

Text entity types.

```python
TLEntityType.BOLD
TLEntityType.ITALIC
TLEntityType.UNDERLINE
TLEntityType.STRIKETHROUGH
TLEntityType.CODE
TLEntityType.PRE
TLEntityType.TEXT_LINK
TLEntityType.TEXT_URL
TLEntityType.MENTION
TLEntityType.HASHTAG
TLEntityType.CASHTAG
TLEntityType.EMAIL
TLEntityType.PHONE
TLEntityType.BOT_COMMAND
TLEntityType.BLOCKQUOTE
TLEntityType.SPOILER
TLEntityType.CUSTOM_EMOJI
```

---

## Complete Export List

### Classes (36)

```python
MSPlugin, JsonDB, JsonCacheFile, CacheFile, Logger, CustomLogger,
BulletinHelper, InnerBulletinHelper, Dispatcher, Command, ArgSpec,
AutoUpdater, UpdaterTask, Spinner, UI, AlertDialogBuilder,
Requests, HTML, Markdown, RawEntity, TLEntityType,
Header, Switch, Input, Text, Divider,
HTMLParserTL, MarkdownParser,
HashTagsFixHook, ArticleViewerFixHook, NoCallConfirmationHook, OldBottomForwardHook,
Callback1, Callback2, Callback5,
SettingsBuilder
```

### Functions (172)

#### Auto-Update (4)
```python
add_autoupdater_task, remove_autoupdater_task,
download_and_install_plugin, get_plugin
```

#### Logging (5)
```python
build_log, format_exc, format_exc_from, format_exc_only, get_logs
```

#### Text (5)
```python
escape_html, link, pluralization_string, add_surrogates, remove_surrogates
```

#### Clipboard (1)
```python
copy_to_clipboard
```

#### Type Conversion (4)
```python
arraylist_to_list, list_to_arraylist, cast_arg, smart_cast
```

#### Localization (1)
```python
localise
```

#### System (2)
```python
runtime_exec, get_plugin
```

#### Async (2)
```python
run_on_ui_thread, run_on_queue
```

#### Bulletin (1)
```python
build_bulletin_helper
```

#### Commands (3)
```python
create_command, parse_args, is_allowed_type
```

#### Requests (1)
```python
request_callback_factory
```

#### And 140+ more utility functions...

### Constants (10)

```python
CACHE_DIRECTORY, PLUGINS_DIRECTORY, LOCALE,
NOT_PREMIUM, TELEGRAM_PREMIUM, MSLIB_GLOBAL_PREMIUM,
DEFAULT_AUTOUPDATE_TIMEOUT, DEFAULT_DISABLE_TIMESTAMP_CHECK, DEFAULT_DEBUG_MODE,
MSLIB_AUTOUPDATE_CHANNEL_ID, MSLIB_AUTOUPDATE_MSG_ID,
ALLOWED_ARG_TYPES, ALLOWED_ORIGIN
```

### Decorators (4)

```python
@command, @uri, @message_uri, @watcher
```

---

## Version Info

```python
__name__ = "MSLib"
__id__ = "mslib"
__version__ = "1.1.0-beta"
__author__ = "@Imrcle"
__description__ = "Powerful Utility Library for exteraGram Plugin Development"
__min_version__ = "12.0.0"
```

---

## Quick Reference Card

### Most Used Functions

```python
# Logging
from MSLib import build_log, logger
logger.info("Message")

# Notifications
from MSLib import BulletinHelper
BulletinHelper.show_success("Done!")

# Storage
from MSLib import JsonDB
db = JsonDB("data.json")
db.set("key", value)

# Commands
from MSLib import command
@command()
def my_cmd(self, param, account):
    pass

# Auto-Update
from MSLib import add_autoupdater_task
add_autoupdater_task("plugin", -1001234, 123)

# Requests
from MSLib import Requests
Requests.get_user(123, callback, account)

# UI
from MSLib import Spinner, UI
with Spinner("Loading..."):
    work()
```

---

**[← Back to Documentation](README.md)**
