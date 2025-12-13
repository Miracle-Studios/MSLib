# UI Components

MSLib provides powerful UI utilities for creating dialogs, alerts, spinners, and managing the user interface.

## 📖 Overview

The UI components include:

- 🎨 **UI Class** - Alert and confirmation dialogs
- ⏳ **Spinner** - Loading dialog context manager
- 🔔 **AlertDialogBuilder** - Custom alert builder
- 📋 **Clipboard** - Copy text to clipboard
- 🔗 **Link Builder** - Create clickable links

## 📚 API Reference

### UI Class

The `UI` class provides static methods for user dialogs.

#### `UI.show_alert(title, message="", callback=None, account=0)`

Show an alert dialog.

**Parameters:**
- `title` (str): Dialog title
- `message` (str): Dialog message (optional)
- `callback` (Callable, optional): Callback when closed
- `account` (int): Account index

**Example:**

```python
from MSLib import UI

# Simple alert
UI.show_alert("Success", "Operation completed!")

# With callback
def on_closed():
    logger.info("Alert closed")

UI.show_alert(
    title="Warning",
    message="Are you sure?",
    callback=on_closed
)
```

**Full Example:**

```python
from MSLib import UI, command
from base_plugin import HookResult

class NotificationPlugin(BasePlugin):
    @command("notify")
    def show_notification(self, param, account, *message_parts: str):
        """Show alert: .notify Hello World!"""
        
        if not message_parts:
            UI.show_alert("Error", "No message provided")
            return HookResult()
        
        message = " ".join(message_parts)
        
        def on_closed():
            logger.info(f"User closed notification: {message}")
        
        UI.show_alert(
            title="📢 Notification",
            message=message,
            callback=on_closed,
            account=account
        )
        
        return HookResult()
```

#### `UI.show_confirm(title, message, positive_button, negative_button, callback, account=0)`

Show a confirmation dialog with two buttons.

**Parameters:**
- `title` (str): Dialog title
- `message` (str): Dialog message
- `positive_button` (str): Text for "Yes" button
- `negative_button` (str): Text for "No" button
- `callback` (Callable): Callback `(confirmed: bool) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import UI, logger

def on_confirm(confirmed):
    if confirmed:
        logger.info("User confirmed")
        # Do something
    else:
        logger.info("User cancelled")

UI.show_confirm(
    title="Delete File",
    message="Are you sure you want to delete this file?",
    positive_button="Delete",
    negative_button="Cancel",
    callback=on_confirm
)
```

**Full Example:**

```python
from MSLib import UI, command, BulletinHelper, JsonDB, CACHE_DIRECTORY
from base_plugin import HookResult
import os

class DataManagerPlugin(BasePlugin):
    def on_plugin_load(self):
        self.db = JsonDB(os.path.join(CACHE_DIRECTORY, "data.json"))
    
    @command("cleardata")
    def clear_data(self, param, account):
        """Clear all data: .cleardata"""
        
        def on_confirm(confirmed):
            if not confirmed:
                BulletinHelper.show_info("Cancelled")
                return
            
            # Clear database
            self.db.clear()
            BulletinHelper.show_success("All data cleared!")
        
        UI.show_confirm(
            title="⚠️ Clear Data",
            message="This will delete all saved data. Continue?",
            positive_button="Clear",
            negative_button="Cancel",
            callback=on_confirm,
            account=account
        )
        
        return HookResult()
    
    @command("reset")
    def reset_settings(self, param, account, setting_name: str = "all"):
        """Reset settings: .reset [all|theme|lang]"""
        
        def on_confirm(confirmed):
            if not confirmed:
                return
            
            if setting_name == "all":
                self.db.clear()
                msg = "All settings reset"
            else:
                self.db.delete(setting_name)
                msg = f"Setting '{setting_name}' reset"
            
            BulletinHelper.show_success(msg)
        
        message = f"Reset {setting_name}?"
        
        UI.show_confirm(
            title="Reset Settings",
            message=message,
            positive_button="Reset",
            negative_button="Cancel",
            callback=on_confirm,
            account=account
        )
        
        return HookResult()
```

