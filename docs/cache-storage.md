# Cache & Storage

MSLib provides robust storage solutions for persisting plugin data, from simple key-value stores to compressed caches.

## 📖 Overview

MSLib offers three storage mechanisms:

- **JsonDB**: Simple key-value database with automatic saving
- **JsonCacheFile**: JSON cache with compression support
- **CacheFile**: Raw binary cache with compression

## 🗄️ JsonDB

Simple key-value database stored as JSON.

### API Reference

#### Constructor

```python
JsonDB(filepath: str)
```

**Parameters:**
- `filepath` (str): Path to JSON file

**Example:**

```python
from MSLib import JsonDB, CACHE_DIRECTORY
import os

db = JsonDB(os.path.join(CACHE_DIRECTORY, "mydata.json"))
```

### Methods

#### `set(key, value)`

Sets a value and automatically saves.

```python
db.set("user_count", 100)
db.set("settings", {"theme": "dark", "lang": "en"})
```

#### `get(key, default=None)`

Gets a value with optional default.

```python
count = db.get("user_count", 0)
settings = db.get("settings", {})
```

#### `save()`

Manually saves to file (usually automatic).

```python
db["custom_key"] = "value"
db.save()
```

#### `reset()`

Clears all data and saves empty database.

```python
db.reset()
```

### Usage Examples

#### Example 1: User Statistics

```python
from MSLib import JsonDB, CACHE_DIRECTORY
import os

class StatsPlugin(BasePlugin):
    def on_plugin_load(self):
        self.db = JsonDB(os.path.join(CACHE_DIRECTORY, "stats.json"))
        
        # Initialize counters
        if "commands_used" not in self.db:
            self.db.set("commands_used", 0)
        if "users" not in self.db:
            self.db.set("users", [])
    
    @command("stats")
    def show_stats(self, param, account):
        total = self.db.get("commands_used", 0)
        users = self.db.get("users", [])
        
        BulletinHelper.show_info(
            f"Commands used: {total}\n"
            f"Unique users: {len(users)}"
        )
        return HookResult()
    
    def track_command(self, user_id):
        # Increment counter
        count = self.db.get("commands_used", 0)
        self.db.set("commands_used", count + 1)
        
        # Track unique users
        users = self.db.get("users", [])
        if user_id not in users:
            users.append(user_id)
            self.db.set("users", users)
```

#### Example 2: Configuration Storage

```python
from MSLib import JsonDB, CACHE_DIRECTORY
import os

class ConfigPlugin(BasePlugin):
    DEFAULT_CONFIG = {
        "api_key": "",
        "endpoint": "https://api.example.com",
        "timeout": 30,
        "debug": False
    }
    
    def on_plugin_load(self):
        self.config = JsonDB(os.path.join(CACHE_DIRECTORY, "config.json"))
        
        # Load with defaults
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config.set(key, value)
    
    def get_config(self, key):
        return self.config.get(key, self.DEFAULT_CONFIG.get(key))
    
    def update_config(self, key, value):
        self.config.set(key, value)
        logger.info(f"Config updated: {key} = {value}")
```

#### Example 3: Message History

```python
from MSLib import JsonDB, CACHE_DIRECTORY
import os
from datetime import datetime

class HistoryPlugin(BasePlugin):
    def on_plugin_load(self):
        self.history = JsonDB(os.path.join(CACHE_DIRECTORY, "history.json"))
        
        if "messages" not in self.history:
            self.history.set("messages", [])
    
    def add_message(self, user_id, text):
        messages = self.history.get("messages", [])
        messages.append({
            "user_id": user_id,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 messages
        if len(messages) > 100:
            messages = messages[-100:]
        
        self.history.set("messages", messages)
    
    def get_recent_messages(self, limit=10):
        messages = self.history.get("messages", [])
        return messages[-limit:]
```

## 📦 JsonCacheFile

JSON cache with compression and lazy loading.

### API Reference

#### Constructor

```python
JsonCacheFile(
    filename: str,
    default: Any,
    read_on_init: bool = True,
    compress: bool = False
)
```

**Parameters:**
- `filename` (str): Cache filename (automatically placed in CACHE_DIRECTORY)
- `default` (Any): Default value if file doesn't exist
- `read_on_init` (bool): Read file on creation
- `compress` (bool): Enable zlib compression

