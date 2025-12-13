# Requests API

MSLib provides a simplified wrapper around Telegram's API for common operations like fetching users, chats, messages, and moderation actions.

## 📖 Overview

The `Requests` class offers static methods for:

- 🔍 Fetching users, chats, and messages
- 🔎 Searching messages
- 🗑️ Deleting messages
- 🔨 Moderation (ban/unban)
- ⏱️ Slowmode control
- 👥 Participant management

All methods support callbacks for async operations and multi-account support.

## 📚 API Reference

### Core Methods

#### `send(request, callback=None, account=0)`

Send a raw TL request.

**Parameters:**
- `request` (TLObject): Telegram TL request object
- `callback` (Callable, optional): Callback function `(response, error) -> None`
- `account` (int): Account index (default: 0)

**Example:**

```python
from MSLib import Requests
from org.telegram.tgnet import TLRPC

# Create request
request = TLRPC.TL_messages_getDialogs()
request.offset_date = 0
request.offset_id = 0
request.offset_peer = TLRPC.TL_inputPeerEmpty()
request.limit = 100

# Send request
def on_response(response, error):
    if error:
        logger.error(f"Request failed: {error}")
    else:
        logger.info(f"Got {len(response.dialogs)} dialogs")

Requests.send(request, callback=on_response)
```

### User & Chat Methods

#### `get_user(user_id, callback, account=0)`

Fetch user information.

**Parameters:**
- `user_id` (int): Telegram user ID
- `callback` (Callable): Callback `(user, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, logger

def on_user_loaded(user, error):
    if error:
        logger.error(f"Failed to load user: {error}")
        return
    
    if user:
        logger.info(f"User: {user.first_name} {user.last_name}")
        logger.info(f"Username: @{user.username}")
        logger.info(f"Premium: {user.premium}")

Requests.get_user(123456789, on_user_loaded)
```

**Full Example with UI:**

```python
from MSLib import Requests, BulletinHelper, command
from base_plugin import HookResult

class UserInfoPlugin(BasePlugin):
    @command("userinfo")
    def get_user_info(self, param, account, user_id: int):
        """Get user info: .userinfo 123456789"""
        
        def on_user(user, error):
            if error:
                BulletinHelper.show_error(f"Failed to load user: {error}")
                return
            
            if user:
                info = f"👤 **{user.first_name or ''}** {user.last_name or ''}\n"
                
                if user.username:
                    info += f"📱 @{user.username}\n"
                
                info += f"🆔 ID: `{user.id}`\n"
                
                if user.premium:
                    info += "⭐ Premium User\n"
                
                if user.bot:
                    info += "🤖 Bot Account\n"
                
                if user.verified:
                    info += "✅ Verified\n"
                
                BulletinHelper.show_info(info)
        
        Requests.get_user(user_id, on_user, account)
        return HookResult()
```

#### `get_chat(chat_id, callback, account=0)`

Fetch chat/channel information.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `callback` (Callable): Callback `(chat, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_chat_loaded(chat, error):
    if error:
        BulletinHelper.show_error(f"Failed to load chat: {error}")
        return
    
    if chat:
        info = f"💬 {chat.title}\n"
        info += f"👥 Members: {chat.participants_count}\n"
        
        if hasattr(chat, 'username') and chat.username:
            info += f"🔗 @{chat.username}\n"
        
        BulletinHelper.show_info(info)

Requests.get_chat(-1001234567890, on_chat_loaded)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class ChatInfoPlugin(BasePlugin):
    @command("chatinfo")
    def get_chat_info(self, param, account, chat_id: int):
        """Get chat info: .chatinfo -1001234567890"""
        
        def on_chat(chat, error):
            if error:
                BulletinHelper.show_error(f"Error: {error}")
                return
            
            if not chat:
                BulletinHelper.show_error("Chat not found")
                return
            
            # Build info message
            lines = [f"💬 **{chat.title}**"]
            
            if hasattr(chat, 'username') and chat.username:
                lines.append(f"🔗 t.me/{chat.username}")
            
            lines.append(f"🆔 ID: `{chat.id}`")
            
            if hasattr(chat, 'participants_count'):
                lines.append(f"👥 Members: {chat.participants_count:,}")
            
            if hasattr(chat, 'about') and chat.about:
                lines.append(f"📝 {chat.about[:100]}")
            
            # Channel-specific
            if hasattr(chat, 'broadcast') and chat.broadcast:
                lines.append("📢 Channel")
            elif hasattr(chat, 'megagroup') and chat.megagroup:
                lines.append("👥 Supergroup")
            
            if hasattr(chat, 'verified') and chat.verified:
                lines.append("✅ Verified")
            
            BulletinHelper.show_info("\n".join(lines))
        
        Requests.get_chat(chat_id, on_chat, account)
        return HookResult()
```

### Message Methods

#### `get_message(channel_id, message_id, callback, account=0)`

Fetch a specific message from a channel.

