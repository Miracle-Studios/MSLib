# Parsers

MSLib provides powerful parsers for converting between HTML, Markdown, and Telegram entities.

## 📖 Overview

The parser system includes:

- 📝 **HTML** - Parse and generate HTML with Telegram entities
- ✍️ **Markdown** - Parse and generate Markdown
- 🔤 **TLEntityType** - Telegram entity types enum
- 📋 **RawEntity** - Entity representation class

## 📚 API Reference

### HTML Class

The `HTML` class converts between HTML and Telegram entities.

#### `HTML.parse(html_text)`

Parse HTML text to Telegram entities.

**Parameters:**
- `html_text` (str): HTML formatted text

**Returns:** Tuple `(text, entities)`
- `text` (str): Plain text
- `entities` (List[RawEntity]): List of formatting entities

**Supported Tags:**
- `<b>`, `<strong>` - Bold
- `<i>`, `<em>` - Italic
- `<u>` - Underline
- `<s>`, `<strike>`, `<del>` - Strikethrough
- `<code>` - Monospace
- `<pre>` - Code block
- `<a href="...">` - Links
- `<blockquote>` - Quote

**Example:**

```python
from MSLib import HTML, logger

# Simple formatting
html = "<b>Bold</b> and <i>italic</i> text"
text, entities = HTML.parse(html)

logger.info(f"Text: {text}")  # "Bold and italic text"
logger.info(f"Entities: {len(entities)}")  # 2

# Links
html = 'Visit <a href="https://example.com">our website</a>'
text, entities = HTML.parse(html)
# text: "Visit our website"
# entities: [RawEntity(type=TEXT_LINK, offset=6, length=11, url="https://example.com")]

# Complex formatting
html = """
<b>Title</b>
<i>Description with <u>underlined</u> word</i>
<code>code_example()</code>
<a href="https://github.com">GitHub</a>
"""
text, entities = HTML.parse(html)

# Use entities with Telegram API
for entity in entities:
    logger.info(f"{entity.type} at {entity.offset}:{entity.offset + entity.length}")
```

**Full Example:**

```python
from MSLib import HTML, BulletinHelper, command
from base_plugin import HookResult

class HTMLFormatterPlugin(BasePlugin):
    @command("format")
    def format_text(self, param, account, *html_parts: str):
        """Format text with HTML: .format <b>Hello</b> <i>World</i>"""
        
        if not html_parts:
            help_text = (
                "**HTML Formatting Guide:**\n\n"
                "`<b>Bold</b>` - **Bold**\n"
                "`<i>Italic</i>` - *Italic*\n"
                "`<u>Underline</u>` - __Underline__\n"
                "`<s>Strike</s>` - ~~Strike~~\n"
                "`<code>Code</code>` - `Code`\n"
                "`<a href=\"url\">Link</a>` - [Link](url)\n\n"
                "**Example:**\n"
                "`.format <b>Hello</b> <i>World</i>`"
            )
            BulletinHelper.show_info(help_text)
            return HookResult()
        
        html_text = " ".join(html_parts)
        
        try:
            text, entities = HTML.parse(html_text)
            
            # Show parsed result
            result = f"**Parsed Text:**\n{text}\n\n"
            result += f"**Entities:** {len(entities)}\n"
            
            for i, entity in enumerate(entities, 1):
                entity_text = text[entity.offset:entity.offset + entity.length]
                result += f"{i}. {entity.type}: '{entity_text}'\n"
            
            BulletinHelper.show_info(result)
            
        except Exception as e:
            BulletinHelper.show_error(f"Parse error: {e}")
        
        return HookResult()
    
    @command("htmlpreview")
    def preview_html(self, param, account, *html_parts: str):
        """Preview HTML rendering"""
        
        html_text = " ".join(html_parts)
        
        try:
            text, entities = HTML.parse(html_text)
            
            # Convert back to Markdown for preview
            markdown = HTML.unparse(text, entities)
            
            preview = (
                "**HTML Preview:**\n\n"
                f"**Original HTML:**\n`{html_text}`\n\n"
                f"**Rendered:**\n{markdown}\n\n"
                f"**Plain Text:**\n{text}"
            )
            
            BulletinHelper.show_info(preview)
            
        except Exception as e:
            BulletinHelper.show_error(f"Error: {e}")
        
        return HookResult()