**Example:**

```python
from MSLib import JsonCacheFile

cache = JsonCacheFile(
    filename="mycache.json",
    default={"items": [], "count": 0},
    compress=True
)
```

### Attributes

#### `json_content`

Current cached data (dict or any JSON-serializable type).

```python
cache.json_content["items"].append("new_item")
cache.json_content["count"] += 1
```

### Methods

#### `read()`

Loads data from file.

```python
cache.read()
```

#### `write()`

Saves data to file.

```python
cache.json_content["updated"] = True
cache.write()
```

#### `wipe()`

Resets to default value and saves.

```python
cache.wipe()
```

### Usage Examples

#### Example 1: Response Cache

```python
from MSLib import JsonCacheFile
import time

class APIPlugin(BasePlugin):
    def on_plugin_load(self):
        self.cache = JsonCacheFile(
            filename="api_cache.json",
            default={"responses": {}, "timestamps": {}},
            compress=True
        )
    
    def get_cached_response(self, key, max_age=300):
        """Get cached response if not expired"""
        responses = self.cache.json_content.get("responses", {})
        timestamps = self.cache.json_content.get("timestamps", {})
        
        if key in responses:
            age = time.time() - timestamps.get(key, 0)
            if age < max_age:
                logger.info(f"Cache hit for {key}")
                return responses[key]
        
        return None
    
    def cache_response(self, key, response):
        """Cache API response"""
        if "responses" not in self.cache.json_content:
            self.cache.json_content["responses"] = {}
        if "timestamps" not in self.cache.json_content:
            self.cache.json_content["timestamps"] = {}
        
        self.cache.json_content["responses"][key] = response
        self.cache.json_content["timestamps"][key] = time.time()
        self.cache.write()
        
        logger.info(f"Cached response for {key}")
```

#### Example 2: Session Data

```python
from MSLib import JsonCacheFile

class SessionPlugin(BasePlugin):
    def on_plugin_load(self):
        self.sessions = JsonCacheFile(
            filename="sessions.json",
            default={"active": {}, "history": []},
            read_on_init=True
        )
    
    def create_session(self, user_id, data):
        """Create new session"""
        self.sessions.json_content["active"][str(user_id)] = {
            "data": data,
            "created": time.time()
        }
        self.sessions.write()
    
    def end_session(self, user_id):
        """End and archive session"""
        user_key = str(user_id)
        if user_key in self.sessions.json_content["active"]:
            session = self.sessions.json_content["active"].pop(user_key)
            self.sessions.json_content["history"].append(session)
            self.sessions.write()
```

#### Example 3: Compressed Large Dataset

```python
from MSLib import JsonCacheFile

class DataPlugin(BasePlugin):
    def on_plugin_load(self):
        # Large dataset with compression
        self.data = JsonCacheFile(
            filename="large_data.json",
            default={"records": []},
            compress=True  # Save disk space
        )
    
    def add_record(self, record):
        """Add record to dataset"""
        self.data.json_content["records"].append(record)
        
        # Only write periodically to reduce I/O
        if len(self.data.json_content["records"]) % 100 == 0:
            self.data.write()
            logger.info("Data auto-saved (100 records)")
    
    def on_plugin_unload(self):
        """Save on exit"""
        self.data.write()
        logger.info("Final data save")
```

## 💾 CacheFile

Raw binary cache for non-JSON data.

### API Reference

#### Constructor

```python
CacheFile(
    filename: str,
    read_on_init: bool = True,
    compress: bool = False
)
```

**Parameters:**
- `filename` (str): Cache filename
- `read_on_init` (bool): Read on creation
- `compress` (bool): Enable compression

### Attributes

#### `content`

Binary content (bytes).

```python
cache.content = b"raw binary data"
```

### Methods

Same as JsonCacheFile: `read()`, `write()`, `delete()`

### Usage Examples

#### Example 1: Image Cache

```python
from MSLib import CacheFile

class ImagePlugin(BasePlugin):
    def on_plugin_load(self):
        self.image_cache = CacheFile(
            filename="avatar.jpg",
            read_on_init=False,
            compress=False  # Don't compress images
        )
    
    def cache_image(self, image_bytes):
        """Cache downloaded image"""
        self.image_cache.content = image_bytes
        self.image_cache.write()
    
    def get_cached_image(self):
        """Get cached image"""
        if os.path.exists(self.image_cache.path):
            self.image_cache.read()
            return self.image_cache.content
        return None
```