### Spinner Class

A context manager for showing loading dialogs.

#### `Spinner(message="Loading...", cancellable=True, account=0)`

**Parameters:**
- `message` (str): Loading message (default: "Loading...")
- `cancellable` (bool): Can user cancel? (default: True)
- `account` (int): Account index

**Methods:**
- `update(message)` - Update spinner message
- `cancel()` - Cancel spinner programmatically

**Example:**

```python
from MSLib import Spinner
import time

# Basic usage
with Spinner("Processing..."):
    time.sleep(2)
    # Do work

# Update message
with Spinner("Starting...") as spinner:
    time.sleep(1)
    spinner.update("Step 1/3...")
    time.sleep(1)
    spinner.update("Step 2/3...")
    time.sleep(1)
    spinner.update("Step 3/3...")
    time.sleep(1)

# Non-cancellable
with Spinner("Critical operation", cancellable=False):
    # User cannot cancel this
    time.sleep(3)
```

**Full Example:**

```python
from MSLib import Spinner, command, BulletinHelper, Requests
from base_plugin import HookResult

class BatchProcessorPlugin(BasePlugin):
    @command("process")
    def process_batch(self, param, account, count: int = 10):
        """Process batch: .process 50"""
        
        if count <= 0 or count > 100:
            BulletinHelper.show_error("Count must be 1-100")
            return HookResult()
        
        results = []
        
        with Spinner(f"Processing 0/{count}...") as spinner:
            for i in range(count):
                # Update progress
                spinner.update(f"Processing {i+1}/{count}...")
                
                # Simulate work
                import time
                time.sleep(0.1)
                
                results.append(f"Item {i+1}")
                
                # Check if cancelled
                if not spinner.is_active():
                    BulletinHelper.show_info("Cancelled by user")
                    return HookResult()
        
        BulletinHelper.show_success(f"Processed {len(results)} items")
        return HookResult()
    
    @command("download")
    def download_files(self, param, account, *file_ids: int):
        """Download files: .download 123 124 125"""
        
        if not file_ids:
            BulletinHelper.show_error("No file IDs provided")
            return HookResult()
        
        total = len(file_ids)
        downloaded = 0
        
        with Spinner(f"Downloading 0/{total}...", cancellable=True) as spinner:
            for i, file_id in enumerate(file_ids):
                spinner.update(f"Downloading file {i+1}/{total}...")
                
                # Download file (example)
                try:
                    # download_file_logic(file_id)
                    import time
                    time.sleep(0.5)
                    downloaded += 1
                except Exception as e:
                    logger.error(f"Failed to download {file_id}: {e}")
        
        BulletinHelper.show_success(f"Downloaded {downloaded}/{total} files")
        return HookResult()
```

**Advanced Example with Error Handling:**

```python
from MSLib import Spinner, BulletinHelper, logger
import time

class DataSyncPlugin(BasePlugin):
    @command("sync")
    def sync_data(self, param, account):
        """Sync data with server"""
        
        try:
            with Spinner("Connecting to server...", cancellable=False) as spinner:
                # Phase 1: Connect
                time.sleep(1)
                
                # Phase 2: Upload
                spinner.update("Uploading local changes...")
                upload_count = self._upload_changes()
                time.sleep(1)
                
                # Phase 3: Download
                spinner.update("Downloading remote changes...")
                download_count = self._download_changes()
                time.sleep(1)
                
                # Phase 4: Merge
                spinner.update("Merging data...")
                self._merge_data()
                time.sleep(1)
            
            # Success
            BulletinHelper.show_success(
                f"Sync complete!\n"
                f"↑ Uploaded: {upload_count}\n"
                f"↓ Downloaded: {download_count}"
            )
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            BulletinHelper.show_error(f"Sync failed: {str(e)}")
        
        return HookResult()
    
    def _upload_changes(self):
        # Upload logic
        return 5
    
    def _download_changes(self):
        # Download logic
        return 3
    
    def _merge_data(self):
        # Merge logic
        pass
```

