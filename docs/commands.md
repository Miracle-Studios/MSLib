# Commands System

Build powerful command handlers with type validation, automatic argument parsing, and flexible routing.

## 📖 Overview

MSLib's command system provides:

- ✅ Decorator-based command registration
- ✅ Automatic type conversion and validation
- ✅ Support for Union and Optional types
- ✅ Custom command prefix
- ✅ Command aliases
- ✅ Subcommands support
- ✅ Error handling

## 🚀 Quick Start

### Basic Command

```python
from base_plugin import BasePlugin, HookResult
from MSLib import command, BulletinHelper

class MyPlugin(BasePlugin):
    @command("hello")
    def hello_cmd(self, param, account):
        """Say hello"""
        BulletinHelper.show_success("Hello, World!")
        return HookResult()
```

Usage: `.hello`

### Command with Arguments

```python
@command("greet")
def greet_cmd(self, param, account, name: str):
    """Greet someone: .greet John"""
    BulletinHelper.show_info(f"Hello, {name}!")
    return HookResult()
```

Usage: `.greet Alice`

## 📚 API Reference

### Decorators

#### `@command()`

Registers a function as a command.

**Signature:**

```python
@command(
    cmd: Optional[str] = None,
    *,
    aliases: Optional[List[str]] = None,
    doc: Optional[str] = None,
    enabled: Optional[Union[str, bool]] = None
)
```

**Parameters:**
- `cmd` (str): Command name (default: function name)
- `aliases` (List[str]): Alternative names
- `doc` (str): Localization key for description
- `enabled` (str | bool): Setting key or bool to enable/disable

**Examples:**

```python
# Simple command
@command()
def test(self, param, account):
    return HookResult()

# Custom name
@command("hello")
def greeting(self, param, account):
    return HookResult()

# With aliases
@command("calculate", aliases=["calc", "c"])
def calculator(self, param, account):
    return HookResult()

# With documentation
@command("help", doc="help_text_key")
def show_help(self, param, account):
    return HookResult()

# Conditional enabling
@command("admin", enabled="is_admin_mode")
def admin_cmd(self, param, account):
    # Only available when is_admin_mode setting is True
    return HookResult()
```

### Type Annotations

Commands support automatic type conversion:

#### Supported Types

```python
from typing import Optional, Union

@command("types")
def type_demo(
    self,
    param,
    account,
    text: str,           # String
    count: int,          # Integer
    price: float,        # Float
    enabled: bool,       # Boolean (true/1/yes/on or false/0/no/off)
    optional: Optional[str] = None,  # Optional argument
    multi: Union[int, str] = 0       # Multiple types
):
    return HookResult()
```

Usage examples:
```
.types hello 42 3.14 true optional_value mixed_value
.types "with spaces" 100 2.5 false
.types simple 10 1.0 yes
```

### Dispatcher

Central command router.

#### Constructor

```python
from MSLib import Dispatcher

dispatcher = Dispatcher(
    plugin_id="my_plugin",
    prefix=".",
    commands_priority=-1
)
```

**Parameters:**
- `plugin_id` (str): Plugin identifier
- `prefix` (str): Command prefix (default: ".")
- `commands_priority` (int): Hook priority

#### Methods

##### `register_command(name)`

Decorator to register commands.

```python
@dispatcher.register_command("test")
def test_handler(param, account):
    BulletinHelper.show_info("Test command")
    return HookResult()
```

##### `unregister_command(name)`

Remove a command.

```python
dispatcher.unregister_command("test")
```

##### `set_prefix(prefix)`

Change command prefix.

```python
dispatcher.set_prefix("!")
# Commands now use: !command
```

##### `validate_prefix(prefix)` (static)

Check if prefix is valid.

```python
if Dispatcher.validate_prefix("!"):
    dispatcher.set_prefix("!")
```

## 🎯 Usage Examples

### Example 1: Calculator Command

```python
from MSLib import command, BulletinHelper
from base_plugin import HookResult

class Calculator(BasePlugin):
    @command("add", aliases=["sum", "+"])
    def add_cmd(self, param, account, a: int, b: int):
        """Add two numbers: .add 5 10"""
        result = a + b
        BulletinHelper.show_success(f"{a} + {b} = {result}")
        return HookResult()
    
    @command("multiply", aliases=["mul", "*"])
    def multiply_cmd(self, param, account, a: float, b: float):
        """Multiply: .multiply 3.5 2"""
        result = a * b
        BulletinHelper.show_info(f"{a} × {b} = {result}")
        return HookResult()
    
    @command("calc")
    def calc_cmd(self, param, account, expression: str):
        """Evaluate: .calc 2+2*2"""
        try:
            # Simple eval (be careful in production!)
            result = eval(expression)
            BulletinHelper.show_success(f"{expression} = {result}")
        except Exception as e:
            BulletinHelper.show_error(f"Invalid expression: {e}")
        return HookResult()
```