**Parameters:**
- `channel_id` (int): Channel ID (positive number, not negative)
- `message_id` (int): Message ID
- `callback` (Callable): Callback `(message, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_message_loaded(message, error):
    if error:
        BulletinHelper.show_error(f"Failed to load message: {error}")
        return
    
    if message:
        text = message.message if hasattr(message, 'message') else "No text"
        BulletinHelper.show_info(f"Message: {text}")

# Channel ID: -1001234567890 → use 1234567890 (positive)
Requests.get_message(1234567890, 123, on_message_loaded)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class MessageFetcherPlugin(BasePlugin):
    @command("getmsg")
    def get_message_cmd(self, param, account, channel_id: int, msg_id: int):
        """Fetch message: .getmsg 1234567890 123"""
        
        def on_message(msg, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
                return
            
            if not msg:
                BulletinHelper.show_error("Message not found")
                return
            
            # Extract message info
            info_lines = [f"📨 **Message {msg.id}**"]
            
            if hasattr(msg, 'message') and msg.message:
                info_lines.append(f"📝 {msg.message[:200]}")
            
            if hasattr(msg, 'date'):
                from datetime import datetime
                date = datetime.fromtimestamp(msg.date)
                info_lines.append(f"🕒 {date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if hasattr(msg, 'views') and msg.views:
                info_lines.append(f"👁️ Views: {msg.views:,}")
            
            if hasattr(msg, 'forwards') and msg.forwards:
                info_lines.append(f"↗️ Forwards: {msg.forwards:,}")
            
            BulletinHelper.show_info("\n".join(info_lines))
        
        # Convert negative channel ID to positive
        if channel_id < 0:
            channel_id = abs(channel_id) - 1000000000000
        
        Requests.get_message(channel_id, msg_id, on_message, account)
        return HookResult()
```

#### `search_messages(peer_id, query, callback, limit=100, offset_id=0, filter_type=None, account=0)`

Search messages in a chat.

**Parameters:**
- `peer_id` (int): Chat/channel ID
- `query` (str): Search query
- `callback` (Callable): Callback `(results, error) -> None`
- `limit` (int): Max results (default: 100)
- `offset_id` (int): Pagination offset
- `filter_type` (Any): Message filter type
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_search_results(results, error):
    if error:
        BulletinHelper.show_error(f"Search failed: {error}")
        return
    
    if results and hasattr(results, 'messages'):
        count = len(results.messages)
        BulletinHelper.show_info(f"Found {count} messages")
        
        for msg in results.messages[:5]:  # Show first 5
            if hasattr(msg, 'message'):
                logger.info(f"Message: {msg.message}")

Requests.search_messages(
    peer_id=-1001234567890,
    query="hello",
    callback=on_search_results,
    limit=50
)
```

**Full Example with Pagination:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class SearchPlugin(BasePlugin):
    @command("search")
    def search_cmd(self, param, account, query: str, limit: int = 20):
        """Search messages: .search "hello world" 50"""
        
        # Get current chat ID
        chat_id = param.chat_id  # You need to get this from context
        
        def on_results(results, error):
            if error:
                BulletinHelper.show_error(f"Search error: {error}")
                return
            
            if not results or not hasattr(results, 'messages'):
                BulletinHelper.show_info("No messages found")
                return
            
            messages = results.messages
            total = len(messages)
            
            if total == 0:
                BulletinHelper.show_info(f"No results for '{query}'")
                return
            
            # Format results
            result_text = f"🔍 Found {total} messages for '{query}':\n\n"
            
            for i, msg in enumerate(messages[:10], 1):  # Show top 10
                if hasattr(msg, 'message') and msg.message:
                    preview = msg.message[:50]
                    if len(msg.message) > 50:
                        preview += "..."
                    result_text += f"{i}. {preview}\n"
            
            if total > 10:
                result_text += f"\n... and {total - 10} more"
            
            BulletinHelper.show_info(result_text)
        
        Requests.search_messages(
            peer_id=chat_id,
            query=query,
            callback=on_results,
            limit=limit,
            account=account
        )
        
        return HookResult()
```

### Moderation Methods

#### `delete_messages(message_ids, peer_id, callback=None, revoke=True, account=0)`

Delete messages.

**Parameters:**
- `message_ids` (List[int]): List of message IDs to delete
- `peer_id` (int): Chat ID
- `callback` (Callable, optional): Callback function
- `revoke` (bool): Delete for all users (default: True)
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_deleted(result, error):
    if error:
        BulletinHelper.show_error(f"Delete failed: {error}")
    else:
        BulletinHelper.show_success("Messages deleted")

# Delete multiple messages
message_ids = [123, 124, 125]
Requests.delete_messages(
    message_ids=message_ids,
    peer_id=-1001234567890,
    callback=on_deleted,
    revoke=True  # Delete for everyone
)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult
from typing import List