### AlertDialogBuilder

Build custom alert dialogs with multiple buttons.

#### `AlertDialogBuilder(title, message="")`

**Methods:**
- `set_positive_button(text, callback)` - Add positive button
- `set_negative_button(text, callback)` - Add negative button
- `set_neutral_button(text, callback)` - Add neutral button
- `show(account=0)` - Show the dialog

**Example:**

```python
from MSLib import AlertDialogBuilder, BulletinHelper

# Three-button dialog
builder = AlertDialogBuilder(
    title="Save Changes",
    message="You have unsaved changes"
)

def on_save():
    BulletinHelper.show_success("Changes saved")

def on_discard():
    BulletinHelper.show_info("Changes discarded")

def on_cancel():
    BulletinHelper.show_info("Cancelled")

builder.set_positive_button("Save", on_save)
builder.set_negative_button("Discard", on_discard)
builder.set_neutral_button("Cancel", on_cancel)
builder.show()
```

**Full Example:**

```python
from MSLib import AlertDialogBuilder, command, BulletinHelper, JsonDB, CACHE_DIRECTORY
from base_plugin import HookResult
import os

class DocumentEditorPlugin(BasePlugin):
    def on_plugin_load(self):
        self.db = JsonDB(os.path.join(CACHE_DIRECTORY, "documents.json"))
        self.current_doc = None
        self.has_changes = False
    
    @command("newtdoc")
    def new_document(self, param, account):
        """Create new document"""
        
        if self.has_changes:
            # Show save dialog
            self._show_save_dialog(lambda: self._create_new_document())
        else:
            self._create_new_document()
        
        return HookResult()
    
    def _show_save_dialog(self, after_action):
        """Show dialog to save unsaved changes"""
        
        builder = AlertDialogBuilder(
            title="⚠️ Unsaved Changes",
            message="You have unsaved changes. What would you like to do?"
        )
        
        def on_save():
            self._save_document()
            BulletinHelper.show_success("Document saved")
            after_action()
        
        def on_discard():
            self.has_changes = False
            BulletinHelper.show_info("Changes discarded")
            after_action()
        
        def on_cancel():
            BulletinHelper.show_info("Cancelled")
        
        builder.set_positive_button("💾 Save", on_save)
        builder.set_negative_button("🗑️ Discard", on_discard)
        builder.set_neutral_button("❌ Cancel", on_cancel)
        builder.show()
    
    def _create_new_document(self):
        self.current_doc = {"content": "", "created": time.time()}
        self.has_changes = False
        BulletinHelper.show_success("New document created")
    
    def _save_document(self):
        if self.current_doc:
            doc_id = str(int(time.time()))
            self.db.set(doc_id, self.current_doc)
            self.has_changes = False
    
    @command("exportdoc")
    def export_document(self, param, account, doc_id: str):
        """Export document"""
        
        builder = AlertDialogBuilder(
            title="📤 Export Document",
            message="Choose export format:"
        )
        
        def export_txt():
            # Export as TXT
            BulletinHelper.show_success("Exported as TXT")
        
        def export_md():
            # Export as Markdown
            BulletinHelper.show_success("Exported as Markdown")
        
        def export_html():
            # Export as HTML
            BulletinHelper.show_success("Exported as HTML")
        
        builder.set_positive_button("📄 TXT", export_txt)
        builder.set_negative_button("📝 Markdown", export_md)
        builder.set_neutral_button("🌐 HTML", export_html)
        builder.show(account)
        
        return HookResult()
```

### Clipboard Functions

#### `copy_to_clipboard(text, show_bulletin=True)`

Copy text to clipboard.

**Parameters:**
- `text` (str): Text to copy
- `show_bulletin` (bool): Show notification (default: True)

**Example:**

```python
from MSLib import copy_to_clipboard

# Copy with notification
copy_to_clipboard("Hello World!")

# Copy silently
copy_to_clipboard("Secret data", show_bulletin=False)
```

**Full Example:**