### Example 2: User Management

```python
from MSLib import command, BulletinHelper, JsonDB, CACHE_DIRECTORY
from typing import Optional
import os

class UserManager(BasePlugin):
    def on_plugin_load(self):
        self.users = JsonDB(os.path.join(CACHE_DIRECTORY, "users.json"))
    
    @command("adduser")
    def add_user(self, param, account, user_id: int, name: str, role: str = "user"):
        """Add user: .adduser 123456789 "John Doe" admin"""
        users = self.users.get("list", {})
        users[str(user_id)] = {"name": name, "role": role}
        self.users.set("list", users)
        
        BulletinHelper.show_success(f"Added {name} as {role}")
        return HookResult()
    
    @command("getuser")
    def get_user(self, param, account, user_id: int):
        """Get user info: .getuser 123456789"""
        users = self.users.get("list", {})
        user = users.get(str(user_id))
        
        if user:
            BulletinHelper.show_info(
                f"Name: {user['name']}\n"
                f"Role: {user['role']}"
            )
        else:
            BulletinHelper.show_error("User not found")
        
        return HookResult()
    
    @command("listusers")
    def list_users(self, param, account, role: Optional[str] = None):
        """List users: .listusers [role]"""
        users = self.users.get("list", {})
        
        filtered = users
        if role:
            filtered = {
                uid: u for uid, u in users.items()
                if u.get("role") == role
            }
        
        if filtered:
            user_list = "\n".join(
                f"• {u['name']} ({uid}): {u['role']}"
                for uid, u in filtered.items()
            )
            BulletinHelper.show_info(f"Users:\n{user_list}")
        else:
            BulletinHelper.show_info("No users found")
        
        return HookResult()
```

### Example 3: Settings Commands

```python
from MSLib import command, BulletinHelper
from typing import Union

class SettingsPlugin(BasePlugin):
    @command("set")
    def set_setting(self, param, account, key: str, value: Union[str, int, bool]):
        """Set a setting: .set theme dark"""
        # Convert string to appropriate type
        if isinstance(value, str):
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
        
        self.save_setting(key, value)
        BulletinHelper.show_success(f"Set {key} = {value}")
        return HookResult()
    
    @command("get")
    def get_setting(self, param, account, key: str):
        """Get a setting: .get theme"""
        value = self.get_setting(key, "not set")
        BulletinHelper.show_info(f"{key} = {value}")
        return HookResult()
    
    @command("reset")
    def reset_settings(self, param, account, confirm: bool = False):
        """Reset all settings: .reset true"""
        if not confirm:
            BulletinHelper.show_error("Add 'true' to confirm reset")
            return HookResult()
        
        # Reset logic here
        BulletinHelper.show_success("Settings reset")
        return HookResult()
```

### Example 4: Variadic Arguments

```python
from MSLib import command, BulletinHelper

class TextPlugin(BasePlugin):
    @command("echo")
    def echo_cmd(self, param, account, *words: str):
        """Echo text: .echo hello world"""
        text = " ".join(words)
        BulletinHelper.show_info(text)
        return HookResult()
    
    @command("join")
    def join_cmd(self, param, account, separator: str, *items: str):
        """Join with separator: .join , apple banana orange"""
        result = separator.join(items)
        BulletinHelper.show_info(result)
        return HookResult()
```

### Example 5: Subcommands

```python
from MSLib import command, BulletinHelper

class GitPlugin(BasePlugin):
    @command("git")
    def git_main(self, param, account):
        """Git command helper"""
        BulletinHelper.show_info(
            "Subcommands:\n"
            "• .git status\n"
            "• .git commit <msg>\n"
            "• .git push"
        )
        return HookResult()
    
    @command("git_status", aliases=["git status"])
    def git_status(self, param, account):
        """Show git status"""
        # Your git status logic
        BulletinHelper.show_info("Status: clean")
        return HookResult()
    
    @command("git_commit", aliases=["git commit"])
    def git_commit(self, param, account, message: str):
        """Commit with message: .git commit "Added feature" """
        # Your git commit logic
        BulletinHelper.show_success(f"Committed: {message}")
        return HookResult()
```

### Example 6: Error Handling

```python
from MSLib import command, BulletinHelper, logger
from base_plugin import HookResult

class SafePlugin(BasePlugin):
    @command("divide")
    def divide_cmd(self, param, account, a: float, b: float):
        """Divide numbers: .divide 10 2"""
        try:
            if b == 0:
                BulletinHelper.show_error("Cannot divide by zero!")
                return HookResult()
            
            result = a / b
            BulletinHelper.show_success(f"{a} ÷ {b} = {result:.2f}")
        except Exception as e:
            logger.error(f"Division error: {e}")
            BulletinHelper.show_error("Calculation failed")
        
        return HookResult()
    
    @command("api")
    def api_cmd(self, param, account, endpoint: str):
        """Call API: .api /users"""
        try:
            # API call here
            BulletinHelper.show_success("API call successful")
        except ConnectionError:
            BulletinHelper.show_error("Network error")
        except TimeoutError:
            BulletinHelper.show_error("Request timeout")
        except Exception as e:
            logger.error(f"API error: {e}")
            BulletinHelper.show_error("Unknown error occurred")
        
        return HookResult()
```