```

#### `HTML.unparse(text, entities)`

Generate HTML from text and entities.

**Parameters:**
- `text` (str): Plain text
- `entities` (List[RawEntity]): Formatting entities

**Returns:** HTML formatted string

**Example:**

```python
from MSLib import HTML, RawEntity, TLEntityType

# Create entities manually
text = "Hello World!"
entities = [
    RawEntity(type=TLEntityType.BOLD, offset=0, length=5),  # "Hello"
    RawEntity(type=TLEntityType.ITALIC, offset=6, length=6)  # "World!"
]

html = HTML.unparse(text, entities)
# Result: "<b>Hello</b> <i>World!</i>"

# With links
text = "Visit GitHub"
entities = [
    RawEntity(
        type=TLEntityType.TEXT_LINK,
        offset=6,
        length=6,
        url="https://github.com"
    )
]

html = HTML.unparse(text, entities)
# Result: 'Visit <a href="https://github.com">GitHub</a>'
```

**Full Example:**

```python
from MSLib import HTML, RawEntity, TLEntityType, BulletinHelper, command
from base_plugin import HookResult

class EntityBuilderPlugin(BasePlugin):
    @command("build")
    def build_formatted_text(self, param, account):
        """Build formatted text programmatically"""
        
        # Build text
        parts = []
        entities = []
        offset = 0
        
        # Add bold title
        title = "Important Notice"
        parts.append(title)
        entities.append(RawEntity(
            type=TLEntityType.BOLD,
            offset=offset,
            length=len(title)
        ))
        offset += len(title)
        
        # Add newline
        parts.append("\n\n")
        offset += 2
        
        # Add italic description
        desc = "This is an important message with "
        parts.append(desc)
        offset += len(desc)
        
        # Add underlined word
        word = "emphasized"
        parts.append(word)
        entities.append(RawEntity(
            type=TLEntityType.UNDERLINE,
            offset=offset,
            length=len(word)
        ))
        offset += len(word)
        
        # Add rest
        rest = " content."
        parts.append(rest)
        offset += len(rest)
        
        # Add code example
        parts.append("\n\n")
        offset += 2
        
        code = "example_code()"
        parts.append(code)
        entities.append(RawEntity(
            type=TLEntityType.CODE,
            offset=offset,
            length=len(code)
        ))
        offset += len(code)
        
        # Add link
        parts.append("\n\n")
        offset += 2
        
        link_text = "Read more"
        parts.append(link_text)
        entities.append(RawEntity(
            type=TLEntityType.TEXT_LINK,
            offset=offset,
            length=len(link_text),
            url="https://example.com"
        ))
        
        # Combine
        full_text = "".join(parts)
        
        # Generate HTML
        html = HTML.unparse(full_text, entities)
        
        result = (
            "**Built Text:**\n\n"
            f"**Plain:**\n{full_text}\n\n"
            f"**HTML:**\n`{html}`\n\n"
            f"**Entities:** {len(entities)}"
        )
        
        BulletinHelper.show_info(result)
        return HookResult()
```

### Markdown Class

The `Markdown` class converts between Markdown and Telegram entities.

#### `Markdown.parse(markdown_text)`

Parse Markdown to Telegram entities.

**Parameters:**
- `markdown_text` (str): Markdown formatted text

**Returns:** Tuple `(text, entities)`

**Supported Syntax:**
- `**bold**`, `__bold__` - Bold
- `*italic*`, `_italic_` - Italic
- `` `code` `` - Monospace
- ``` ```code block``` ``` - Code block
- `[text](url)` - Links
- `~~strikethrough~~` - Strikethrough

**Example:**

```python
from MSLib import Markdown, logger

# Basic formatting
md = "**Bold** and *italic* text"
text, entities = Markdown.parse(md)

logger.info(f"Text: {text}")  # "Bold and italic text"
logger.info(f"Entities: {len(entities)}")  # 2

# Links
md = "Visit [GitHub](https://github.com)"
text, entities = Markdown.parse(md)
# text: "Visit GitHub"
# entities: [RawEntity(type=TEXT_LINK, offset=6, length=6, url="https://github.com")]

# Code
md = "Use `function()` to call"
text, entities = Markdown.parse(md)

