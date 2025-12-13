import copy
import json
import zlib
import html
import base64
import inspect
import logging
import os
import os.path
import sys
import time
import threading
import traceback
import re
from enum import Enum
from html.parser import HTMLParser
from struct import unpack
from contextlib import suppress
from typing import List, Callable, Optional, Any, Union, Dict, Tuple, get_origin, get_args
from urllib.parse import urlencode, parse_qs

from ui.bulletin import BulletinHelper as _BulletinHelper
from ui.settings import Header, Switch, Input, Text, Divider
from ui.alert import AlertDialogBuilder
from base_plugin import BasePlugin, HookResult, MethodHook, HookStrategy
from android_utils import log as _log, run_on_ui_thread
from client_utils import (get_messages_controller, get_last_fragment,
                          send_request, get_account_instance, send_message,
                          get_file_loader, run_on_queue)

from java import cast, dynamic_proxy, jint, jarray, jclass # type: ignore
from java.util import Locale, ArrayList # type: ignore
from java.lang import Long, Integer, String, Boolean # type: ignore
from java.io import File # type: ignore
from org.telegram.tgnet import TLRPC, TLObject # type: ignore
from org.telegram.ui import ChatActivity # type: ignore
from org.telegram.messenger import (R, Utilities, AndroidUtilities, ApplicationLoader, # type: ignore
                                    LocaleController, MessageObject, UserConfig, AccountInstance, FileLoader)
from org.telegram.ui.ActionBar import Theme # type: ignore
from com.exteragram.messenger.plugins import PluginsController # type: ignore
from android.text import SpannableStringBuilder, Spanned, InputType # type: ignore
from android.view import Gravity, View # type: ignore
from android.widget import LinearLayout, FrameLayout, TextView # type: ignore
from android.util import TypedValue # type: ignore
from hook_utils import get_private_field, set_private_field
from org.telegram.ui import ChatActivityContainer, ArticleViewer # type: ignore
from org.telegram.ui.Components.voip import VoIPHelper # type: ignore
from org.telegram.messenger import MediaDataController # type: ignore
from android.view import MotionEvent # type: ignore
from android.app import Activity # type: ignore


__name__ = "MSLib"
__id__ = "MSLib"
__description__ = "MSLib is a powerful plugin development library for ETG Messenger, providing a wide range of utilities and tools to simplify plugin creation and enhance functionality."
__icon__ = "MSMainPack/3"
__author__ = "@MiracleStudios"
__version__ = "1.1"
__min_version__ = "12.0.0"


# ==================== Constants ====================
CACHE_DIRECTORY = None
PLUGINS_DIRECTORY = None
LOCALE = "en"
ALLOWED_ARG_TYPES = (str, int, float, bool, Any)
ALLOWED_ORIGIN = (Union, Optional)
NOT_PREMIUM = 0
TELEGRAM_PREMIUM = 1
MSLIB_GLOBAL_PREMIUM = 2
DEFAULT_AUTOUPDATE_TIMEOUT = "600"
DEFAULT_DISABLE_TIMESTAMP_CHECK = False
DEFAULT_DEBUG_MODE = False
MSLIB_AUTOUPDATE_CHANNEL_ID = -1003314084396
MSLIB_AUTOUPDATE_MSG_ID = 3

def _init_constants():
    global CACHE_DIRECTORY, PLUGINS_DIRECTORY, LOCALE
    if CACHE_DIRECTORY is None:
        CACHE_DIRECTORY = os.path.join(AndroidUtilities.getCacheDir().getAbsolutePath(), "mslib_cache")
    if PLUGINS_DIRECTORY is None:
        PLUGINS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
    try:
        LOCALE = Locale.getDefault().getLanguage()
    except:
        LOCALE = "en"

# ==================== Logging utilities ====================
class CustomLogger(logging.Logger):
    def _log(self, level: int, msg: Any, args: Tuple[Any, ...], exc_info=None, extra=None, stack_info=False, stacklevel=1):
        caller_frame = inspect.stack()[2]
        func_name = caller_frame.function
        
        level_name = logging.getLevelName(level).upper()
        
        prefix_items = [level_name, self.name, func_name]
        prefix_items = filter(lambda i: i, prefix_items)
        prefix_items = [f"[{i}]" for i in prefix_items]
        prefix = " ".join(prefix_items)
        
        try:
            formatted_msg = str(msg) % args if args else str(msg)
        except (TypeError, ValueError):
            formatted_msg = f"{msg} {args}"
        
        _log(f"{prefix} {formatted_msg}")

logging.setLoggerClass(CustomLogger)