```python
from MSLib import copy_to_clipboard, command, BulletinHelper
from base_plugin import HookResult

class ClipboardPlugin(BasePlugin):
    @command("copy")
    def copy_text(self, param, account, *text_parts: str):
        """Copy text: .copy Hello World"""
        
        if not text_parts:
            BulletinHelper.show_error("No text provided")
            return HookResult()
        
        text = " ".join(text_parts)
        copy_to_clipboard(text, show_bulletin=True)
        
        return HookResult()
    
    @command("copyid")
    def copy_chat_id(self, param, account):
        """Copy current chat ID"""
        
        chat_id = param.chat_id
        copy_to_clipboard(str(chat_id))
        BulletinHelper.show_success(f"Chat ID copied: {chat_id}")
        
        return HookResult()
    
    @command("copymsg")
    def copy_message(self, param, account, message_id: int):
        """Copy message text: .copymsg 123"""
        
        # Get message from cache or API
        message_text = self._get_message_text(message_id)
        
        if message_text:
            copy_to_clipboard(message_text)
            BulletinHelper.show_success("Message copied")
        else:
            BulletinHelper.show_error("Message not found")
        
        return HookResult()
    
    def _get_message_text(self, msg_id):
        # Implementation
        return f"Sample message {msg_id}"
```

### Link Builder

#### `link(url, text=None)`

Create a clickable Markdown link.

**Parameters:**
- `url` (str): Link URL
- `text` (str, optional): Link text (default: URL)

**Returns:** Markdown link string

**Example:**

```python
from MSLib import link, BulletinHelper

# URL as text
github_link = link("https://github.com")
# Result: [https://github.com](https://github.com)

# Custom text
github_link = link("https://github.com", "GitHub")
# Result: [GitHub](https://github.com)

# Use in notification
BulletinHelper.show_info(
    f"Visit our {link('https://example.com', 'website')} for more info"
)
```

**Full Example:**

```python
from MSLib import link, command, BulletinHelper
from base_plugin import HookResult

class LinksPlugin(BasePlugin):
    @command("links")
    def show_links(self, param, account):
        """Show useful links"""
        
        links_text = "🔗 **Useful Links**\n\n"
        
        links_text += f"📚 {link('https://docs.example.com', 'Documentation')}\n"
        links_text += f"💬 {link('https://t.me/support', 'Support Chat')}\n"
        links_text += f"🐛 {link('https://github.com/issues', 'Report Bug')}\n"
        links_text += f"⭐ {link('https://github.com/repo', 'GitHub Repo')}\n"
        
        BulletinHelper.show_info(links_text)
        return HookResult()
    
    @command("help")
    def show_help(self, param, account, topic: str = "general"):
        """Show help: .help [topic]"""
        
        help_urls = {
            "general": "https://docs.example.com/general",
            "commands": "https://docs.example.com/commands",
            "api": "https://docs.example.com/api",
            "faq": "https://docs.example.com/faq"
        }
        
        if topic not in help_urls:
            available = ", ".join(help_urls.keys())
            BulletinHelper.show_error(f"Unknown topic. Available: {available}")
            return HookResult()
        
        url = help_urls[topic]
        message = f"📖 Help: {topic.capitalize()}\n\n"
        message += f"Read more: {link(url, 'Documentation')}"
        
        BulletinHelper.show_info(message)
        return HookResult()
```

## 🎯 Complete Usage Examples

### Example 1: Interactive Setup Wizard