# Multiple formatting
md = """
**Title**
*Description with ~~strike~~ text*
`code_example()`
[Link](https://example.com)
"""
text, entities = Markdown.parse(md)
```

**Full Example:**

```python
from MSLib import Markdown, BulletinHelper, command, copy_to_clipboard
from base_plugin import HookResult

class MarkdownPlugin(BasePlugin):
    @command("md")
    def parse_markdown(self, param, account, *md_parts: str):
        """Parse Markdown: .md **Hello** *World*"""
        
        if not md_parts:
            help_text = (
                "**Markdown Guide:**\n\n"
                "`**Bold**` - **Bold**\n"
                "`*Italic*` - *Italic*\n"
                "`` `Code` `` - `Code`\n"
                "`~~Strike~~` - ~~Strike~~\n"
                "`[Text](url)` - [Text](url)\n\n"
                "**Example:**\n"
                "`.md **Hello** *World*`"
            )
            BulletinHelper.show_info(help_text)
            return HookResult()
        
        md_text = " ".join(md_parts)
        
        try:
            text, entities = Markdown.parse(md_text)
            
            result = f"**Parsed Markdown:**\n\n{text}\n\n"
            result += f"**Entities:** {len(entities)}\n"
            
            for entity in entities:
                entity_text = text[entity.offset:entity.offset + entity.length]
                result += f"• {entity.type}: '{entity_text}'\n"
            
            BulletinHelper.show_info(result)
            
        except Exception as e:
            BulletinHelper.show_error(f"Parse error: {e}")
        
        return HookResult()
    
    @command("mdconvert")
    def convert_markdown(self, param, account, format: str, *text_parts: str):
        """Convert Markdown to format: .mdconvert html **Hello**"""
        
        if format not in ["html", "plain"]:
            BulletinHelper.show_error("Format must be 'html' or 'plain'")
            return HookResult()
        
        md_text = " ".join(text_parts)
        
        try:
            text, entities = Markdown.parse(md_text)
            
            if format == "html":
                from MSLib import HTML
                result = HTML.unparse(text, entities)
                copy_to_clipboard(result)
                BulletinHelper.show_success(f"HTML copied:\n`{result}`")
            else:
                copy_to_clipboard(text)
                BulletinHelper.show_success(f"Plain text copied:\n{text}")
            
        except Exception as e:
            BulletinHelper.show_error(f"Conversion error: {e}")
        
        return HookResult()
```

#### `Markdown.unparse(text, entities)`

Generate Markdown from text and entities.

**Parameters:**
- `text` (str): Plain text
- `entities` (List[RawEntity]): Formatting entities

**Returns:** Markdown formatted string

**Example:**

```python
from MSLib import Markdown, RawEntity, TLEntityType

# Create entities
text = "Hello World!"
entities = [
    RawEntity(type=TLEntityType.BOLD, offset=0, length=5),  # "Hello"
    RawEntity(type=TLEntityType.ITALIC, offset=6, length=6)  # "World!"
]

md = Markdown.unparse(text, entities)
# Result: "**Hello** *World!*"

# With links
text = "Visit GitHub"
entities = [
    RawEntity(
        type=TLEntityType.TEXT_LINK,
        offset=6,
        length=6,
        url="https://github.com"
    )
]

md = Markdown.unparse(text, entities)
# Result: "Visit [GitHub](https://github.com)"
```

### TLEntityType Enum

Entity types for Telegram formatting.

**Available Types:**

```python
from MSLib import TLEntityType

# Text formatting
TLEntityType.BOLD           # Bold text
TLEntityType.ITALIC         # Italic text
TLEntityType.UNDERLINE      # Underlined text
TLEntityType.STRIKETHROUGH  # Strikethrough text
TLEntityType.CODE           # Monospace code
TLEntityType.PRE            # Code block

# Links
TLEntityType.TEXT_LINK      # Hyperlink
TLEntityType.TEXT_URL       # URL without custom text
TLEntityType.MENTION        # @username mention
TLEntityType.HASHTAG        # #hashtag
TLEntityType.CASHTAG        # $TICKER

# Special
TLEntityType.EMAIL          # Email address
TLEntityType.PHONE          # Phone number
TLEntityType.BOT_COMMAND    # /command
TLEntityType.BLOCKQUOTE     # Quote block
```

**Example:**

```python
from MSLib import TLEntityType, RawEntity, HTML