#### Example 2: Binary Protocol Cache

```python
from MSLib import CacheFile
import struct

class ProtocolPlugin(BasePlugin):
    def on_plugin_load(self):
        self.proto_cache = CacheFile(
            filename="protocol.bin",
            compress=True
        )
    
    def save_packet(self, packet_id, data):
        """Save binary packet"""
        # Pack as binary: ID (4 bytes) + length (4 bytes) + data
        packed = struct.pack(">II", packet_id, len(data)) + data
        self.proto_cache.content = packed
        self.proto_cache.write()
    
    def load_packet(self):
        """Load binary packet"""
        self.proto_cache.read()
        if self.proto_cache.content:
            packet_id, length = struct.unpack(">II", self.proto_cache.content[:8])
            data = self.proto_cache.content[8:8+length]
            return packet_id, data
        return None, None
```

## 🎯 Comparison Table

| Feature | JsonDB | JsonCacheFile | CacheFile |
|---------|--------|---------------|-----------|
| **Data Type** | JSON (dict-like) | JSON (any) | Binary |
| **Auto-save** | Yes (on `set()`) | No (manual `write()`) | No (manual `write()`) |
| **Compression** | No | Optional | Optional |
| **Best For** | Settings, configs | Cached API responses | Images, binary data |
| **Lazy Loading** | No | Yes | Yes |
| **Default Value** | No | Yes | No |

## 💡 Best Practices

### 1. Use Correct Storage Type

```python
# ✅ Good: JsonDB for simple key-value
settings = JsonDB("settings.json")
settings.set("theme", "dark")

# ✅ Good: JsonCacheFile for cached data
cache = JsonCacheFile("cache.json", default={}, compress=True)

# ✅ Good: CacheFile for binary
image_cache = CacheFile("image.jpg", compress=False)

# ❌ Bad: JsonDB for large datasets (no compression)
# ❌ Bad: CacheFile for JSON (manual parsing)
```

### 2. Always Use CACHE_DIRECTORY

```python
from MSLib import CACHE_DIRECTORY
import os

# ✅ Correct
db_path = os.path.join(CACHE_DIRECTORY, "data.json")
db = JsonDB(db_path)

# ❌ Wrong - relative path may fail
db = JsonDB("data.json")
```

### 3. Handle Missing Data

```python
# ✅ Good: Always provide defaults
count = db.get("count", 0)
items = cache.json_content.get("items", [])

# ❌ Bad: Assume data exists
count = db["count"]  # KeyError if missing
```

### 4. Batch Writes for Performance

```python
# ✅ Good: Batch updates
for i in range(100):
    cache.json_content["items"].append(i)
cache.write()  # Single write

# ❌ Bad: Write in loop
for i in range(100):
    cache.json_content["items"].append(i)
    cache.write()  # 100 writes!
```

### 5. Compression for Large Data

```python
# ✅ Good: Compress large datasets
cache = JsonCacheFile(
    "large_data.json",
    default={"records": []},
    compress=True  # Saves disk space
)

# ✅ Good: Don't compress small configs
config = JsonCacheFile(
    "config.json",
    default={},
    compress=False  # Faster access
)
```

## 🐛 Troubleshooting

### Permission Errors

```python
# Wrap in try-except
try:
    db.set("key", "value")
except PermissionError as e:
    logger.error(f"Cannot write to database: {e}")
    BulletinHelper.show_error("Failed to save data")
```

### Corrupted Cache

```python
# Reset cache if corrupted
try:
    cache.read()
except (json.JSONDecodeError, Exception) as e:
    logger.warning(f"Cache corrupted, resetting: {e}")
    cache.wipe()
```

### Large File Performance

```python
# Use compression for large files
cache = JsonCacheFile(
    "big_data.json",
    default={"data": []},
    compress=True  # Reduces file size 60-80%
)

# Lazy load - don't read on init
cache = JsonCacheFile(
    "huge_data.json",
    default={},
    read_on_init=False  # Load only when needed
)
```

---

**Next:** [Commands System →](commands.md)