```python
from MSLib import UI, Spinner, AlertDialogBuilder, BulletinHelper, JsonDB, CACHE_DIRECTORY
from base_plugin import HookResult
import os

class SetupWizardPlugin(BasePlugin):
    def on_plugin_load(self):
        self.config = JsonDB(os.path.join(CACHE_DIRECTORY, "wizard_config.json"))
    
    @command("setup")
    def run_setup(self, param, account):
        """Run setup wizard: .setup"""
        
        # Check if already configured
        if self.config.get("setup_complete"):
            def on_confirm(confirmed):
                if confirmed:
                    self._start_wizard(account)
            
            UI.show_confirm(
                title="Setup Already Complete",
                message="Run setup wizard again?",
                positive_button="Yes",
                negative_button="No",
                callback=on_confirm,
                account=account
            )
        else:
            self._start_wizard(account)
        
        return HookResult()
    
    def _start_wizard(self, account):
        """Start the setup wizard"""
        
        BulletinHelper.show_info("🧙 Starting Setup Wizard...")
        
        # Step 1: Choose language
        self._step1_language(account)
    
    def _step1_language(self, account):
        """Step 1: Language selection"""
        
        builder = AlertDialogBuilder(
            title="Step 1/3: Language",
            message="Choose your language:"
        )
        
        def choose_en():
            self.config.set("language", "en")
            self._step2_theme(account)
        
        def choose_ru():
            self.config.set("language", "ru")
            self._step2_theme(account)
        
        def choose_es():
            self.config.set("language", "es")
            self._step2_theme(account)
        
        builder.set_positive_button("🇬🇧 English", choose_en)
        builder.set_negative_button("🇷🇺 Русский", choose_ru)
        builder.set_neutral_button("🇪🇸 Español", choose_es)
        builder.show(account)
    
    def _step2_theme(self, account):
        """Step 2: Theme selection"""
        
        builder = AlertDialogBuilder(
            title="Step 2/3: Theme",
            message="Choose your theme:"
        )
        
        def choose_light():
            self.config.set("theme", "light")
            self._step3_notifications(account)
        
        def choose_dark():
            self.config.set("theme", "dark")
            self._step3_notifications(account)
        
        def choose_auto():
            self.config.set("theme", "auto")
            self._step3_notifications(account)
        
        builder.set_positive_button("☀️ Light", choose_light)
        builder.set_negative_button("🌙 Dark", choose_dark)
        builder.set_neutral_button("🔄 Auto", choose_auto)
        builder.show(account)
    
    def _step3_notifications(self, account):
        """Step 3: Notifications"""
        
        def on_confirm(confirmed):
            self.config.set("notifications", confirmed)
            self._finish_setup(account)
        
        UI.show_confirm(
            title="Step 3/3: Notifications",
            message="Enable notifications?",
            positive_button="Enable",
            negative_button="Disable",
            callback=on_confirm,
            account=account
        )
    
    def _finish_setup(self, account):
        """Finish setup"""
        
        with Spinner("Saving configuration...", cancellable=False):
            import time
            time.sleep(1)
            
            self.config.set("setup_complete", True)
            self.config.set("setup_date", int(time.time()))
        
        # Show summary
        lang = self.config.get("language", "en")
        theme = self.config.get("theme", "auto")
        notif = "enabled" if self.config.get("notifications") else "disabled"
        
        summary = (
            "✅ Setup Complete!\n\n"
            f"Language: {lang}\n"
            f"Theme: {theme}\n"
            f"Notifications: {notif}"
        )
        
        UI.show_alert("Setup Complete", summary, account=account)
```

### Example 2: File Manager