# Use entity types
text = "Hello @user with #hashtag"
entities = [
    RawEntity(type=TLEntityType.BOLD, offset=0, length=5),
    RawEntity(type=TLEntityType.MENTION, offset=6, length=5),
    RawEntity(type=TLEntityType.HASHTAG, offset=17, length=8)
]

html = HTML.unparse(text, entities)
```

### RawEntity Class

Represents a formatting entity.

#### `RawEntity(type, offset, length, url=None, user_id=None, language=None)`

**Parameters:**
- `type` (TLEntityType): Entity type
- `offset` (int): Start position in text
- `length` (int): Length of entity
- `url` (str, optional): For TEXT_LINK entities
- `user_id` (int, optional): For MENTION entities
- `language` (str, optional): For PRE entities (code language)

**Example:**

```python
from MSLib import RawEntity, TLEntityType

# Bold entity
entity = RawEntity(
    type=TLEntityType.BOLD,
    offset=0,
    length=5
)

# Link entity
link_entity = RawEntity(
    type=TLEntityType.TEXT_LINK,
    offset=10,
    length=7,
    url="https://example.com"
)

# Code block with language
code_entity = RawEntity(
    type=TLEntityType.PRE,
    offset=20,
    length=50,
    language="python"
)

# Mention entity
mention_entity = RawEntity(
    type=TLEntityType.MENTION,
    offset=5,
    length=10,
    user_id=123456789
)
```

## 🎯 Complete Usage Examples

### Example 1: Rich Text Editor

```python
from MSLib import HTML, Markdown, RawEntity, TLEntityType, BulletinHelper, command
from base_plugin import HookResult

class RichTextEditorPlugin(BasePlugin):
    @command("edit")
    def edit_text(self, param, account, mode: str, *text_parts: str):
        """Edit text: .edit html <b>Hello</b> or .edit md **Hello**"""
        
        if mode not in ["html", "md"]:
            BulletinHelper.show_error("Mode must be 'html' or 'md'")
            return HookResult()
        
        input_text = " ".join(text_parts)
        
        try:
            # Parse based on mode
            if mode == "html":
                text, entities = HTML.parse(input_text)
                output_html = HTML.unparse(text, entities)
                output_md = Markdown.unparse(text, entities)
            else:  # md
                text, entities = Markdown.parse(input_text)
                output_html = HTML.unparse(text, entities)
                output_md = Markdown.unparse(text, entities)
            
            # Show both formats
            result = (
                f"**Plain Text:**\n{text}\n\n"
                f"**HTML:**\n`{output_html}`\n\n"
                f"**Markdown:**\n`{output_md}`\n\n"
                f"**Entities:** {len(entities)}"
            )
            
            BulletinHelper.show_info(result)
            
        except Exception as e:
            BulletinHelper.show_error(f"Error: {e}")
        
        return HookResult()
    
    @command("entities")
    def show_entities(self, param, account, format: str, *text_parts: str):
        """Show entities: .entities html <b>Hello</b>"""
        
        if format not in ["html", "md"]:
            BulletinHelper.show_error("Format must be 'html' or 'md'")
            return HookResult()
        
        input_text = " ".join(text_parts)
        
        try:
            # Parse
            if format == "html":
                text, entities = HTML.parse(input_text)
            else:
                text, entities = Markdown.parse(input_text)
            
            # Show detailed entity info
            result = f"**Text:** {text}\n\n**Entities ({len(entities)}):**\n\n"
            
            for i, entity in enumerate(entities, 1):
                entity_text = text[entity.offset:entity.offset + entity.length]
                
                result += f"**{i}. {entity.type}**\n"
                result += f"  • Position: {entity.offset}:{entity.offset + entity.length}\n"
                result += f"  • Length: {entity.length}\n"
                result += f"  • Text: '{entity_text}'\n"
                
                if entity.url:
                    result += f"  • URL: {entity.url}\n"
                if entity.language:
                    result += f"  • Language: {entity.language}\n"
                
                result += "\n"
            
            BulletinHelper.show_info(result)
            
        except Exception as e:
            BulletinHelper.show_error(f"Error: {e}")
        
        return HookResult()