class ModeratorPlugin(BasePlugin):
    @command("del")
    def delete_cmd(self, param, account, *msg_ids: int):
        """Delete messages: .del 123 124 125"""
        
        if not msg_ids:
            BulletinHelper.show_error("Specify message IDs")
            return HookResult()
        
        chat_id = param.chat_id
        
        def on_delete(result, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
            else:
                count = len(msg_ids)
                BulletinHelper.show_success(f"Deleted {count} message(s)")
        
        Requests.delete_messages(
            message_ids=list(msg_ids),
            peer_id=chat_id,
            callback=on_delete,
            revoke=True,
            account=account
        )
        
        return HookResult()
    
    @command("purge")
    def purge_cmd(self, param, account, from_id: int, to_id: int):
        """Delete range: .purge 100 150"""
        
        if to_id < from_id:
            BulletinHelper.show_error("Invalid range")
            return HookResult()
        
        if to_id - from_id > 100:
            BulletinHelper.show_error("Max 100 messages at once")
            return HookResult()
        
        # Generate ID list
        msg_ids = list(range(from_id, to_id + 1))
        chat_id = param.chat_id
        
        def on_purge(result, error):
            if error:
                BulletinHelper.show_error(f"Purge failed: {error}")
            else:
                BulletinHelper.show_success(
                    f"Purged {len(msg_ids)} messages"
                )
        
        Requests.delete_messages(
            message_ids=msg_ids,
            peer_id=chat_id,
            callback=on_purge,
            account=account
        )
        
        return HookResult()
```

#### `ban(chat_id, peer_id, until_date=None, callback=None, account=0)`

Ban a user from a chat.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `peer_id` (int): User ID to ban
- `until_date` (int, optional): Unix timestamp (None = permanent)
- `callback` (Callable, optional): Callback function
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper
import time

def on_banned(result, error):
    if error:
        BulletinHelper.show_error(f"Ban failed: {error}")
    else:
        BulletinHelper.show_success("User banned")

# Permanent ban
Requests.ban(
    chat_id=-1001234567890,
    peer_id=123456789,
    callback=on_banned
)

# Temporary ban (24 hours)
until = int(time.time()) + 86400
Requests.ban(
    chat_id=-1001234567890,
    peer_id=123456789,
    until_date=until,
    callback=on_banned
)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult
import time

class BanPlugin(BasePlugin):
    @command("ban")
    def ban_user(self, param, account, user_id: int, duration: int = 0):
        """Ban user: .ban 123456789 [hours]"""
        
        chat_id = param.chat_id
        
        # Calculate until_date
        until_date = None
        if duration > 0:
            until_date = int(time.time()) + (duration * 3600)
        
        def on_ban(result, error):
            if error:
                BulletinHelper.show_error(f"Ban failed: {error}")
                return
            
            if duration > 0:
                msg = f"User banned for {duration} hour(s)"
            else:
                msg = "User banned permanently"
            
            BulletinHelper.show_success(msg)
        
        Requests.ban(
            chat_id=chat_id,
            peer_id=user_id,
            until_date=until_date,
            callback=on_ban,
            account=account
        )
        
        return HookResult()
    
    @command("kick")
    def kick_user(self, param, account, user_id: int):
        """Kick user (ban + unban): .kick 123456789"""
        
        chat_id = param.chat_id
        
        # First ban
        def on_banned(result, error):
            if error:
                BulletinHelper.show_error(f"Kick failed: {error}")
                return
            
            # Then unban
            def on_unbanned(result2, error2):
                if error2:
                    BulletinHelper.show_error(f"Unban failed: {error2}")
                else:
                    BulletinHelper.show_success("User kicked")
            
            Requests.unban(chat_id, user_id, on_unbanned, account)
        
        Requests.ban(chat_id, user_id, callback=on_banned, account=account)
        return HookResult()
```

#### `unban(chat_id, target_peer_id, callback=None, account=0)`

Unban a user.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `target_peer_id` (int): User ID to unban
- `callback` (Callable, optional): Callback function
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_unbanned(result, error):
    if error:
        BulletinHelper.show_error(f"Unban failed: {error}")
    else:
        BulletinHelper.show_success("User unbanned")

Requests.unban(
    chat_id=-1001234567890,
    target_peer_id=123456789,
    callback=on_unbanned
)
```

#### `change_slowmode(chat_id, seconds=0, callback=None, account=0)`

Change slowmode delay.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `seconds` (int): Delay in seconds (0 = disable)
- `callback` (Callable, optional): Callback function
- `account` (int): Account index

**Allowed values:** 0, 10, 30, 60, 300, 900, 3600

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_slowmode_changed(result, error):
    if error:
        BulletinHelper.show_error(f"Failed: {error}")
    else:
        BulletinHelper.show_success("Slowmode updated")

# Enable 30 second slowmode
Requests.change_slowmode(
    chat_id=-1001234567890,
    seconds=30,
    callback=on_slowmode_changed
)

# Disable slowmode
Requests.change_slowmode(
    chat_id=-1001234567890,
    seconds=0,
    callback=on_slowmode_changed
)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class SlowmodePlugin(BasePlugin):
    ALLOWED_DELAYS = [0, 10, 30, 60, 300, 900, 3600]
    
    @command("slowmode")
    def set_slowmode(self, param, account, seconds: int = 0):
        """Set slowmode: .slowmode [0|10|30|60|300|900|3600]"""
        
        if seconds not in self.ALLOWED_DELAYS:
            BulletinHelper.show_error(
                f"Invalid delay. Use: {', '.join(map(str, self.ALLOWED_DELAYS))}"
            )
            return HookResult()
        
        chat_id = param.chat_id
        
        def on_changed(result, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
                return
            
            if seconds == 0:
                BulletinHelper.show_success("Slowmode disabled")
            else:
                mins = seconds // 60 if seconds >= 60 else 0
                secs = seconds % 60
                
                if mins > 0:
                    time_str = f"{mins}m {secs}s" if secs > 0 else f"{mins}m"
                else:
                    time_str = f"{secs}s"
                
                BulletinHelper.show_success(f"Slowmode: {time_str}")
        
        Requests.change_slowmode(
            chat_id=chat_id,
            seconds=seconds,
            callback=on_changed,
            account=account
        )
        
        return HookResult()
```

### Participant Methods

#### `get_chat_participant(chat_id, target_peer_id, callback, account=0)`

Get participant info.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `target_peer_id` (int): User ID
- `callback` (Callable): Callback `(participant, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_participant(participant, error):
    if error:
        BulletinHelper.show_error(f"Failed: {error}")
        return
    
    if participant:
        # Check participant type
        if hasattr(participant, 'participant'):
            p = participant.participant
            
            # Admin
            if hasattr(p, 'admin_rights'):
                BulletinHelper.show_info("User is admin")
            # Banned
            elif hasattr(p, 'banned_rights'):
                BulletinHelper.show_info("User is banned")
            # Regular
            else:
                BulletinHelper.show_info("Regular member")

Requests.get_chat_participant(
    chat_id=-1001234567890,
    target_peer_id=123456789,
    callback=on_participant
)
```

**Full Example:**

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class ParticipantPlugin(BasePlugin):
    @command("whois")
    def check_participant(self, param, account, user_id: int):
        """Check user status: .whois 123456789"""
        
        chat_id = param.chat_id
        
        def on_participant(result, error):
            if error:
                BulletinHelper.show_error(f"Error: {error}")
                return
            
            if not result or not hasattr(result, 'participant'):
                BulletinHelper.show_info("User is not in this chat")
                return
            
            p = result.participant
            info_lines = []
            
            # Check type
            type_name = p.__class__.__name__
            
            if type_name == "TL_channelParticipantCreator":
                info_lines.append("👑 **Creator**")
            elif type_name == "TL_channelParticipantAdmin":
                info_lines.append("⚡ **Admin**")
                
                if hasattr(p, 'admin_rights'):
                    rights = p.admin_rights
                    permissions = []
                    
                    if rights.change_info:
                        permissions.append("📝 Edit info")
                    if rights.delete_messages:
                        permissions.append("🗑️ Delete messages")
                    if rights.ban_users:
                        permissions.append("🔨 Ban users")
                    if rights.invite_users:
                        permissions.append("➕ Invite users")
                    if rights.pin_messages:
                        permissions.append("📌 Pin messages")
                    
                    if permissions:
                        info_lines.append("\n**Permissions:**")
                        info_lines.extend(permissions)
            
            elif type_name == "TL_channelParticipantBanned":
                info_lines.append("🚫 **Banned**")
                
                if hasattr(p, 'banned_rights'):
                    rights = p.banned_rights
                    restrictions = []
                    
                    if rights.view_messages:
                        restrictions.append("Cannot view messages")
                    if rights.send_messages:
                        restrictions.append("Cannot send messages")
                    
                    if restrictions:
                        info_lines.append("\n**Restrictions:**")
                        info_lines.extend(restrictions)
            
            else:
                info_lines.append("👤 **Regular Member**")
            
            # Join date
            if hasattr(p, 'date'):
                from datetime import datetime
                join_date = datetime.fromtimestamp(p.date)
                info_lines.append(f"\n📅 Joined: {join_date.strftime('%Y-%m-%d')}")
            
            BulletinHelper.show_info("\n".join(info_lines))
        
        Requests.get_chat_participant(
            chat_id=chat_id,
            target_peer_id=user_id,
            callback=on_participant,
            account=account
        )
        
        return HookResult()
```

#### `reload_admins(chat_id, account=0)`

Reload admin list for a chat.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

# Reload admin list
Requests.reload_admins(-1001234567890)
BulletinHelper.show_info("Admin list reloaded")
```

## 🎯 Complete Usage Examples

### Example 1: User Lookup Bot

```python
from MSLib import Requests, command, BulletinHelper
from base_plugin import HookResult

class UserLookupBot(BasePlugin):
    @command("lookup")
    def lookup_user(self, param, account, user_id: int):
        """Complete user lookup: .lookup 123456789"""
        
        def on_user(user, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
                return
            
            if not user:
                BulletinHelper.show_error("User not found")
                return
            
            # Build comprehensive info
            lines = ["👤 **User Information**\n"]
            
            # Name
            name_parts = []
            if user.first_name:
                name_parts.append(user.first_name)
            if user.last_name:
                name_parts.append(user.last_name)
            lines.append(f"**Name:** {' '.join(name_parts)}")
            
            # Username
            if user.username:
                lines.append(f"**Username:** @{user.username}")
            
            # ID
            lines.append(f"**ID:** `{user.id}`")
            
            # Status
            status_emoji = {
                "TL_userStatusOnline": "🟢 Online",
                "TL_userStatusOffline": "⚫ Offline",
                "TL_userStatusRecently": "🟡 Recently",
                "TL_userStatusLastWeek": "🟠 Last week",
                "TL_userStatusLastMonth": "🔴 Last month"
            }
            
            if hasattr(user, 'status'):
                status_type = user.status.__class__.__name__
                lines.append(f"**Status:** {status_emoji.get(status_type, '❓ Unknown')}")
            
            # Special flags
            flags = []
            if user.bot:
                flags.append("🤖 Bot")
            if user.premium:
                flags.append("⭐ Premium")
            if user.verified:
                flags.append("✅ Verified")
            if user.scam:
                flags.append("⚠️ Scam")
            if user.fake:
                flags.append("❌ Fake")
            
            if flags:
                lines.append(f"**Flags:** {', '.join(flags)}")
            
            # Bio
            if hasattr(user, 'about') and user.about:
                lines.append(f"\n**Bio:**\n{user.about}")
            
            BulletinHelper.show_info("\n".join(lines))
        
        Requests.get_user(user_id, on_user, account)
        return HookResult()
```

### Example 2: Chat Management Suite

```python
from MSLib import Requests, command, BulletinHelper, logger
from base_plugin import HookResult
import time

class ChatManager(BasePlugin):
    @command("chatadmin")
    def admin_panel(self, param, account):
        """Show admin panel"""
        BulletinHelper.show_info(
            "🔧 **Admin Commands**\n\n"
            "👥 User Management:\n"
            "• .ban <id> [hours]\n"
            "• .unban <id>\n"
            "• .kick <id>\n\n"
            "🗑️ Message Management:\n"
            "• .del <ids...>\n"
            "• .purge <from> <to>\n\n"
            "⚙️ Chat Settings:\n"
            "• .slowmode <seconds>\n"
            "• .chatinfo\n"
            "• .whois <id>"
        )
        return HookResult()
    
    @command("ban")
    def ban_user(self, param, account, user_id: int, hours: int = 0):
        """Ban user: .ban 123456789 24"""
        chat_id = param.chat_id
        until = int(time.time()) + (hours * 3600) if hours > 0 else None
        
        def on_ban(result, error):
            if error:
                BulletinHelper.show_error(f"❌ Ban failed: {error}")
            else:
                msg = f"✅ User {user_id} banned"
                if hours > 0:
                    msg += f" for {hours}h"
                BulletinHelper.show_success(msg)
        
        Requests.ban(chat_id, user_id, until, on_ban, account)
        return HookResult()
    
    @command("stats")
    def chat_stats(self, param, account):
        """Get chat statistics"""
        chat_id = param.chat_id
        
        def on_chat(chat, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
                return
            
            stats = ["📊 **Chat Statistics**\n"]
            
            if hasattr(chat, 'participants_count'):
                stats.append(f"👥 Members: {chat.participants_count:,}")
            
            if hasattr(chat, 'admins_count'):
                stats.append(f"⚡ Admins: {chat.admins_count}")
            
            if hasattr(chat, 'kicked_count'):
                stats.append(f"🚫 Banned: {chat.kicked_count}")
            
            if hasattr(chat, 'online_count'):
                stats.append(f"🟢 Online: {chat.online_count}")
            
            BulletinHelper.show_info("\n".join(stats))
        
        Requests.get_chat(chat_id, on_chat, account)
        return HookResult()
```

### Example 3: Message Search Engine

```python
from MSLib import Requests, command, BulletinHelper, JsonDB, CACHE_DIRECTORY
from base_plugin import HookResult
import os

class SearchEngine(BasePlugin):
    def on_plugin_load(self):
        self.search_history = JsonDB(
            os.path.join(CACHE_DIRECTORY, "search_history.json")
        )
    
    @command("find")
    def search_messages(self, param, account, *query_words: str):
        """Search messages: .find hello world"""
        
        if not query_words:
            BulletinHelper.show_error("Enter search query")
            return HookResult()
        
        query = " ".join(query_words)
        chat_id = param.chat_id
        
        # Save to history
        history = self.search_history.get("queries", [])
        if query not in history:
            history.append(query)
            if len(history) > 50:  # Keep last 50
                history = history[-50:]
            self.search_history.set("queries", history)
        
        def on_results(results, error):
            if error:
                BulletinHelper.show_error(f"Search error: {error}")
                return
            
            if not results or not hasattr(results, 'messages'):
                BulletinHelper.show_info(f"No results for '{query}'")
                return
            
            messages = results.messages
            total = len(messages)
            
            # Format results
            lines = [f"🔍 **Found {total} results for '{query}'**\n"]
            
            # Group by sender
            senders = {}
            for msg in messages:
                if hasattr(msg, 'from_id'):
                    sender_id = msg.from_id.user_id if hasattr(msg.from_id, 'user_id') else 0
                    senders[sender_id] = senders.get(sender_id, 0) + 1
            
            if senders:
                lines.append("**Top senders:**")
                sorted_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)
                for sender_id, count in sorted_senders[:5]:
                    lines.append(f"• User {sender_id}: {count} messages")
            
            # Show sample messages
            lines.append("\n**Sample messages:**")
            for i, msg in enumerate(messages[:5], 1):
                if hasattr(msg, 'message') and msg.message:
                    preview = msg.message[:60]
                    if len(msg.message) > 60:
                        preview += "..."
                    lines.append(f"{i}. {preview}")
            
            if total > 5:
                lines.append(f"\n... and {total - 5} more results")
            
            BulletinHelper.show_info("\n".join(lines))
        
        BulletinHelper.show_info(f"Searching for '{query}'...")
        
        Requests.search_messages(
            peer_id=chat_id,
            query=query,
            callback=on_results,
            limit=100,
            account=account
        )
        
        return HookResult()
    
    @command("searchhistory")
    def show_history(self, param, account):
        """Show search history"""
        history = self.search_history.get("queries", [])
        
        if not history:
            BulletinHelper.show_info("No search history")
            return HookResult()
        
        lines = ["📜 **Search History**\n"]
        for i, query in enumerate(reversed(history[-10:]), 1):
            lines.append(f"{i}. {query}")
        
        BulletinHelper.show_info("\n".join(lines))
        return HookResult()
```

## 💡 Best Practices

### 1. Always Use Callbacks

```python
# ✅ Good
def on_response(result, error):
    if error:
        handle_error(error)
    else:
        handle_result(result)

Requests.get_user(123, on_response)

# ❌ Bad
Requests.get_user(123, None)  # No error handling
```

### 2. Check for Errors

```python
# ✅ Good
def on_result(result, error):
    if error:
        logger.error(f"Request failed: {error}")
        BulletinHelper.show_error("Operation failed")
        return
    
    # Process result
    if result:
        process(result)

# ❌ Bad
def on_result(result, error):
    # Assuming success - dangerous!
    process(result)
```

### 3. Handle None Results

```python
# ✅ Good
def on_user(user, error):
    if error:
        return
    
    if not user:
        BulletinHelper.show_error("User not found")
        return
    
    # User exists, process it
    show_user_info(user)

# ❌ Bad
def on_user(user, error):
    # Might crash if user is None
    name = user.first_name
```

### 4. Use Multi-Account Support

```python
# ✅ Good
@command("getuser")
def get_user(self, param, account, user_id: int):
    # Use the active account
    Requests.get_user(user_id, callback, account)

# Also good for specific account
Requests.get_user(123, callback, account=1)  # Second account
```

### 5. Validate IDs

```python
# ✅ Good
@command("ban")
def ban_user(self, param, account, user_id: int):
    if user_id <= 0:
        BulletinHelper.show_error("Invalid user ID")
        return HookResult()
    
    Requests.ban(param.chat_id, user_id, callback, account)

# ✅ Good for channel IDs
def get_message(channel_id: int, msg_id: int):
    # Convert negative to positive
    if channel_id < 0:
        channel_id = abs(channel_id) - 1000000000000
    
    Requests.get_message(channel_id, msg_id, callback)
```

## 🐛 Troubleshooting

### Request Fails

```python
def on_response(result, error):
    if error:
        error_str = str(error)
        
        if "FLOOD_WAIT" in error_str:
            logger.warning("Rate limited")
        elif "CHAT_ADMIN_REQUIRED" in error_str:
            BulletinHelper.show_error("Admin rights required")
        elif "USER_NOT_PARTICIPANT" in error_str:
            BulletinHelper.show_error("User not in chat")
        else:
            logger.error(f"Unknown error: {error}")
```

### Network Issues

```python
import time

def retry_request(func, max_retries=3):
    """Retry wrapper for requests"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    return wrapper
```

---

## 🆕 New in v1.2.0

### Message Editing

#### `edit_message(message_object, text, entities=None, markup=None, callback=None, account=0)`

Edit existing message.

**Parameters:**
- `message_object` (MessageObject): Message to edit
- `text` (str): New message text
- `entities` (ArrayList, optional): Text entities
- `markup` (Any, optional): Reply markup
- `callback` (Callable, optional): Callback function
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper
from org.telegram.messenger import MessageObject

def edit_current_message(message_obj: MessageObject):
    """Edit message text"""
    
    new_text = "Updated message content"
    
    def on_edited(response, error):
        if error:
            BulletinHelper.show_error(f"Edit failed: {error}")
        else:
            BulletinHelper.show_success("Message edited!")
    
    Requests.edit_message(
        message_obj,
        new_text,
        callback=on_edited
    )
```

**Full Example:**

```python
from MSLib import Requests, BulletinHelper, command, Inline
from base_plugin import HookResult, BasePlugin

class EditPlugin(BasePlugin):
    @command("editmsg")
    def edit_message_cmd(self, param, account):
        """Edit last message: .editmsg"""
        
        # Get last message
        # (You'll need to implement getting the message object)
        message_obj = self.get_last_message()
        
        if not message_obj:
            BulletinHelper.show_error("No message to edit")
            return HookResult()
        
        # New content
        new_text = "✅ This message has been edited!"
        
        # Optional: Add markup
        markup = Inline.Markup()
        markup.add_row(
            Inline.button("Edited!", url="https://example.com")
        )
        
        def on_edited(response, error):
            if error:
                BulletinHelper.show_error(f"Failed: {error}")
            else:
                BulletinHelper.show_success("Message updated!")
        
        Requests.edit_message(
            message_obj,
            new_text,
            markup=markup.to_tlrpc(),
            callback=on_edited
        )
        
        return HookResult()
```

### Message Forwarding

#### `forward_messages(from_peer, to_peer, message_ids, callback=None, account=0)`

Forward messages between chats.

**Parameters:**
- `from_peer` (int): Source chat/user ID
- `to_peer` (int): Destination chat/user ID
- `message_ids` (List[int]): List of message IDs to forward
- `callback` (Callable, optional): Callback function
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

# Forward single message
Requests.forward_messages(
    from_peer=-1001234567890,  # Source channel
    to_peer=-1009876543210,     # Destination channel
    message_ids=[123],          # Message ID
    callback=lambda r, e: BulletinHelper.show_success("Forwarded!") if not e else None
)

# Forward multiple messages
Requests.forward_messages(
    from_peer=-1001234567890,
    to_peer=123456789,  # To user
    message_ids=[1, 2, 3, 4, 5]
)
```

**Full Example:**

```python
from MSLib import Requests, BulletinHelper, command
from base_plugin import HookResult, BasePlugin

class ForwardPlugin(BasePlugin):
    @command("fwd")
    def forward_cmd(self, param, account, from_chat: int, to_chat: int, *msg_ids: int):
        """Forward messages: .fwd -100123 -100456 1 2 3"""
        
        if not msg_ids:
            BulletinHelper.show_error("No message IDs provided")
            return HookResult()
        
        def on_forwarded(response, error):
            if error:
                BulletinHelper.show_error(f"Forward failed: {error}")
            else:
                count = len(msg_ids)
                BulletinHelper.show_success(
                    f"Forwarded {count} message{'s' if count > 1 else ''}!"
                )
        
        Requests.forward_messages(
            from_peer=from_chat,
            to_peer=to_chat,
            message_ids=list(msg_ids),
            callback=on_forwarded,
            account=account
        )
        
        return HookResult()
```

### Full User Info

#### `get_full_user(user_id, callback, account=0)`

Get complete user information including bio, shared media count, etc.

**Parameters:**
- `user_id` (int): User ID
- `callback` (Callable): Callback function `(result, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_user_info(result, error):
    if error:
        BulletinHelper.show_error(f"Failed: {error}")
        return
    
    # Access full user data
    full_user = result.full_user
    user = result.users.get(0)
    
    info = f"""
    **User Info:**
    Name: {user.first_name}
    Bio: {full_user.about or 'No bio'}
    Photos: {full_user.profile_photo_count}
    Common chats: {full_user.common_chats_count}
    """
    
    BulletinHelper.show_info(info)

Requests.get_full_user(123456789, on_user_info)
```

**Full Example:**

```python
from MSLib import Requests, BulletinHelper, command
from base_plugin import HookResult, BasePlugin

class UserInfoPlugin(BasePlugin):
    @command("userinfo")
    def user_info(self, param, account, user_id: int):
        """Get user info: .userinfo 123456789"""
        
        def on_result(result, error):
            if error:
                BulletinHelper.show_error(f"Failed to get user info: {error}")
                return
            
            try:
                full_user = result.full_user
                user = result.users.get(0)
                
                # Build info message
                info = f"👤 **User Info**\n\n"
                info += f"**Name:** {user.first_name}"
                
                if user.last_name:
                    info += f" {user.last_name}"
                
                if user.username:
                    info += f"\n**Username:** @{user.username}"
                
                if full_user.about:
                    info += f"\n**Bio:** {full_user.about}"
                
                info += f"\n**Photos:** {full_user.profile_photo_count}"
                info += f"\n**Common Chats:** {full_user.common_chats_count}"
                
                if full_user.phone_number:
                    info += f"\n**Phone:** {full_user.phone_number}"
                
                # Check status
                if user.bot:
                    info += "\n\n🤖 **Bot Account**"
                if user.verified:
                    info += "\n✅ **Verified**"
                if user.premium:
                    info += "\n⭐ **Premium**"
                
                BulletinHelper.show_info(info)
                
            except Exception as e:
                BulletinHelper.show_error(f"Error parsing user info: {e}")
        
        Requests.get_full_user(user_id, on_result, account)
        return HookResult()
```

### Full Chat Info

#### `get_full_chat(chat_id, callback, account=0)`

Get complete chat/channel information.

**Parameters:**
- `chat_id` (int): Chat/channel ID
- `callback` (Callable): Callback function `(result, error) -> None`
- `account` (int): Account index

**Example:**

```python
from MSLib import Requests, BulletinHelper

def on_chat_info(result, error):
    if error:
        BulletinHelper.show_error(f"Failed: {error}")
        return
    
    # For channels
    if hasattr(result, 'full_chat'):
        full_chat = result.full_chat
        
        info = f"""
        **Chat Info:**
        About: {full_chat.about}
        Participants: {full_chat.participants_count}
        Admins: {full_chat.admins_count}
        """
        
        BulletinHelper.show_info(info)

Requests.get_full_chat(-1001234567890, on_chat_info)
```

**Full Example:**

```python
from MSLib import Requests, BulletinHelper, command, pluralization_string
from base_plugin import HookResult, BasePlugin

class ChatInfoPlugin(BasePlugin):
    @command("chatinfo")
    def chat_info(self, param, account, chat_id: int = None):
        """Get chat info: .chatinfo or .chatinfo -100123"""
        
        # Use current chat if not specified
        if chat_id is None:
            chat_id = param.peer_id
        
        def on_result(result, error):
            if error:
                BulletinHelper.show_error(f"Failed to get chat info: {error}")
                return
            
            try:
                full_chat = result.full_chat
                
                # Get chat object
                chat = None
                if hasattr(result, 'chats') and result.chats.size() > 0:
                    chat = result.chats.get(0)
                
                # Build info message
                info = "💬 **Chat Info**\n\n"
                
                if chat:
                    info += f"**Title:** {chat.title}\n"
                    
                    if hasattr(chat, 'username') and chat.username:
                        info += f"**Username:** @{chat.username}\n"
                
                if full_chat.about:
                    info += f"**About:** {full_chat.about}\n"
                
                # Participant stats
                if hasattr(full_chat, 'participants_count'):
                    count = full_chat.participants_count
                    forms = ("участник", "участника", "участников")
                    info += f"**Members:** {pluralization_string(count, forms)}\n"
                
                if hasattr(full_chat, 'admins_count'):
                    info += f"**Admins:** {full_chat.admins_count}\n"
                
                if hasattr(full_chat, 'kicked_count'):
                    info += f"**Banned:** {full_chat.kicked_count}\n"
                
                if hasattr(full_chat, 'online_count'):
                    info += f"**Online:** {full_chat.online_count}\n"
                
                # Flags
                flags = []
                if chat:
                    if hasattr(chat, 'verified') and chat.verified:
                        flags.append("✅ Verified")
                    if hasattr(chat, 'scam') and chat.scam:
                        flags.append("⚠️ Scam")
                    if hasattr(chat, 'fake') and chat.fake:
                        flags.append("🚫 Fake")
                    if hasattr(chat, 'megagroup') and chat.megagroup:
                        flags.append("👥 Megagroup")
                    if hasattr(chat, 'broadcast') and chat.broadcast:
                        flags.append("📢 Channel")
                
                if flags:
                    info += f"\n{' '.join(flags)}"
                
                BulletinHelper.show_info(info)
                
            except Exception as e:
                BulletinHelper.show_error(f"Error parsing chat info: {e}")
        
        Requests.get_full_chat(chat_id, on_result, account)
        return HookResult()
```

### Usage Tips

#### Combining Methods

```python
from MSLib import Requests, BulletinHelper

class AdvancedPlugin(BasePlugin):
    @command("copymsgs")
    def copy_messages(self, param, account, from_chat: int, to_chat: int):
        """Copy messages with editing"""
        
        # 1. Search messages in source chat
        def on_search(messages, error):
            if error or not messages:
                BulletinHelper.show_error("No messages found")
                return
            
            # 2. Forward messages
            msg_ids = [msg.getId() for msg in messages[:5]]  # First 5
            
            Requests.forward_messages(
                from_peer=from_chat,
                to_peer=to_chat,
                message_ids=msg_ids,
                callback=on_forwarded
            )
        
        def on_forwarded(response, error):
            if error:
                BulletinHelper.show_error("Forward failed")
                return
            
            BulletinHelper.show_success("Messages copied!")
        
        # Start the chain
        Requests.search_messages(
            peer_id=from_chat,
            query="important",
            callback=on_search,
            limit=5
        )
        
        return HookResult()
```

---

**Next:** [UI Components →](ui-components.md)