```python
from MSLib import UI, Spinner, AlertDialogBuilder, BulletinHelper, copy_to_clipboard
from base_plugin import HookResult
import os

class FileManagerPlugin(BasePlugin):
    @command("fm")
    def file_manager(self, param, account, path: str = "."):
        """File manager: .fm [path]"""
        
        if not os.path.exists(path):
            BulletinHelper.show_error("Path not found")
            return HookResult()
        
        if os.path.isfile(path):
            self._show_file_options(path, account)
        else:
            self._show_dir_contents(path, account)
        
        return HookResult()
    
    def _show_file_options(self, filepath, account):
        """Show file operations"""
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        builder = AlertDialogBuilder(
            title=f"📄 {filename}",
            message=f"Size: {filesize:,} bytes\n\nChoose action:"
        )
        
        def copy_path():
            copy_to_clipboard(filepath)
            BulletinHelper.show_success("Path copied")
        
        def delete_file():
            def on_confirm(confirmed):
                if confirmed:
                    try:
                        os.remove(filepath)
                        BulletinHelper.show_success("File deleted")
                    except Exception as e:
                        BulletinHelper.show_error(f"Failed: {e}")
            
            UI.show_confirm(
                title="Delete File",
                message=f"Delete {filename}?",
                positive_button="Delete",
                negative_button="Cancel",
                callback=on_confirm,
                account=account
            )
        
        def view_file():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # First 1000 chars
                    if len(content) == 1000:
                        content += "\n... (truncated)"
                    BulletinHelper.show_info(f"```\n{content}\n```")
            except Exception as e:
                BulletinHelper.show_error(f"Cannot read: {e}")
        
        builder.set_positive_button("📋 Copy Path", copy_path)
        builder.set_negative_button("🗑️ Delete", delete_file)
        builder.set_neutral_button("👁️ View", view_file)
        builder.show(account)
    
    def _show_dir_contents(self, dirpath, account):
        """Show directory contents"""
        
        try:
            items = os.listdir(dirpath)
            
            if not items:
                BulletinHelper.show_info("Empty directory")
                return
            
            # Count files and dirs
            files = [i for i in items if os.path.isfile(os.path.join(dirpath, i))]
            dirs = [i for i in items if os.path.isdir(os.path.join(dirpath, i))]
            
            msg = f"📁 {os.path.basename(dirpath) or dirpath}\n\n"
            msg += f"Folders: {len(dirs)}\n"
            msg += f"Files: {len(files)}\n\n"
            
            # Show first few items
            for d in dirs[:5]:
                msg += f"📁 {d}/\n"
            
            for f in files[:5]:
                msg += f"📄 {f}\n"
            
            total = len(dirs) + len(files)
            if total > 10:
                msg += f"\n... and {total - 10} more items"
            
            BulletinHelper.show_info(msg)
            
        except Exception as e:
            BulletinHelper.show_error(f"Error: {e}")
```

### Example 3: Progress Tracker

```python
from MSLib import Spinner, UI, BulletinHelper, JsonDB, CACHE_DIRECTORY
from base_plugin import HookResult
import os
import time

class ProgressTrackerPlugin(BasePlugin):
    def on_plugin_load(self):
        self.tasks_db = JsonDB(os.path.join(CACHE_DIRECTORY, "tasks.json"))
    
    @command("addtask")
    def add_task(self, param, account, *task_parts: str):
        """Add task: .addtask Buy groceries"""
        
        if not task_parts:
            BulletinHelper.show_error("Task description required")
            return HookResult()
        
        task_text = " ".join(task_parts)
        tasks = self.tasks_db.get("tasks", [])
        
        task = {
            "id": len(tasks) + 1,
            "text": task_text,
            "done": False,
            "created": int(time.time())
        }
        
        tasks.append(task)
        self.tasks_db.set("tasks", tasks)
        
        BulletinHelper.show_success(f"✅ Task #{task['id']} added")
        return HookResult()
    
    @command("tasks")
    def list_tasks(self, param, account):
        """List all tasks"""
        
        tasks = self.tasks_db.get("tasks", [])
        
        if not tasks:
            BulletinHelper.show_info("No tasks")
            return HookResult()
        
        pending = [t for t in tasks if not t["done"]]
        completed = [t for t in tasks if t["done"]]
        
        msg = "📋 **Task List**\n\n"
        
        if pending:
            msg += "**Pending:**\n"
            for task in pending:
                msg += f"⬜ #{task['id']}: {task['text']}\n"
        
        if completed:
            msg += "\n**Completed:**\n"
            for task in completed:
                msg += f"✅ #{task['id']}: ~~{task['text']}~~\n"
        
        msg += f"\n📊 Progress: {len(completed)}/{len(tasks)}"
        
        BulletinHelper.show_info(msg)
        return HookResult()
    
    @command("completetask")
    def complete_task(self, param, account, task_id: int):
        """Complete task: .completetask 1"""
        
        tasks = self.tasks_db.get("tasks", [])
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if not task:
            BulletinHelper.show_error(f"Task #{task_id} not found")
            return HookResult()
        
        if task["done"]:
            BulletinHelper.show_info("Task already completed")
            return HookResult()
        
        # Mark as done
        task["done"] = True
        task["completed_at"] = int(time.time())
        self.tasks_db.set("tasks", tasks)
        
        BulletinHelper.show_success(f"✅ Task #{task_id} completed!")
        
        # Check if all tasks done
        if all(t["done"] for t in tasks):
            UI.show_alert(
                "🎉 Congratulations!",
                "All tasks completed!",
                account=account
            )
        
        return HookResult()
    
    @command("cleartasks")
    def clear_tasks(self, param, account):
        """Clear all tasks"""
        
        tasks = self.tasks_db.get("tasks", [])
        
        if not tasks:
            BulletinHelper.show_info("No tasks to clear")
            return HookResult()
        
        def on_confirm(confirmed):
            if not confirmed:
                return
            
            with Spinner("Clearing tasks...", cancellable=False):
                time.sleep(0.5)
                self.tasks_db.set("tasks", [])
            
            BulletinHelper.show_success("All tasks cleared")
        
        pending = len([t for t in tasks if not t["done"]])
        message = f"Clear {len(tasks)} tasks ({pending} pending)?"
        
        UI.show_confirm(
            title="Clear Tasks",
            message=message,
            positive_button="Clear",
            negative_button="Cancel",
            callback=on_confirm,
            account=account
        )
        
        return HookResult()
```