```

### Example 2: Format Converter

```python
from MSLib import HTML, Markdown, BulletinHelper, command, copy_to_clipboard
from base_plugin import HookResult

class FormatConverterPlugin(BasePlugin):
    @command("convert")
    def convert(self, param, account, from_format: str, to_format: str, *text: str):
        """Convert formats: .convert html md <b>Hello</b>"""
        
        if from_format not in ["html", "md", "plain"]:
            BulletinHelper.show_error("from_format must be: html, md, plain")
            return HookResult()
        
        if to_format not in ["html", "md", "plain"]:
            BulletinHelper.show_error("to_format must be: html, md, plain")
            return HookResult()
        
        input_text = " ".join(text)
        
        try:
            # Parse input
            if from_format == "html":
                plain_text, entities = HTML.parse(input_text)
            elif from_format == "md":
                plain_text, entities = Markdown.parse(input_text)
            else:  # plain
                plain_text = input_text
                entities = []
            
            # Generate output
            if to_format == "html":
                output = HTML.unparse(plain_text, entities)
            elif to_format == "md":
                output = Markdown.unparse(plain_text, entities)
            else:  # plain
                output = plain_text
            
            # Copy to clipboard
            copy_to_clipboard(output)
            
            # Show result
            result = (
                f"**Conversion: {from_format.upper()} → {to_format.upper()}**\n\n"
                f"**Input:**\n`{input_text}`\n\n"
                f"**Output:**\n`{output}`\n\n"
                "✅ Copied to clipboard"
            )
            
            BulletinHelper.show_success(result)
            
        except Exception as e:
            BulletinHelper.show_error(f"Conversion failed: {e}")
        
        return HookResult()
    
    @command("strip")
    def strip_formatting(self, param, account, format: str, *text: str):
        """Remove formatting: .strip html <b>Hello</b>"""
        
        if format not in ["html", "md"]:
            BulletinHelper.show_error("Format must be 'html' or 'md'")
            return HookResult()
        
        input_text = " ".join(text)
        
        try:
            # Parse and get plain text
            if format == "html":
                plain_text, _ = HTML.parse(input_text)
            else:
                plain_text, _ = Markdown.parse(input_text)
            
            copy_to_clipboard(plain_text)
            
            BulletinHelper.show_success(
                f"**Stripped Text:**\n{plain_text}\n\n"
                "✅ Copied to clipboard"
            )
            
        except Exception as e:
            BulletinHelper.show_error(f"Error: {e}")
        
        return HookResult()
```

### Example 3: Entity Builder

```python
from MSLib import RawEntity, TLEntityType, HTML, Markdown, BulletinHelper, command
from base_plugin import HookResult