## 🎛️ Advanced Features

### Custom Dispatcher

```python
from MSLib import Dispatcher
from base_plugin import BasePlugin

class MultiPrefixPlugin(BasePlugin):
    def on_plugin_load(self):
        # Create custom dispatcher
        self.cmd = Dispatcher(
            plugin_id="multi_prefix",
            prefix="!",  # Use ! instead of .
            commands_priority=100
        )
        
        # Register commands
        @self.cmd.register_command("test")
        def test(param, account):
            BulletinHelper.show_info("Custom prefix command!")
            return HookResult()
```

### Dynamic Prefix Change

```python
from MSLib import command, BulletinHelper, command_dispatcher

class PrefixPlugin(BasePlugin):
    @command("prefix")
    def change_prefix(self, param, account, new_prefix: str):
        """Change command prefix: .prefix !"""
        global command_dispatcher
        
        if command_dispatcher:
            if Dispatcher.validate_prefix(new_prefix):
                command_dispatcher.set_prefix(new_prefix)
                BulletinHelper.show_success(f"Prefix changed to: {new_prefix}")
            else:
                BulletinHelper.show_error("Invalid prefix (must be one character)")
        
        return HookResult()
```

### Command Aliases

```python
@command("calculate", aliases=["calc", "c", "="])
def calculator(self, param, account, expr: str):
    """Calculator with multiple aliases"""
    # Works with: .calculate, .calc, .c, .=
    return HookResult()
```

## 💡 Best Practices

### 1. Always Return HookResult

```python
# ✅ Correct
@command("test")
def test_cmd(self, param, account):
    BulletinHelper.show_info("Test")
    return HookResult()  # Always return

# ❌ Wrong
@command("test")
def test_cmd(self, param, account):
    BulletinHelper.show_info("Test")
    # Missing return - will cause errors
```

### 2. Use Type Hints

```python
# ✅ Good: Clear types
@command("add")
def add(self, param, account, a: int, b: int):
    return HookResult()

# ❌ Bad: No types (all arguments will be strings)
@command("add")
def add(self, param, account, a, b):
    # a and b are strings, not integers!
    return HookResult()
```

### 3. Provide Defaults for Optional Arguments

```python
# ✅ Good
@command("search")
def search(self, param, account, query: str, limit: int = 10):
    # limit defaults to 10 if not provided
    return HookResult()

# Also good
from typing import Optional

@command("search")
def search(self, param, account, query: str, limit: Optional[int] = None):
    limit = limit or 10
    return HookResult()
```

### 4. Validate Input

```python
@command("setage")
def set_age(self, param, account, age: int):
    # Validate
    if age < 0 or age > 150:
        BulletinHelper.show_error("Invalid age")
        return HookResult()
    
    # Process valid input
    self.save_setting("age", age)
    BulletinHelper.show_success(f"Age set to {age}")
    return HookResult()
```

### 5. Use Descriptive Docstrings

```python
# ✅ Good
@command("send")
def send_message(self, param, account, user_id: int, message: str):
    """
    Send a message to a user
    
    Usage: .send 123456789 "Hello!"
    
    Args:
        user_id: Telegram user ID
        message: Message text
    """
    return HookResult()
```

## 🐛 Troubleshooting

### Command Not Working

```python
# Check if command is registered
from MSLib import command_dispatcher, logger

if command_dispatcher:
    if "mycommand" in command_dispatcher.listeners:
        logger.info("Command registered")
    else:
        logger.error("Command not found")
```

### Type Conversion Errors

```python
# Handle invalid types gracefully
@command("calculate")
def calc(self, param, account, a: int, b: int):
    # MSLib automatically converts and raises CannotCastError if invalid
    # You don't need to handle this manually
    result = a + b
    return HookResult()

# User types: .calculate abc def
# MSLib will show error: "Cannot cast 'abc' to int"
```

### Wrong Argument Count

```python
@command("test")
def test(self, param, account, required: str, optional: str = "default"):
    # Required: 1 argument (required)
    # Optional: 1 argument (optional)
    return HookResult()

# .test → Error: "Not enough arguments"
# .test value → OK
# .test value1 value2 → OK
# .test value1 value2 value3 → Error: "Too many arguments"
```

---

**Next:** [Logging & Notifications →](logging-notifications.md)