## 💡 Best Practices

### 1. Always Use Callbacks

```python
# ✅ Good
def on_confirm(confirmed):
    if confirmed:
        # User confirmed
        do_action()

UI.show_confirm("Title", "Message", "Yes", "No", on_confirm)

# ❌ Bad
UI.show_confirm("Title", "Message", "Yes", "No", None)  # No callback
```

### 2. Provide Clear Messages

```python
# ✅ Good
UI.show_alert(
    title="Success",
    message="Your data has been saved successfully!"
)

# ❌ Bad
UI.show_alert("Done", "OK")  # Too vague
```

### 3. Use Spinner for Long Operations

```python
# ✅ Good
with Spinner("Processing data..."):
    long_operation()

# ❌ Bad
long_operation()  # No feedback to user
```

### 4. Make Spinners Cancellable When Possible

```python
# ✅ Good (user can cancel)
with Spinner("Downloading...", cancellable=True) as spinner:
    for item in items:
        if not spinner.is_active():
            break
        download(item)

# ⚠️ Only use cancellable=False for critical operations
with Spinner("Saving...", cancellable=False):
    save_critical_data()
```

### 5. Update Spinner Progress

```python
# ✅ Good
with Spinner("Starting...") as spinner:
    for i, item in enumerate(items):
        spinner.update(f"Processing {i+1}/{len(items)}...")
        process(item)

# ❌ Bad
with Spinner("Processing..."):
    # No progress updates
    for item in items:
        process(item)
```

## 🐛 Troubleshooting

### Dialog Not Showing

```python
# Make sure account index is correct
UI.show_alert("Test", "Message", account=0)  # First account

# Check if dialog is created properly
builder = AlertDialogBuilder("Title", "Message")
builder.set_positive_button("OK", lambda: None)
builder.show(account=0)
```

### Spinner Not Updating

```python
# ✅ Use update() method
with Spinner("Starting...") as spinner:
    spinner.update("Step 1...")
    time.sleep(1)
    spinner.update("Step 2...")

# ❌ Don't reassign
with Spinner("Starting...") as spinner:
    spinner = Spinner("Step 1...")  # Wrong!
```

### Callback Not Called

```python
# ✅ Define callback before using
def on_confirm(confirmed):
    print(f"User confirmed: {confirmed}")

UI.show_confirm("Title", "Msg", "Yes", "No", on_confirm)

# ❌ Don't use lambda without storing reference
UI.show_confirm("Title", "Msg", "Yes", "No", lambda x: print(x))  # May not work
```

---

**Next:** [Parsers →](parsers.md)