def build_log(tag: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(tag)
    logger.setLevel(level)
    return logger

logger = build_log(__name__)

def format_exc() -> str:
    return traceback.format_exc().strip()

def format_exc_from(e: Exception) -> str:
    return "".join(traceback.format_exception(type(e), e, e.__traceback__)).strip()

def format_exc_only(e: Exception) -> str:
    return ''.join(traceback.format_exception_only(type(e), e)).strip()

# ==================== Markdown & HTML parsers ====================
def add_surrogates(text: str) -> str:
    return re.compile(r"[\U00010000-\U0010FFFF]").sub(
        lambda match: "".join(chr(i) for i in unpack("<HH", match.group().encode("utf-16le"))),
        text
    )

def remove_surrogates(text: str) -> str:
    return text.encode("utf-16", "surrogatepass").decode("utf-16")

class TLEntityType(Enum):
    CODE = 'code'
    PRE = 'pre'
    STRIKETHROUGH = 'strikethrough'
    TEXT_LINK = 'text_link'
    BOLD = 'bold'
    ITALIC = 'italic'
    UNDERLINE = 'underline'
    SPOILER = 'spoiler'
    CUSTOM_EMOJI = 'custom_emoji'
    BLOCKQUOTE = 'blockquote'

class RawEntity:
    def __init__(self, type, offset, length, extra=None):
        self.type = type
        self.offset = offset
        self.length = length
        self.extra = extra

class HTMLParser_(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.entities = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append((tag, dict(attrs), len(self.text)))
    
    def handle_data(self, data):
        self.text += data
    
    def handle_endtag(self, tag):
        if not self.tag_stack or self.tag_stack[-1][0] != tag:
            return
        
        tag_name, attrs, start_pos = self.tag_stack.pop()
        length = len(self.text) - start_pos
        
        if length <= 0:
            return
        
        entity_type = None
        extra = None
        
        if tag_name == 'b' or tag_name == 'strong':
            entity_type = TLEntityType.BOLD
        elif tag_name == 'i' or tag_name == 'em':
            entity_type = TLEntityType.ITALIC
        elif tag_name == 'u':
            entity_type = TLEntityType.UNDERLINE
        elif tag_name == 's' or tag_name == 'del' or tag_name == 'strike':
            entity_type = TLEntityType.STRIKETHROUGH
        elif tag_name == 'code':
            entity_type = TLEntityType.CODE
        elif tag_name == 'pre':
            entity_type = TLEntityType.PRE
        elif tag_name == 'a':
            entity_type = TLEntityType.TEXT_LINK
            extra = attrs.get('href', '')
        elif tag_name == 'emoji':
            entity_type = TLEntityType.CUSTOM_EMOJI
            extra = attrs.get('id', '')
        elif tag_name == 'blockquote':
            entity_type = TLEntityType.BLOCKQUOTE
        elif tag_name == 'spoiler':
            entity_type = TLEntityType.SPOILER
        
        if entity_type:
            self.entities.append(RawEntity(entity_type, start_pos, length, extra))

class HTML:
    @staticmethod
    def parse(text: str) -> Tuple[str, List[RawEntity]]:
        parser = HTMLParser_()
        parser.feed(text)
        return add_surrogates(parser.text), parser.entities
    
    @staticmethod
    def unparse(text: str, entities: List[RawEntity]) -> str:
        if not entities:
            return text
        
        result = []
        last_offset = 0
        
        for entity in sorted(entities, key=lambda e: e.offset):
            result.append(text[last_offset:entity.offset])
            
            content = text[entity.offset:entity.offset + entity.length]
            
            if entity.type == TLEntityType.BOLD:
                result.append(f"<b>{content}</b>")
            elif entity.type == TLEntityType.ITALIC:
                result.append(f"<i>{content}</i>")
            elif entity.type == TLEntityType.UNDERLINE:
                result.append(f"<u>{content}</u>")
            elif entity.type == TLEntityType.STRIKETHROUGH:
                result.append(f"<s>{content}</s>")
            elif entity.type == TLEntityType.CODE:
                result.append(f"<code>{content}</code>")
            elif entity.type == TLEntityType.PRE:
                result.append(f"<pre>{content}</pre>")
            elif entity.type == TLEntityType.TEXT_LINK:
                result.append(f'<a href="{entity.extra}">{content}</a>')
            elif entity.type == TLEntityType.CUSTOM_EMOJI:
                result.append(f'<emoji id="{entity.extra}">{content}</emoji>')
            elif entity.type == TLEntityType.BLOCKQUOTE:
                result.append(f"<blockquote>{content}</blockquote>")
            elif entity.type == TLEntityType.SPOILER:
                result.append(f"<spoiler>{content}</spoiler>")
            
            last_offset = entity.offset + entity.length
        
        result.append(text[last_offset:])
        return ''.join(result)

class Markdown:
    BOLD_DELIM = "**"
    ITALIC_DELIM = "_"
    UNDERLINE_DELIM = "__"
    STRIKE_DELIM = "~~"
    SPOILER_DELIM = "||"
    CODE_DELIM = "`"
    PRE_DELIM = "```"
    BLOCKQUOTE_DELIM = ">"
    
    @staticmethod
    def parse(text: str, strict: bool = False) -> Tuple[str, List[RawEntity]]:
        entities = []
        clean_text = text
        offset_shift = 0
        
        import re
        
        # Bold (**text**)
        for match in re.finditer(r'\*\*(.+?)\*\*', text):
            entities.append(RawEntity(
                TLEntityType.BOLD,
                match.start() - offset_shift,
                len(match.group(1))
            ))
            clean_text = clean_text.replace(match.group(0), match.group(1), 1)
            offset_shift += 4
        
        # Italic (*text* or _text_)
        for match in re.finditer(r'(?<!\*)\*([^*]+)\*(?!\*)', clean_text):
            entities.append(RawEntity(
                TLEntityType.ITALIC,
                match.start(),
                len(match.group(1))
            ))
        
        # Strikethrough (~~text~~)
        for match in re.finditer(r'~~(.+?)~~', clean_text):
            entities.append(RawEntity(
                TLEntityType.STRIKETHROUGH,
                match.start(),
                len(match.group(1))
            ))
        
        # Code (`text`)
        for match in re.finditer(r'`([^`]+)`', clean_text):
            entities.append(RawEntity(
                TLEntityType.CODE,
                match.start(),
                len(match.group(1))
            ))
        
        # Spoiler (||text||)
        for match in re.finditer(r'\|\|(.+?)\|\|', clean_text):
            entities.append(RawEntity(
                TLEntityType.SPOILER,
                match.start(),
                len(match.group(1))
            ))
        
        return add_surrogates(clean_text), entities
    
    @staticmethod
    def unparse(text: str, entities: List[RawEntity]) -> str:
        if not entities:
            return text
        
        result = []
        last_offset = 0
        
        for entity in sorted(entities, key=lambda e: e.offset):
            result.append(text[last_offset:entity.offset])
            
            content = text[entity.offset:entity.offset + entity.length]
            
            if entity.type == TLEntityType.BOLD:
                result.append(f"**{content}**")
            elif entity.type == TLEntityType.ITALIC:
                result.append(f"*{content}*")
            elif entity.type == TLEntityType.UNDERLINE:
                result.append(f"__{content}__")
            elif entity.type == TLEntityType.STRIKETHROUGH:
                result.append(f"~~{content}~~")
            elif entity.type == TLEntityType.CODE:
                result.append(f"`{content}`")
            elif entity.type == TLEntityType.PRE:
                result.append(f"```{content}```")
            elif entity.type == TLEntityType.TEXT_LINK:
                result.append(f"[{content}]({entity.extra})")
            elif entity.type == TLEntityType.SPOILER:
                result.append(f"||{content}||")
            else:
                result.append(content)
            
            last_offset = entity.offset + entity.length
        
        result.append(text[last_offset:])
        return ''.join(result)

def link(text: str, url: str) -> str:
    return f'<a href="{url}">{text}</a>'

# ==================== Working with Java collections ====================
def arraylist_to_list(jarray: Optional[ArrayList]) -> Optional[List[Any]]:
    return [jarray.get(i) for i in range(jarray.size())] if jarray else None

def list_to_arraylist(python_list: Optional[List[Any]], int_auto_convert: bool = True) -> Optional[ArrayList]:
    if not python_list:
        return None
    
    arraylist = ArrayList()
    for item in python_list:
        if int_auto_convert and isinstance(item, int):
            arraylist.add(Integer(item))
        else:
            arraylist.add(item)
    return arraylist

# ==================== Command system ====================
class CannotCastError(Exception):
    pass

class WrongArgumentAmountError(Exception):
    pass

class MissingRequiredArguments(Exception):
    pass

class InvalidTypeError(Exception):
    pass

class ArgSpec:
    def __init__(self, name, annotation, kind, default=None, is_optional=False):
        self.name = name
        self.annotation = annotation
        self.kind = kind
        self.default = default if default is not None else inspect.Parameter.empty
        self.is_optional = is_optional
    
    @classmethod
    def from_parameter(cls, param):
        is_optional = False
        annotation = param.annotation
        
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                if type(None) in annotation.__args__:
                    is_optional = True
                    non_none_args = [arg for arg in annotation.__args__ if arg is not type(None)]
                    if len(non_none_args) == 1:
                        annotation = non_none_args[0]
        
        return cls(
            name=param.name,
            annotation=annotation if annotation != inspect.Parameter.empty else Any,
            kind=param.kind,
            default=param.default,
            is_optional=is_optional
        )

class Command:
    def __init__(self, func, name, args=None, subcommands=None, error_handler=None):
        self.func = func
        self.name = name
        self.args = args if args is not None else []
        self.subcommands = subcommands if subcommands is not None else {}
        self.error_handler = error_handler
    
    def subcommand(self, name: str):
        def decorator(func: Callable):
            cmd = create_command(func, name)
            self.subcommands[name] = cmd
            return func
        return decorator
    
    def register_error_handler(self, func: Callable[[Any, int, Exception], HookResult]):
        self.error_handler = func
        return func

def is_allowed_type(arg_type) -> bool:
    if arg_type in ALLOWED_ARG_TYPES:
        return True
    
    if arg_type is type(None):
        return True
    
    origin = get_origin(arg_type)
    if origin in ALLOWED_ORIGIN:
        return all(is_allowed_type(t) for t in get_args(arg_type))
    return False

def create_command(func: Callable, name: str) -> Command:
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())
    return_type = signature.return_annotation
    
    if len(parameters) < 2:
        raise MissingRequiredArguments("Command must have 'param' variable as first argument and 'account' variable as second argument")
    
    args = [ArgSpec.from_parameter(param) for param in parameters]
    
    for index, arg in enumerate(args):
        if arg.kind == inspect.Parameter.VAR_POSITIONAL:
            if index != len(args) - 1:
                raise InvalidTypeError(f"VAR_POSITIONAL argument must be the last argument")
            if arg.annotation != str and arg.annotation != Any:
                raise InvalidTypeError(f"VAR_POSITIONAL argument must be str or Any, got {arg.annotation}")
        elif not is_allowed_type(arg.annotation):
            raise InvalidTypeError(f"Unsupported argument type: {arg.annotation}")
    
    if return_type != HookResult:
        return_type_name = "NoneType" if return_type == inspect.Parameter.empty else return_type
        raise InvalidTypeError(f"Command function must return {HookResult} object, got {return_type_name}")
    
    return Command(func=func, name=name, args=args)

def cast_arg(arg: str, target_type: type):
    if target_type == str or target_type == Any:
        return arg
    elif target_type == int:
        return int(arg)
    elif target_type == float:
        return float(arg)
    elif target_type == bool:
        lower = arg.lower()
        if lower in ('true', '1', 'yes', 'on'):
            return True
        elif lower in ('false', '0', 'no', 'off'):
            return False
        raise CannotCastError(f"Cannot cast '{arg}' to bool")
    else:
        raise CannotCastError(f"Unsupported type: {target_type}")

def smart_cast(arg, annotation):
    if annotation in ALLOWED_ARG_TYPES:
        try:
            return cast_arg(arg, annotation)
        except Exception:
            raise CannotCastError("Cannot cast '{}' to {}".format(arg, annotation))
    
    if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
        for arg_type in annotation.__args__:
            if arg_type is type(None):
                continue
            try:
                return cast_arg(arg, arg_type)
            except Exception:
                continue
        raise CannotCastError("Cannot cast '{}' to any of Union types".format(arg))
    
    raise CannotCastError("Unsupported annotation: {}".format(annotation))

def parse_args(raw_args: List[str], command_args: List[ArgSpec]) -> Tuple[Any, ...]:
    out: List[Any] = []
    required_arg_count = sum(
        1 for arg in command_args
        if not arg.is_optional and arg.default == inspect.Parameter.empty and arg.kind != inspect.Parameter.VAR_POSITIONAL
    )
    is_variadic = any(arg.kind == inspect.Parameter.VAR_POSITIONAL for arg in command_args)
    
    if not is_variadic and len(raw_args) > len(command_args):
        raise WrongArgumentAmountError(f"Too many arguments: expected {len(command_args)}, got {len(raw_args)}")
    if len(raw_args) < required_arg_count:
        raise WrongArgumentAmountError(f"Not enough arguments: expected at least {required_arg_count}, got {len(raw_args)}")
    
    for i, cmd_arg in enumerate(command_args):
        if cmd_arg.kind == inspect.Parameter.VAR_POSITIONAL:
            out.extend(raw_args[i:])
            break
        elif i < len(raw_args):
            out.append(smart_cast(raw_args[i], cmd_arg.annotation))
        elif cmd_arg.default != inspect.Parameter.empty:
            out.append(cmd_arg.default)
        elif cmd_arg.is_optional:
            out.append(None)
        else:
            raise WrongArgumentAmountError(f"Missing required argument: {cmd_arg.name}")
    
    return tuple(out)

class Dispatcher:
    def __init__(self, plugin_id: str, prefix: str = ".", commands_priority: int = -1):
        self.plugin_id = plugin_id
        self.prefix = prefix
        self.commands_priority = commands_priority
        self.listeners: Dict[str, Command] = {}
    
    @staticmethod
    def validate_prefix(prefix: str) -> bool:
        return len(prefix) == 1 and not prefix.isalnum()
    
    def set_prefix(self, prefix: str):
        if not self.validate_prefix(prefix):
            logger.error(f"Invalid prefix: {prefix}")
            return
        
        logger.info(f"{self.plugin_id} dp: Set '{prefix}' prefix.")
        self.prefix = prefix
    
    def register_command(self, name: str):
        def decorator(func: Callable):
            cmd = create_command(func, name)
            self.listeners[name] = cmd
            logger.info(f"{self.plugin_id} dp: Registered command {name}.")
            return func
        return decorator
    
    def unregister_command(self, name: str):
        logger.info(f"{self.plugin_id} dp: Unregistered command '{name}'.")
        self.listeners.pop(name, None)

# ==================== Decorators ====================
def command(cmd: Optional[str] = None, *, aliases: Optional[List[str]] = None, doc: Optional[str] = None, enabled: Optional[Union[str, bool]] = None):
    def decorator(func):
        func.__is_command__ = True
        func.__aliases__ = aliases or []
        func.__cdoc__ = doc
        func.__enabled__ = enabled
        func.__cmd__ = cmd or func.__name__
        return func
    return decorator

def uri(uri_path: str):
    def decorator(func):
        func.__is_uri_handler__ = True
        func.__uri__ = uri_path
        return func
    return decorator

def message_uri(uri_path: str, support_long_click: bool = False):
    def decorator(func):
        func.__is_uri_message_handler__ = True
        func.__uri__ = uri_path
        func.__support_long__ = support_long_click
        return func
    return decorator

def watcher():
    def decorator(func):
        func.__is_watcher__ = True
        return func
    return decorator

def inline_handler(method: str, support_long_click: bool = False):
    def decorator(func):
        func.__is_inline_handler__ = True
        func.__method__ = method
        func.__support_long__ = support_long_click
        return func
    return decorator

# ==================== JsonDB - JSON-based database ====================
class JsonDB(dict):
    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self._load()
    
    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.update(data)
            except Exception as e:
                logger.error(f"Failed to load JsonDB from {self.filepath}: {format_exc_only(e)}")
    
    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(dict(self), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JsonDB to {self.filepath}: {format_exc_only(e)}")
    
    def set(self, key: str, value: Any):
        self[key] = value
        self.save()
    
    def reset(self):
        self.clear()
        self.save()
    
    def pop(self, key: str, default: Any = None) -> Any:
        value = self.get(key, default)
        if key in self:
            del self[key]
            self.save()
        return value
    
    def update_from(self, **kwargs):
        self.update(kwargs)
        self.save()

# ==================== Inline buttons ====================
class Inline:

    callbacks: Dict[str, Callable] = {}
    
    class Markup:
        def __init__(self):
            self.rows = []
        
        def add_row(self, *buttons):
            if buttons and buttons[0] is not None:
                self.rows.append(list(buttons))
            return self
        
        def to_tlrpc(self) -> TLRPC.TL_replyInlineMarkup:
            markup = TLRPC.TL_replyInlineMarkup()
            markup.rows = ArrayList()
            
            for row in self.rows:
                tlrpc_row = TLRPC.TL_keyboardButtonRow()
                tlrpc_row.buttons = ArrayList()
                
                for btn in row:
                    if isinstance(btn, dict):
                        btn_type = btn.get('type', 'url')
                        
                        if btn_type == 'url':
                            button = TLRPC.TL_keyboardButtonUrl()
                            button.text = btn.get('text', '')
                            button.url = btn.get('url', '')
                        elif btn_type == 'callback':
                            button = TLRPC.TL_keyboardButtonCallback()
                            button.text = btn.get('text', '')
                            button.data = btn.get('callback_data', '').encode('utf-8')
                        else:
                            continue
                        
                        tlrpc_row.buttons.add(button)
                
                markup.rows.add(tlrpc_row)
            
            return markup
    
    @staticmethod
    def CallbackData(plugin_id: str, method: str, **kwargs) -> str:
        params = urlencode(kwargs)
        return f"mslib://{plugin_id}/{method}?{params}" if params else f"mslib://{plugin_id}/{method}"
    
    @staticmethod
    def button(text: str, *, url: Optional[str] = None, callback_data: Optional[str] = None, **kwargs):
        if url:
            return {'text': text, 'url': url, 'type': 'url'}
        elif callback_data:
            return {'text': text, 'callback_data': callback_data, 'type': 'callback'}
        return {'text': text}
    
    @classmethod
    def on_click(cls, method: str, support_long_click: bool = False):
        def decorator(func):
            cls.callbacks[method] = func
            func.__is_inline_handler__ = True
            func.__method__ = method
            func.__support_long__ = support_long_click
            return func
        return decorator

# ==================== Localization ====================
class Locales:
    en = {
        "copy_button": "Copy",
        "loaded": "MSLib loaded successfully!",
        "unloaded": "MSLib unloaded.",
        "error": "Error",
        "success": "Success",
        "info": "Info",
        "commands_header": "Commands",
        "command_prefix_label": "Command prefix",
        "command_prefix_hint": "Symbol used to trigger commands (e.g., . ! /)",
        "autoupdater_header": "AutoUpdater",
        "enable_autoupdater": "Enable AutoUpdater",
        "autoupdater_hint": "Automatically check for updates (MSLib + plugins using it)",
        "force_update_check": "Force update check",
        "autoupdate_timeout": "Update check interval (seconds)",
        "autoupdate_timeout_title": "Update check interval",
        "autoupdate_timeout_hint": "Time between update checks",
        "disable_timestamp_check_title": "Disable message edit check",
        "disable_timestamp_check_hint": "Plugin will be updated even if the file has not been modified",
        "plugins_header": "Integrated Plugins",
        "article_viewer_fix": "Disable swipe-to-close gesture in browser",
        "no_call_confirmation": "No Call Confirmation",
        "old_bottom_forward": "Old Bottom Forward",
        "hide_profile_edit": "Hide Profile Edit Button",
        "dev_header": "Developer",
        "debug_mode_title": "Debug mode",
        "debug_mode_hint": "Enables detailed logging for troubleshooting",
        "article_viewer_fix_enabled": "Article Viewer Fix enabled",
        "article_viewer_fix_disabled": "Article Viewer Fix disabled",
        "no_call_confirmation_enabled": "No Call Confirmation enabled",
        "no_call_confirmation_disabled": "No Call Confirmation disabled",
        "old_bottom_forward_enabled": "Old Bottom Forward enabled",
        "old_bottom_forward_disabled": "Old Bottom Forward disabled",
        "hide_profile_edit_enabled": "Profile edit button hidden",
        "hide_profile_edit_disabled": "Profile edit button visible",
        "update_check_started": "Update check started!",
        "autoupdater_not_initialized": "AutoUpdater is not initialized",
    }
    ru = {
        "copy_button": "Копировать",
        "loaded": "MSLib успешно загружена!",
        "unloaded": "MSLib выгружена.",
        "error": "Ошибка",
        "success": "Успешно",
        "info": "Информация",
        "commands_header": "Команды",
        "command_prefix_label": "Префикс команд",
        "command_prefix_hint": "Символ для вызова команд (например, . ! /)",
        "autoupdater_header": "Автообновления",
        "enable_autoupdater": "Автообновление",
        "force_update_check": "Принудительная проверка",
        "autoupdate_timeout": "Интервал проверки обновлений (секунды)",
        "autoupdate_timeout_title": "Интервал проверки обновлений",
        "autoupdate_timeout_hint": "Время между проверками обновлений",
        "disable_timestamp_check_title": "Отключить проверку редактирования",
        "disable_timestamp_check_hint": "Плагин будет обновлен, даже если файл не был изменен",
        "plugins_header": "Дополнительные функции",
        "article_viewer_fix": "Отключение свайпа в браузере",
        "no_call_confirmation": "Убрать подтверждение звонка",
        "old_bottom_forward": "Старое меню пересылки",
        "hide_profile_edit": "Убрать асиметрию",
        "dev_header": "Разработчик",
        "debug_mode_title": "Режим отладки",
        "debug_mode_hint": "Включает подробное логирование для диагностики",
        "article_viewer_fix_enabled": "Исправление просмотра статей включено",
        "article_viewer_fix_disabled": "Исправление просмотра статей выключено",
        "no_call_confirmation_enabled": "Без подтверждения звонка включено",
        "no_call_confirmation_disabled": "Без подтверждения звонка выключено",
        "old_bottom_forward_enabled": "Старая пересылка включена",
        "old_bottom_forward_disabled": "Старая пересылка выключена",
        "hide_profile_edit_enabled": "Кнопка редактирования профиля скрыта",
        "hide_profile_edit_disabled": "Кнопка редактирования профиля видима",
        "update_check_started": "Проверка обновлений запущена!",
        "autoupdater_not_initialized": "AutoUpdater не инициализирован",
    }
    default = en

def localise(key: str) -> str:
    try:
        locale = LOCALE if LOCALE else "en"
        locale_dict = getattr(Locales, locale, Locales.default)
        return locale_dict.get(key, key)
    except:
        return key

class CacheFile:
    def __init__(self, filename: str, read_on_init: bool = True, compress: bool = False):
        self.filename = filename
        self.path = None
        self._content: Optional[bytes] = None
        self.compress = compress
        self.logger = build_log(f"{__name__}.{self.filename}")
        self.read_on_init = read_on_init
    
    def _ensure_path(self):
        if self.path is None and CACHE_DIRECTORY:
            self.path = os.path.join(CACHE_DIRECTORY, self.filename)
            os.makedirs(CACHE_DIRECTORY, exist_ok=True)
            if self.read_on_init:
                self.read()
    
    def read(self):
        self._ensure_path()
        if not self.path or not os.path.exists(self.path):
            if self.path:
                self.logger.warning(f"{self.path} does not exist, setting value to None.")
            self._content = None
            return
        
        try:
            with open(self.path, "rb") as file:
                file_content = file.read()
            
            if self.compress and file_content.startswith(b"\x78\x9c"):
                file_content = zlib.decompress(file_content)
            
            self._content = file_content
        except Exception as e:
            self.logger.error(f"Failed to load data from {self.path}: {format_exc_only(e)}")
            self._content = None
    
    def write(self):
        self._ensure_path()
        if not self.path:
            return
        try:
            save_data = self._content
            if self.compress and save_data:
                save_data = zlib.compress(save_data, level=6)
            
            with open(self.path, "wb") as file:
                file.write(save_data)
        except PermissionError as e:
            self.logger.error(f"No permission to edit {self.path}: {format_exc_only(e)}")
        except Exception as e:
            self.logger.error(f"Error writing to {self.path}: {format_exc_only(e)}")
    
    def delete(self):
        self._ensure_path()
        if not self.path or not os.path.exists(self.path):
            if self.path:
                self.logger.warning(f"File {self.path} does not exist.")
            return
        
        try:
            os.remove(self.path)
            self.logger.info(f"File {self.path} deleted.")
        except Exception as e:
            self.logger.error(f"Failed to delete {self.path}: {format_exc_only(e)}")
    
    @property
    def content(self) -> Optional[bytes]:
        return self._content
    
    @content.setter
    def content(self, value: Optional[bytes]):
        self._content = value

class JsonCacheFile(CacheFile):
    def __init__(self, filename: str, default: Any, read_on_init: bool = True, compress: bool = False):
        self._default = copy.deepcopy(default)
        self.json_content = self._get_copy_of_default()
        super().__init__(filename, read_on_init, compress)
    
    def _get_copy_of_default(self) -> Any:
        return copy.deepcopy(self._default)
    
    def read(self):
        super().read()
        
        if not self._content:
            self.json_content = self._get_copy_of_default()
            self._content = json.dumps(self.json_content).encode()
            return
        
        try:
            self.json_content = json.loads(self._content.decode("utf-8", errors="replace"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to load JSON from {self.path}: {format_exc_only(e)}")
            self.json_content = self._get_copy_of_default()
    
    def write(self):
        self._content = json.dumps(self.json_content, ensure_ascii=False, indent=2).encode("utf-8")
        super().write()
    
    def wipe(self):
        self.json_content = self._get_copy_of_default()
        self._content = json.dumps(self.json_content).encode()
        self.write()
    
    @property
    def content(self) -> Any:
        if self._content is None:
            return self._get_copy_of_default()
        return self.json_content
    
    @content.setter
    def content(self, value: Any):
        self.json_content = value

# ==================== Callback wrappers ====================
class Callback1(dynamic_proxy(Utilities.Callback)):
    def __init__(self, fn: Callable[[Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg):
        try:
            self._fn(arg)
        except Exception as e:
            logger.error(f"Error in Callback1: {format_exc()}")

class Callback2(dynamic_proxy(Utilities.Callback2)):
    def __init__(self, fn: Callable[[Any, Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg1, arg2):
        try:
            self._fn(arg1, arg2)
        except Exception as e:
            logger.error(f"Error in Callback2: {format_exc()}")

class Callback3(dynamic_proxy(Utilities.Callback)):
    def __init__(self, fn: Callable[[Any, Any, Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg1, arg2, arg3):
        try:
            self._fn(arg1, arg2, arg3)
        except Exception as e:
            logger.error(f"Error in Callback3: {format_exc()}")

class Callback5(dynamic_proxy(Utilities.Callback5)):
    def __init__(self, fn: Callable[[Any, Any, Any, Any, Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg1, arg2, arg3, arg4, arg5):
        try:
            self._fn(arg1, arg2, arg3, arg4, arg5)
        except Exception as e:
            logger.error(f"Error in Callback5: {format_exc()}")

# ==================== Text Utilities ====================
def escape_html(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def unescape_html(text: str) -> str:
    return html.unescape(text)

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

# ==================== Data utilities ====================
def compress_and_encode(data: Union[bytes, str], level: int = 6) -> str:
    try:
        import base64
        if isinstance(data, str):
            data = data.encode('utf-8')
        compressed = zlib.compress(data, level=level)
        return base64.b64encode(compressed).decode('ascii')
    except Exception as e:
        logger.error(f"Failed to compress and encode: {format_exc_only(e)}")
        return ""

def decode_and_decompress(encoded_data: Union[bytes, str]) -> bytes:
    try:
        import base64
        if isinstance(encoded_data, str):
            encoded_data = encoded_data.encode('ascii')
        compressed = base64.b64decode(encoded_data)
        return zlib.decompress(compressed)
    except Exception as e:
        logger.error(f"Failed to decode and decompress: {format_exc_only(e)}")
        return b""

# ==================== Text Utilities ====================

def unescape_html(text: str) -> str:
    import html
    return html.unescape(text)

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

# ==================== Clipboard Utilities ====================
def copy_to_clipboard(text: str, show_bulletin: bool = True) -> bool:
    success = AndroidUtilities.addToClipboard(text)
    if success and show_bulletin:
        BulletinHelper.show_copied_to_clipboard()
    return success

# ==================== Bulletin Helper ====================
class InnerBulletinHelper(_BulletinHelper):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = "" if not prefix or not prefix.strip() else f"{prefix}:"
    
    def show_info(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_info(f"{self.prefix} {message}", fragment)
    
    def show_error(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_error(f"{self.prefix} {message}", fragment)
    
    def show_success(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_success(f"{self.prefix} {message}", fragment)
    
    def show_with_copy(self, message: str, text_to_copy: str, icon_res_id: int):
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}" if not message.startswith(f"{self.prefix} ") else message,
            icon_res_id,
            localise("copy_button"),
            on_click=lambda: copy_to_clipboard(text_to_copy, show_bulletin=False),
        )
    
    def show_info_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.info)
    
    def show_error_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.error)
    
    def show_success_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.contact_check)
    
    def show_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int, icon_res_id: int = 0):
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}",
            icon_res_id,
            button_text,
            on_click=lambda: get_last_fragment().presentFragment(ChatActivity.of(peer_id, message_id)),
        )
    
    def show_info_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.info)
    
    def show_error_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.error)
    
    def show_success_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.contact_check)

def build_bulletin_helper(prefix: Optional[str] = None) -> InnerBulletinHelper:
    return InnerBulletinHelper(prefix)

BulletinHelper = build_bulletin_helper(__name__)

def _bulletin(level: str, message: str):
    getattr(BulletinHelper, f"show_{level}")(message, None)

# ==================== AutoUpdater ====================
class UpdaterTask:
    def __init__(self, plugin_id, channel_id, message_id):
        self.plugin_id = plugin_id
        self.channel_id = channel_id
        self.message_id = message_id

class AutoUpdater:
    def __init__(self):
        self.thread: Optional[threading.Thread] = None
        self.forced_stop = False
        self.forced_update_check = False
        self.tasks: List[UpdaterTask] = []
        self.msg_edited_ts_cache = JsonCacheFile("mslib_au__msg_edited_ts", {})
        self.hash = str(zlib.adler32(id(self).to_bytes(8, "little")))
        self.logger = build_log(f"{__name__} AU {self.hash}")
    
    def run(self):
        self.forced_stop = False
        
        if self.thread is None:
            self.thread = threading.Thread(target=self.cycle, daemon=True)
        
        if self.thread.is_alive():
            self.logger.warning("Thread is already running.")
            return
        
        self.thread.start()
        self.logger.info("Thread was started.")
    
    def force_stop(self):
        if self.thread is None:
            self.logger.warning("Thread is not running.")
            return
        self.forced_stop = True
    
    def cycle(self):
        event = threading.Event()
        event.wait(5)
        
        while not self.forced_stop:
            try:
                self.check_for_updates(show_notifications=False)
                start_time = time.time()
                timeout = self.get_timeout_time()
                
                while (time.time() - start_time) < timeout:
                    event.wait(1)
                    
                    if self.forced_update_check:
                        self.logger.info("Forced update check requested, checking immediately...")
                        self.check_for_updates(show_notifications=True)
                        self.forced_update_check = False
                    
                    if self.forced_stop:
                        break
                    
                    if (time.time() - start_time) >= timeout:
                        break
                        
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt, stopping...")
                break
            except Exception as e:
                self.logger.error(f"Exception in cycle: {format_exc_only(e)}")
                if not self.forced_stop:
                    event.wait(60)
        
        self.thread = None
        self.logger.info("Force stopped.")
    
    def check_for_updates(self, show_notifications: bool = False):
        self.logger.info(f"Checking for updates... (notifications: {show_notifications})")
        
        for task in list(self.tasks):
            try:
                plugin = get_plugin(task.plugin_id)
                
                if plugin is None:
                    self.logger.info(f"Plugin {task.plugin_id} not found. Removing task...")
                    self.remove_task(task)
                    continue
                
                if not plugin.isEnabled():
                    self.logger.info(f"Plugin {task.plugin_id} is disabled. Skipping update check...")
                    continue
                
                self.logger.info(f"Checking update for task {task.plugin_id}...")
                self._check_task_for_update(task, show_notifications)
                
            except Exception as e:
                self.logger.error(f"Error checking update for {task.plugin_id}: {format_exc_only(e)}")
    
    def _check_task_for_update(self, task: UpdaterTask, show_notifications: bool = False):
        def get_message_callback(msg):
            if not msg or isinstance(msg, TLRPC.TL_messageEmpty):
                self.logger.warning(f"Message not found for {task.plugin_id}. Removing task...")
                if show_notifications:
                    InnerBulletinHelper("MSLib").show_error(f"Update check failed: message not found for {task.plugin_id}")
                self.remove_task(task)
                return
            
            if not msg.media:
                self.logger.warning(f"Message has no media for {task.plugin_id}. Removing task...")
                if show_notifications:
                    InnerBulletinHelper("MSLib").show_error(f"Update check failed: no document for {task.plugin_id}")
                self.remove_task(task)
                return
            
            disable_ts_check = MSLib_instance.get_setting("disable_timestamp_check", DEFAULT_DISABLE_TIMESTAMP_CHECK) if MSLib_instance else DEFAULT_DISABLE_TIMESTAMP_CHECK
            
            if not disable_ts_check:
                cache_key = f"{task.channel_id}_{task.message_id}"
                cached_edit_date = self.msg_edited_ts_cache.content.get(cache_key, 0)
                current_edit_date = msg.edit_date if msg.edit_date != 0 else msg.date
                
                if current_edit_date <= cached_edit_date:
                    self.logger.info(f"No updates for {task.plugin_id}")
                    if show_notifications:
                        InnerBulletinHelper("MSLib").show_info(f"{task.plugin_id}: Already up to date")
                    return
                
                self.logger.info(f"Update available for {task.plugin_id}: {cached_edit_date} -> {current_edit_date}")
                if show_notifications:
                    InnerBulletinHelper("MSLib").show_success(f"Update found for {task.plugin_id}")
                
                self.msg_edited_ts_cache.content[cache_key] = current_edit_date
                self.msg_edited_ts_cache.write()
            else:
                self.logger.info(f"Timestamp check disabled, forcing update for {task.plugin_id}")
                if show_notifications:
                    InnerBulletinHelper("MSLib").show_info(f"Forcing update for {task.plugin_id}")
            
            run_on_queue(lambda: download_and_install_plugin(msg, task.plugin_id))
        
        Requests.get_message(
            -task.channel_id,
            task.message_id,
            callback=lambda msg, process_task=task: get_message_callback(msg)
        )
    
    def is_task_already_present(self, task: UpdaterTask) -> bool:
        for t in self.tasks:
            if t.plugin_id == task.plugin_id:
                return True
        return False
    
    def add_task(self, task: UpdaterTask):
        if self.is_task_already_present(task):
            self.logger.warning(f"Task {task.plugin_id} already exists.")
            return
        
        self.tasks.append(task)
        self.logger.info(f"Added task {task.plugin_id}.")
    
    def remove_task(self, task: UpdaterTask):
        if task not in self.tasks:
            self.logger.warning(f"Task {task.plugin_id} not found.")
            return
        
        self.tasks.remove(task)
        self.logger.info(f"Removed task {task.plugin_id}")
    
    def remove_task_by_id(self, plugin_id: str):
        filtered_tasks = [t for t in self.tasks if t.plugin_id != plugin_id]
        if len(filtered_tasks) < len(self.tasks):
            self.tasks = filtered_tasks
            self.logger.info(f"Removed task {plugin_id}")
        else:
            self.logger.warning(f"Task {plugin_id} not found.")
    
    def get_timeout_time(self) -> int:
        try:
            timeout_str = MSLib_instance.get_setting("autoupdate_timeout", DEFAULT_AUTOUPDATE_TIMEOUT) if MSLib_instance else DEFAULT_AUTOUPDATE_TIMEOUT
            return int(timeout_str)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to get timeout: {format_exc_only(e)}")
            return int(DEFAULT_AUTOUPDATE_TIMEOUT)
    
    def force_update_check(self):
        self.logger.info("Forced update check was requested.")
        self.forced_update_check = True

# ==================== AutoUpdater Helper Features ====================
def download_and_install_plugin(msg, plugin_id: str, max_tries: int = 10, is_queued: bool = False, current_try: int = 0):
    def plugin_install_error(arg):
        if arg is None:
            return
        logger.error(f"Error installing {plugin_id}: {arg}")
        InnerBulletinHelper("MSLib").show_error(f"Error installing {plugin_id}. Check logs.")
    
    try:
        file_loader = get_file_loader()
        plugins_controller = PluginsController.getInstance()
        document = msg.media.getDocument()
        path = file_loader.getPathToAttach(document, True)
        
        if not path.exists():
            if is_queued:
                logger.info(f"Waiting 1s for {plugin_id} file to download ({current_try}/{max_tries})...")
            else:
                logger.info(f"Starting download of {plugin_id} plugin file...")
            
            file_loader.loadFile(document, msg, FileLoader.PRIORITY_NORMAL, 1)
            
            if current_try >= max_tries:
                logger.error(f"Max tries reached for {plugin_id}, installation aborted.")
                InnerBulletinHelper("MSLib").show_error(f"Failed to download {plugin_id}")
                return
            
            run_on_queue(
                lambda: download_and_install_plugin(msg, plugin_id, max_tries, True, current_try + 1),
                delay=1
            )
            return
        
        logger.info(f"Installing {plugin_id}...")
        
        try:
            plugins_controller.loadPluginFromFile(str(path), None, Callback1(plugin_install_error))
        except TypeError:
            plugins_controller.loadPluginFromFile(str(path), Callback1(plugin_install_error))
        
        logger.info(f"Plugin {plugin_id} installed successfully")
        InnerBulletinHelper("MSLib").show_success(f"{plugin_id} updated successfully!")
        
    except AttributeError as e:
        logger.error(f"AttributeError in download_and_install_plugin for {plugin_id}: {format_exc_only(e)}")
        InnerBulletinHelper("MSLib").show_error(f"Invalid message format for {plugin_id}")
    except Exception as e:
        logger.error(f"Error in download_and_install_plugin for {plugin_id}: {format_exc()}")
        InnerBulletinHelper("MSLib").show_error(f"Failed to install {plugin_id}: {format_exc_only(e)}")

def get_plugin(plugin_id: str):
    return PluginsController.getInstance().plugins.get(plugin_id)

def add_autoupdater_task(plugin_id: str, channel_id: int, message_id: int):
    global autoupdater
    if not autoupdater:
        logger.warning("AutoUpdater is not initialized")
        return
    
    task = UpdaterTask(plugin_id, channel_id, message_id)
    autoupdater.add_task(task)
    logger.info(f"Added autoupdate task for {plugin_id}: channel={channel_id}, message={message_id}")

def remove_autoupdater_task(plugin_id: str):
    global autoupdater
    if not autoupdater:
        logger.warning("AutoUpdater is not initialized")
        return
    
    autoupdater.remove_task_by_id(plugin_id)
    logger.info(f"Removed autoupdate task for {plugin_id}")

# ==================== Requests utilities ====================
def request_callback_factory(custom_callback: Optional[Callable]):
    def default_callback(response, error):
        if custom_callback:
            custom_callback(response, error)
        else:
            if error:
                logger.error(f"Request error: {error}")
    return default_callback

class Requests:
    @staticmethod
    def send(request: TLObject, callback: Optional[Callable] = None, account: int = 0):
        send_request(request, request_callback_factory(callback), account)
    
    @staticmethod
    def get_user(user_id: int, callback: Callable, account: int = 0):
        request = TLRPC.TL_users_getUsers()
        input_user = TLRPC.TL_inputUser()
        input_user.user_id = user_id
        request.id = ArrayList()
        request.id.add(input_user)
        
        def user_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                users = arraylist_to_list(response)
                callback(users[0] if users else None, error)
        
        Requests.send(request, user_callback, account)
    
    @staticmethod
    def get_chat(chat_id: int, callback: Callable, account: int = 0):
        request = TLRPC.TL_messages_getChats()
        request.id = ArrayList()
        request.id.add(Long(abs(chat_id)))
        
        def chat_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                chats = arraylist_to_list(response.chats)
                callback(chats[0] if chats else None, error)
        
        Requests.send(request, chat_callback, account)
    
    @staticmethod
    def get_message(channel_id: int, message_id: int, callback: Callable, account: int = 0):
        request = TLRPC.TL_channels_getMessages()
        input_channel = TLRPC.TL_inputChannel()
        input_channel.channel_id = abs(channel_id)
        input_channel.access_hash = 0
        request.channel = input_channel
        request.id = ArrayList()
        input_message = TLRPC.TL_inputMessageID()
        input_message.id = message_id
        request.id.add(input_message)
        
        def message_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                messages = arraylist_to_list(response.messages) if hasattr(response, 'messages') else []
                callback(messages[0] if messages else None, error)
        
        Requests.send(request, message_callback, account)
    
    @staticmethod
    def search_messages(
        peer_id: int,
        query: str,
        callback: Callable,
        limit: int = 100,
        offset_id: int = 0,
        filter_type: Optional[Any] = None,
        account: int = 0
    ):
        request = TLRPC.TL_messages_search()
        request.peer = Requests._get_input_peer(peer_id)
        request.q = query
        request.filter = filter_type or TLRPC.TL_inputMessagesFilterEmpty()
        request.limit = limit
        request.offset_id = offset_id
        request.min_date = 0
        request.max_date = 0
        request.add_offset = 0
        request.max_id = 0
        request.min_id = 0
        request.hash = 0
        
        def search_callback(response, error):
            if error or not response:
                callback([], error)
            else:
                messages = arraylist_to_list(response.messages) if hasattr(response, 'messages') else []
                callback(messages, error)
        
        Requests.send(request, search_callback, account)
    
    @staticmethod
    def _get_input_peer(peer_id: int):
        if peer_id > 0:
            # User
            input_peer = TLRPC.TL_inputPeerUser()
            input_peer.user_id = peer_id
            input_peer.access_hash = 0
        elif peer_id < -1000000000000:
            # Channel
            input_peer = TLRPC.TL_inputPeerChannel()
            input_peer.channel_id = abs(peer_id + 1000000000000)
            input_peer.access_hash = 0
        else:
            # Chat
            input_peer = TLRPC.TL_inputPeerChat()
            input_peer.chat_id = abs(peer_id)
        
        return input_peer
    
    @staticmethod
    def delete_messages(message_ids: List[int], peer_id: int, callback: Optional[Callable] = None, revoke: bool = True, account: int = 0):
        if peer_id < -1000000000000:
            request = TLRPC.TL_channels_deleteMessages()
            request.channel = Requests._get_input_peer(peer_id)
            request.id = list_to_arraylist(message_ids)
        else:
            request = TLRPC.TL_messages_deleteMessages()
            request.id = list_to_arraylist(message_ids)
            request.revoke = revoke
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def ban(chat_id: int, peer_id: int, until_date: Optional[int] = None, callback: Optional[Callable] = None, account: int = 0):
        msg_controller = get_messages_controller()
        
        banned_rights = TLRPC.TL_chatBannedRights()
        banned_rights.view_messages = True
        banned_rights.send_messages = True
        banned_rights.send_media = True
        banned_rights.send_stickers = True
        banned_rights.send_gifs = True
        banned_rights.send_games = True
        banned_rights.send_inline = True
        banned_rights.embed_links = True
        banned_rights.send_polls = True
        banned_rights.change_info = True
        banned_rights.invite_users = True
        banned_rights.pin_messages = True
        banned_rights.until_date = until_date or 0
        
        request = TLRPC.TL_channels_editBanned()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(peer_id)
        request.banned_rights = banned_rights
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def unban(chat_id: int, target_peer_id: int, callback: Optional[Callable] = None, account: int = 0):
        msg_controller = get_messages_controller()
        
        banned_rights = TLRPC.TL_chatBannedRights()
        banned_rights.until_date = 0
        
        request = TLRPC.TL_channels_editBanned()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(target_peer_id)
        request.banned_rights = banned_rights
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def change_slowmode(chat_id: int, seconds: int = 0, callback: Optional[Callable] = None, account: int = 0):
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_channels_toggleSlowMode()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.seconds = seconds
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def reload_admins(chat_id: int, account: int = 0):
        get_messages_controller().loadChannelAdmins(chat_id, False)
    
    @staticmethod
    def get_chat_participant(chat_id: int, target_peer_id: int, callback: Callable, account: int = 0):
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_channels_getParticipant()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(target_peer_id)
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def edit_message(message_object: MessageObject, text: str, entities: Optional[ArrayList] = None, 
                     markup: Optional[Any] = None, callback: Optional[Callable] = None, account: int = 0):
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_messages_editMessage()
        request.peer = msg_controller.getInputPeer(message_object.getDialogId())
        request.id = message_object.getId()
        request.message = text
        request.no_webpage = True
        
        if entities:
            request.entities = entities
            request.flags |= 8
        
        if markup:
            request.reply_markup = markup
            request.flags |= 4
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def forward_messages(from_peer: int, to_peer: int, message_ids: List[int], 
                        callback: Optional[Callable] = None, account: int = 0):
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_messages_forwardMessages()
        request.from_peer = msg_controller.getInputPeer(from_peer)
        request.to_peer = msg_controller.getInputPeer(to_peer)
        request.id = list_to_arraylist(message_ids)
        request.random_id = ArrayList()
        
        for _ in message_ids:
            request.random_id.add(Long(Utilities.random.nextLong()))
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def get_full_user(user_id: int, callback: Callable, account: int = 0):
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_users_getFullUser()
        request.id = msg_controller.getInputUser(user_id)
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def get_full_chat(chat_id: int, callback: Callable, account: int = 0):
        if chat_id < -1000000000000:
            # Channel
            request = TLRPC.TL_channels_getFullChannel()
            request.channel = get_messages_controller().getInputChannel(chat_id)
        else:
            # Chat
            request = TLRPC.TL_messages_getFullChat()
            request.chat_id = abs(chat_id)
        
        Requests.send(request, callback, account)

# ==================== System utilities ====================
def runtime_exec(cmd: List[str], return_list_lines: bool = False, raise_errors: bool = True) -> Union[List[str], str]:
    from java.lang import Runtime # type: ignore
    from java.io import BufferedReader, InputStreamReader, IOException # type: ignore
    
    result = []
    process = None
    reader = None
    try:
        process = Runtime.getRuntime().exec(cmd)
        reader = BufferedReader(InputStreamReader(process.getInputStream()))
        line = reader.readLine()
        while line is not None:
            result.append(str(line))
            line = reader.readLine()
    except IOException as e:
        if raise_errors:
            raise e
        logger.error(f"IOException in runtime_exec: {format_exc_only(e)}")
    except Exception as e:
        if raise_errors:
            raise e
        logger.error(f"Error in runtime_exec: {format_exc()}")
    finally:
        if reader:
            try:
                reader.close()
            except:
                pass
        if process:
            try:
                process.destroy()
            except:
                pass
    
    return result if return_list_lines else "\n".join(result)

def get_logs(__id__: Optional[str] = None, times: Optional[int] = None, lvl: Optional[str] = None, as_list: bool = False) -> Union[List[str], str]:
    cmd = ["logcat", "-d", "-v", "time"]
    
    if times:
        from java.lang import System as JavaSystem # type: ignore
        time_str = f"{times}s ago"
        cmd.extend(["-t", time_str])
    
    if lvl:
        cmd.extend(["*:{}".format(lvl)])
    
    result = runtime_exec(cmd, return_list_lines=True, raise_errors=False)
    
    if __id__:
        result = [line for line in result if f"[{__id__}]" in line]
    
    logger.debug(f"Got logs with {__id__=}, {times=}s, {lvl=}")
    
    return result if as_list else "\n".join(result)

def pluralization_string(count: int, variants: Tuple[str, str, str]) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} {variants[0]}"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return f"{count} {variants[1]}"
    else:
        return f"{count} {variants[2]}"

# ==================== UI utilities ====================
class UI:
    @staticmethod
    @run_on_ui_thread
    def show_alert(title: str, message: str, positive_button: str = "OK", on_click: Optional[Callable] = None):
        builder = AlertDialogBuilder(ApplicationLoader.applicationContext)
        builder.set_title(title)
        builder.set_message(message)
        builder.set_positive_button(positive_button, on_click)
        builder.show()
    
    @staticmethod
    @run_on_ui_thread
    def show_confirm(title: str, message: str, on_confirm: Callable, on_cancel: Optional[Callable] = None):
        builder = AlertDialogBuilder(ApplicationLoader.applicationContext)
        builder.set_title(title)
        builder.set_message(message)
        builder.set_positive_button("OK", on_confirm)
        builder.set_negative_button("Cancel", on_cancel)
        builder.show()

class Spinner:
    def __init__(self, text: str = "Loading..."):
        self.text = text
        self.alert_dialog = None
        self._shown = False
    
    def show(self):
        if self._shown:
            return
        
        @run_on_ui_thread
        def _show():
            from org.telegram.ui.Components import LineProgressView # type: ignore
            from org.telegram.ui.ActionBar import AlertDialog # type: ignore
            
            builder = AlertDialog.Builder(ApplicationLoader.applicationContext)
            builder.setTitle(self.text)
            
            progress = LineProgressView(ApplicationLoader.applicationContext)
            builder.setView(progress)
            
            self.alert_dialog = builder.create()
            self.alert_dialog.setCanceledOnTouchOutside(False)
            self.alert_dialog.show()
        
        _show()
        self._shown = True
    
    def hide(self):
        if not self._shown:
            return
        
        @run_on_ui_thread
        def _hide():
            if self.alert_dialog:
                try:
                    self.alert_dialog.dismiss()
                except:
                    pass
        
        _hide()
        self._shown = False
    
    def __enter__(self):
        self.show()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.hide()
        return False

# ==================== File System utilities ====================
class FileSystem:
    @staticmethod
    def get_cache_dir(*path: str) -> str:
        if not CACHE_DIRECTORY:
            _init_constants()
        return os.path.join(CACHE_DIRECTORY, *path)
    
    @staticmethod
    def get_plugins_dir(*path: str) -> str:
        if not PLUGINS_DIRECTORY:
            _init_constants()
        return os.path.join(PLUGINS_DIRECTORY, *path)
    
    @staticmethod
    def read_file(filepath: str, mode: str = 'r', encoding: str = 'utf-8') -> Union[str, bytes]:
        try:
            with open(filepath, mode, encoding=encoding if 'b' not in mode else None) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {format_exc_only(e)}")
            return '' if 'b' not in mode else b''
    
    @staticmethod
    def write_file(filepath: str, content: Union[str, bytes], mode: str = 'w', encoding: str = 'utf-8'):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, mode, encoding=encoding if 'b' not in mode else None) as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file {filepath}: {format_exc_only(e)}")
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        return os.path.exists(filepath)
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        try:
            return os.path.getsize(filepath)
        except:
            return 0

# ==================== Singleton metaclass ====================
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

autoupdater: Optional[AutoUpdater] = None
MSLib_instance: Optional['MSLib'] = None
command_dispatcher: Optional[Dispatcher] = None

# ==================== Base ====================
class MSLib(BasePlugin):
    def on_plugin_load(self):
        global autoupdater, MSLib_instance, command_dispatcher
        
        MSLib_instance = self
        
        if command_dispatcher is None:
            prefix = self.get_setting("command_prefix", ".")
            command_dispatcher = Dispatcher(__id__, prefix=prefix)
            logger.info(f"Command dispatcher initialized with prefix: {prefix}")
        
        _init_constants()
        
        self.add_on_send_message_hook(priority=999999)
        
        logger.info(localise("loaded"))
        self.log("MSLib initialized")
        
        if self.get_setting("enable_autoupdater", False):
            from functools import partial
            run_on_ui_thread(partial(self._delayed_autoupdater_start))
            logger.info("AutoUpdater will be started via delayed callback")
        
        self._setup_addons()

    
    def _delayed_autoupdater_start(self):
        global autoupdater
        if not autoupdater:
            autoupdater = AutoUpdater()
            add_autoupdater_task(__id__, MSLIB_AUTOUPDATE_CHANNEL_ID, MSLIB_AUTOUPDATE_MSG_ID)
            logger.info(f"MSLib self-update task added: channel={MSLIB_AUTOUPDATE_CHANNEL_ID}, message={MSLIB_AUTOUPDATE_MSG_ID}")
        
        if autoupdater.thread is None or not autoupdater.thread.is_alive():
            autoupdater.run()
            logger.info("AutoUpdater started on plugin load")
    
    
    def on_send_message_hook(self, account, params):
        global command_dispatcher
        
        if not command_dispatcher or not params or not params.message:
            return HookResult()
        
        message = params.message.strip()
        prefix = command_dispatcher.prefix
        
        if not message or not message.startswith(prefix):
            return HookResult()
        
        if message == prefix or (len(message) > 1 and ' ' not in message):
            commands = self._get_command_hints(message)
            
            if commands:
                markup = Inline.Markup()
                
                row_buttons = []
                for cmd_name, cmd_doc in commands[:12]:
                    btn_text = f"/{cmd_name}"
                    row_buttons.append(
                        Inline.button(
                            btn_text,
                            callback_data=Inline.CallbackData("mslib", "setCommand", cmd=cmd_name)
                        )
                    )
                    
                    if len(row_buttons) == 3:
                        markup.add_row(*row_buttons)
                        row_buttons = []
                
                if row_buttons:
                    markup.add_row(*row_buttons)
                
                hint_text = f"<b>💡 Available commands ({len(commands)}):</b>\n"
                hint_text += "\n".join([f"  <code>{prefix}{name}</code> - {doc}" for name, doc in commands[:5]])
                
                if len(commands) > 5:
                    hint_text += f"\n  <i>... and {len(commands) - 5} more</i>"
                
                peer_id = params.peer
                
                try:
                    send_message(
                        peer_id,
                        hint_text,
                        entities=HTML.parse(hint_text)[1],
                        reply_markup=markup.to_tlrpc(),
                        account=account
                    )
                except Exception as e:
                    logger.error(f"Failed to send command hints: {format_exc_only(e)}")
                
                return HookResult(strategy=HookStrategy.CANCEL)
        
        return HookResult()
    
    def _get_command_hints(self, partial_text: str) -> List[Tuple[str, str]]:
        global command_dispatcher
        
        if not command_dispatcher:
            return []
        
        prefix = command_dispatcher.prefix
        search_text = partial_text[len(prefix):].lower()
        
        commands = []

        for cmd_name in command_dispatcher.listeners.keys():
            if not search_text or cmd_name.lower().startswith(search_text):
                cmd_obj = command_dispatcher.listeners[cmd_name]
                doc = "No description"
                
                if hasattr(cmd_obj.func, '__doc__') and cmd_obj.func.__doc__:
                    doc = cmd_obj.func.__doc__.strip().split('\n')[0][:50]
                
                commands.append((cmd_name, doc))
        
        commands.sort(key=lambda x: x[0])
        
        return commands
    
    @Inline.on_click("setCommand")
    def _set_command_callback(self, params, cmd: str):
        try:
            frag = get_last_fragment()
            if not frag:
                return
            
            from hook_utils import get_private_field
            chat_enter_view = get_private_field(frag, "chatActivityEnterView")
            
            if chat_enter_view:
                global command_dispatcher
                prefix = command_dispatcher.prefix if command_dispatcher else "."
                chat_enter_view.setFieldText(f"{prefix}{cmd} ")
                logger.debug(f"Set command in field: {prefix}{cmd}")
        except Exception as e:
            logger.error(f"Failed to set command: {format_exc_only(e)}")
    
    def _setup_addons(self):
        class ArticleViewerFixHook(MethodHook):
            def before_hooked_method(hook_self, param):
                if not self.get_setting("enable_article_viewer_fix", False):
                    return
                param.setResult(False)
        
        try:
            article_viewer_window_class = jclass("org.telegram.ui.ArticleViewer$WindowView")
            method = article_viewer_window_class.getClass().getDeclaredMethod("handleTouchEvent", MotionEvent)
            self.hook_method(method, ArticleViewerFixHook())
            logger.info("Article Viewer Fix hook registered")
        except Exception as e:
            logger.error(f"Failed to register Article Viewer Fix: {e}")
        
        class NoCallConfirmationHook(MethodHook):
            def before_hooked_method(hook_self, param):
                if not self.get_setting("enable_no_call_confirmation", False):
                    return
                param.args[6] = True
        
        try:
            from org.telegram.ui.Components.voip import VoIPHelper  # type: ignore
            from android.app import Activity # type: ignore
            voip_helper_class = VoIPHelper.getClass()
            method = voip_helper_class.getDeclaredMethod(
                "startCall",
                TLRPC.User, Boolean.TYPE, Boolean.TYPE, 
                Activity, TLRPC.UserFull, AccountInstance, Boolean.TYPE
            )
            self.hook_method(method, NoCallConfirmationHook())
            logger.info("No Call Confirmation hook registered")
        except Exception as e:
            logger.error(f"Failed to register No Call Confirmation: {e}")
        
        class OldBottomForwardHook(MethodHook):
            def before_hooked_method(hook_self, param):
                if not self.get_setting("enable_old_bottom_forward", False):
                    return
                param.args[0] = True
        
        try:
            chat_activity_class = ChatActivity.getClass()
            method = chat_activity_class.getDeclaredMethod("openForward", Boolean.TYPE)
            self.hook_method(method, OldBottomForwardHook())
            logger.info("Old Bottom Forward hook registered")
        except Exception as e:
            logger.error(f"Failed to register Old Bottom Forward: {e}")
        
        class HideProfileEditButtonHook(MethodHook):
            def after_hooked_method(hook_self, param):
                if not self.get_setting("enable_hide_profile_edit", False):
                    return
                
                try:
                    profileActivity = param.thisObject
                    set_private_field(profileActivity, "editItemVisible", False)
                    editItem = get_private_field(profileActivity, "editItem")
                    if editItem:
                        editItem.setVisibility(View.GONE)
                        logger.info("Profile edit button (editItem) hidden successfully")
                except Exception as e:
                    logger.error(f"Failed to hide profile edit button: {format_exc()}")
        
        try:
            from org.telegram.ui import ProfileActivity # type: ignore
            profile_activity_class = ProfileActivity.getClass()
            method = profile_activity_class.getDeclaredMethod("createActionBarMenu", Boolean.TYPE)
            self.hook_method(method, HideProfileEditButtonHook())
            logger.info("Hide Profile Edit Button hook registered")
        except Exception as e:
            logger.error(f"Failed to register Hide Profile Edit Button: {e}")
        
        logger.info("Integrated plugins setup complete")


    def on_plugin_unload(self):
        global autoupdater
        
        logger.info(localise("unloaded"))
        self.log("MSLib unloaded")
        
        if autoupdater:
            autoupdater.force_stop()
            autoupdater = None
            logger.info("AutoUpdater stopped")
    

    def create_settings(self):
        def toggle_autoupdater(enabled: bool):
            global autoupdater
            logger.info(f"Toggle AutoUpdater: {enabled}")
            
            if enabled:
                if not autoupdater:
                    autoupdater = AutoUpdater()
                    add_autoupdater_task(__id__, MSLIB_AUTOUPDATE_CHANNEL_ID, MSLIB_AUTOUPDATE_MSG_ID)
                    logger.info("MSLib self-update task added")
                
                if autoupdater.thread is None or not autoupdater.thread.is_alive():
                    autoupdater.run()
                    _bulletin("success", "AutoUpdater started!")
                    logger.info("AutoUpdater started")
                else:
                    _bulletin("info", "AutoUpdater already running")
            else:
                if autoupdater:
                    autoupdater.force_stop()
                    _bulletin("info", "AutoUpdater stopped")
                    logger.info("AutoUpdater stopped")
                else:
                    _bulletin("info", "AutoUpdater already stopped")
        
        def update_command_prefix(new_prefix: str):
            global command_dispatcher
            if command_dispatcher and new_prefix:
                if Dispatcher.validate_prefix(new_prefix):
                    command_dispatcher.set_prefix(new_prefix)
                    _bulletin("success", f"Command prefix updated to: {new_prefix}")
                    logger.info(f"Command prefix updated to: {new_prefix}")
                else:
                    _bulletin("error", "Invalid prefix! Must be a single non-alphanumeric character")
        
        def force_update_check_onclick(_):
            global autoupdater
            if autoupdater and autoupdater.thread and autoupdater.thread.is_alive():
                autoupdater.force_update_check()
                _bulletin("success", localise("update_check_started"))
            else:
                _bulletin("error", "AutoUpdater is not running. Enable it first!")
        
        def switch_debug_mode(new_value: bool):
            logger.setLevel(logging.DEBUG if new_value else logging.INFO)
            logger.info(f"Debug mode: {new_value}, level: {logging.getLevelName(logger.level)}")
        
        def toggle_plugin(plugin_name: str):
            def callback(value: bool):
                logger.info(f"[TOGGLE] Plugin: {plugin_name}, Value: {value}")
                
                status = "enabled" if value else "disabled"
                level = "success" if value else "info"
                message_key = f"{plugin_name.replace('_', '-')}-{status}"
                message = localise(message_key)
                logger.info(f"[BULLETIN] Level: {level}, Message: {message}")
                _bulletin(level, message)
                logger.info("[TOGGLE] Complete - hook will check setting on next call")
            return callback
        
        return [
            Header(text=localise("commands_header")),
            Input(
                key="command_prefix",
                text=localise("command_prefix_label"),
                subtext=localise("command_prefix_hint"),
                default=".",
                icon="msg_limit_stories",
                on_change=update_command_prefix
            ),
            Divider(),
            Header(text=localise("autoupdater_header")),
            Switch(
                key="enable_autoupdater",
                text=localise("enable_autoupdater"),
                default=False,
                icon="msg_download_solar",
                on_change=toggle_autoupdater
            ),
            Text(
                text=localise("force_update_check"),
                icon="msg_photo_switch2",
                on_click=force_update_check_onclick
            ),
            Input(
                key="autoupdate_timeout",
                text=localise("autoupdate_timeout_title"),
                subtext=localise("autoupdate_timeout_hint"),
                default=DEFAULT_AUTOUPDATE_TIMEOUT,
                icon="msg2_autodelete"
            ),
            Switch(
                key="disable_timestamp_check",
                text=localise("disable_timestamp_check_title"),
                subtext=localise("disable_timestamp_check_hint"),
                default=DEFAULT_DISABLE_TIMESTAMP_CHECK,
                icon="msg_recent"
            ),
            Divider(),
            Header(text=localise("plugins_header")),
            Switch(
                key="enable_article_viewer_fix",
                text=localise("article_viewer_fix"),
                default=False,
                icon="msg_language_solar",
                on_change=toggle_plugin("article_viewer_fix")
            ),
            Switch(
                key="enable_no_call_confirmation",
                text=localise("no_call_confirmation"),
                default=False,
                icon="msg_calls_solar",
                on_change=toggle_plugin("no_call_confirmation")
            ),
            Switch(
                key="enable_old_bottom_forward",
                text=localise("old_bottom_forward"),
                default=False,
                icon="input_forward_solar",
                on_change=toggle_plugin("old_bottom_forward")
            ),
            Switch(
                key="enable_hide_profile_edit",
                text=localise("hide_profile_edit"),
                default=False,
                icon="msg_edit",
                on_change=toggle_plugin("hide_profile_edit")
            ),
            Divider(),
            Header(text=localise("dev_header")),
            Switch(
                key="debug_mode",
                text=localise("debug_mode_title"),
                subtext=localise("debug_mode_hint"),
                default=DEFAULT_DEBUG_MODE,
                icon="msg_log_solar",
                on_change=switch_debug_mode
            ),
        ]