class EntityBuilderPlugin(BasePlugin):
    @command("buildmsg")
    def build_message(self, param, account):
        """Build a formatted message programmatically"""
        
        # Build message parts
        parts = []
        entities = []
        current_offset = 0
        
        # Add bold header
        header = "📢 Announcement"
        parts.append(header)
        entities.append(RawEntity(
            type=TLEntityType.BOLD,
            offset=current_offset,
            length=len(header)
        ))
        current_offset += len(header) + 2
        parts.append("\n\n")
        
        # Add description
        desc = "This is an important update about "
        parts.append(desc)
        current_offset += len(desc)
        
        # Add italic emphasized word
        emphasized = "new features"
        parts.append(emphasized)
        entities.append(RawEntity(
            type=TLEntityType.ITALIC,
            offset=current_offset,
            length=len(emphasized)
        ))
        current_offset += len(emphasized)
        
        parts.append(" in our application.")
        current_offset += len(" in our application.") + 2
        parts.append("\n\n")
        
        # Add code example
        code = "update_app()"
        parts.append(code)
        entities.append(RawEntity(
            type=TLEntityType.CODE,
            offset=current_offset,
            length=len(code)
        ))
        current_offset += len(code) + 2
        parts.append("\n\n")
        
        # Add link
        link_text = "Read full changelog"
        parts.append(link_text)
        entities.append(RawEntity(
            type=TLEntityType.TEXT_LINK,
            offset=current_offset,
            length=len(link_text),
            url="https://example.com/changelog"
        ))
        
        # Combine
        full_text = "".join(parts)
        
        # Generate both formats
        html = HTML.unparse(full_text, entities)
        md = Markdown.unparse(full_text, entities)
        
        # Show result
        result = (
            "**Built Message:**\n\n"
            f"{md}\n\n"
            f"**HTML Version:**\n`{html}`\n\n"
            f"**Entities:** {len(entities)}"
        )
        
        BulletinHelper.show_info(result)
        return HookResult()
    
    @command("addentity")
    def add_entity(self, param, account, entity_type: str, start: int, length: int, text: str):
        """Add entity to text: .addentity bold 0 5 "Hello World" """
        
        # Map string to enum
        type_map = {
            "bold": TLEntityType.BOLD,
            "italic": TLEntityType.ITALIC,
            "code": TLEntityType.CODE,
            "underline": TLEntityType.UNDERLINE,
            "strike": TLEntityType.STRIKETHROUGH
        }
        
        if entity_type not in type_map:
            BulletinHelper.show_error(
                f"Unknown type. Available: {', '.join(type_map.keys())}"
            )
            return HookResult()
        
        # Create entity
        entity = RawEntity(
            type=type_map[entity_type],
            offset=start,
            length=length
        )
        
        # Generate formatted text
        html = HTML.unparse(text, [entity])
        md = Markdown.unparse(text, [entity])
        
        result = (
            f"**Entity Added:**\n\n"
            f"Type: {entity_type}\n"
            f"Position: {start}:{start + length}\n"
            f"Text: '{text[start:start + length]}'\n\n"
            f"**HTML:** `{html}`\n"
            f"**Markdown:** `{md}`"
        )
        
        BulletinHelper.show_info(result)
        return HookResult()
```

## 💡 Best Practices

### 1. Always Handle Parse Errors

```python
# ✅ Good
try:
    text, entities = HTML.parse(html_text)
except Exception as e:
    logger.error(f"Parse error: {e}")
    BulletinHelper.show_error("Invalid HTML")

# ❌ Bad
text, entities = HTML.parse(html_text)  # May crash
```

### 2. Validate Entity Ranges

```python
# ✅ Good
def create_entity(text, offset, length, entity_type):
    if offset < 0 or offset + length > len(text):
        raise ValueError("Entity out of range")
    
    return RawEntity(type=entity_type, offset=offset, length=length)

# ❌ Bad
entity = RawEntity(type=TLEntityType.BOLD, offset=100, length=50)
# Offset may be outside text bounds
```

### 3. Sort Entities by Offset

```python
# ✅ Good
entities.sort(key=lambda e: e.offset)
html = HTML.unparse(text, entities)

# ❌ Bad (unordered entities may cause issues)
html = HTML.unparse(text, unsorted_entities)
```

### 4. Use Correct Entity Types

```python
# ✅ Good
link_entity = RawEntity(
    type=TLEntityType.TEXT_LINK,
    offset=0,
    length=10,
    url="https://example.com"  # URL required for TEXT_LINK
)

# ❌ Bad
link_entity = RawEntity(
    type=TLEntityType.TEXT_LINK,
    offset=0,
    length=10
    # Missing URL!
)
```

## 🐛 Troubleshooting

### Entities Not Applied

```python
# Check entity bounds
text = "Hello"
entity = RawEntity(type=TLEntityType.BOLD, offset=0, length=10)
# length > len(text) - will fail!

# ✅ Fix
entity = RawEntity(type=TLEntityType.BOLD, offset=0, length=len(text))
```

### Nested Formatting Issues

```python
# Some formats don't nest well
# ✅ Good: Separate ranges
entities = [
    RawEntity(type=TLEntityType.BOLD, offset=0, length=5),
    RawEntity(type=TLEntityType.ITALIC, offset=6, length=5)
]

# ⚠️ May have issues: Overlapping
entities = [
    RawEntity(type=TLEntityType.BOLD, offset=0, length=10),
    RawEntity(type=TLEntityType.ITALIC, offset=5, length=10)
]
```

### Invalid HTML/Markdown

```python
# ✅ Handle gracefully
try:
    text, entities = HTML.parse(user_input)
except Exception as e:
    logger.warning(f"Invalid HTML: {e}")
    # Fall back to plain text
    text = user_input
    entities = []
```

---

**Next:** [Utilities →](utilities.md)
