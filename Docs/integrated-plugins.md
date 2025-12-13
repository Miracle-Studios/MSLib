# Integrated Plugins

MSLib включает встроенные плагины-хуки для исправления багов и улучшения функциональности Telegram.

## 📖 Обзор

Встроенные плагины:

- 🏷️ **HashTagsFixHook** - Исправление поиска по хэштегам
- 📖 **ArticleViewerFixHook** - Отключение свайпа в Instant View
- 📞 **NoCallConfirmationHook** - Отключение подтверждения звонков
- 💬 **OldBottomForwardHook** - Старый диалог пересылки

Все плагины автоматически регистрируются при загрузке MSLib.

## 📚 Описание плагинов

### HashTagsFixHook

Исправляет поиск по хэштегам - открывает поиск "Этот чат" вместо глобального.

**Проблема:**
В оригинальном Telegram при клике на хэштег открывается глобальный поиск, что неудобно для поиска в текущем чате.

**Решение:**
Перехватывает клик на хэштег и открывает локальный поиск в текущем чате.

**Использование:**

```python
# Автоматически активируется при загрузке MSLib
# Настройки отсутствуют
```

**Как работает:**

1. Перехватывает `ChatActivityContainer.openHashtag()`
2. Получает ID текущего чата
3. Открывает поиск с параметром `searchFromUser` вместо глобального
4. Сохраняет контекст чата

**Пример кода хука:**

```python
class HashTagsFixHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=ChatActivityContainer,
            target_method="openHashtag",
            hook_strategy=HookStrategy.BEFORE
        )
    
    def before(self, param):
        # Получаем хэштег и контекст
        hashtag = param.args[0]  # String
        chat_id = self._get_current_chat_id(param)
        
        if chat_id:
            # Открываем локальный поиск
            self._open_local_search(hashtag, chat_id)
            # Блокируем оригинальный метод
            return HookResult(prevent_default=True)
        
        return HookResult()
```

**Влияние:**
- ✅ Удобнее поиск по хэштегам в чате
- ✅ Не ломает глобальный поиск (если чат не определён)
- ✅ Совместимо с другими плагинами

---

### ArticleViewerFixHook

Отключает закрытие Instant View по свайпу вниз.

**Проблема:**
В Instant View (встроенный просмотр статей) можно случайно закрыть статью свайпом вниз, что раздражает при чтении.

**Решение:**
Блокирует обработку жеста свайпа вниз в ArticleViewer.

**Использование:**

```python
# Автоматически активируется при загрузке MSLib
# Для отключения нужно удалить хук вручную
```

**Как работает:**

1. Перехватывает `ArticleViewer.onTouchEvent()`
2. Проверяет направление свайпа
3. Блокирует событие, если это свайп вниз
4. Пропускает другие жесты (скролл, зум)

**Пример кода хука:**

```python
class ArticleViewerFixHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=ArticleViewer,
            target_method="onTouchEvent",
            hook_strategy=HookStrategy.BEFORE
        )
    
    def before(self, param):
        event = param.args[0]  # MotionEvent
        
        # Проверяем тип события
        action = event.getAction()
        
        if action == MotionEvent.ACTION_MOVE:
            # Проверяем направление
            delta_y = event.getY() - self.last_y
            
            if delta_y > SWIPE_THRESHOLD:
                # Свайп вниз - блокируем
                return HookResult(prevent_default=True)
        
        self.last_y = event.getY()
        return HookResult()
```

**Влияние:**
- ✅ Невозможно случайно закрыть статью
- ⚠️ Нельзя закрыть свайпом намеренно (нужно использовать кнопку "Назад")
- ✅ Скролл и другие жесты работают нормально

---

### NoCallConfirmationHook

Отключает диалог подтверждения при звонках.

**Проблема:**
При звонке Telegram показывает диалог "Позвонить пользователю?" с кнопками "Отмена" и "Позвонить".

**Решение:**
Автоматически подтверждает звонок без показа диалога.

**Использование:**

```python
# Автоматически активируется при загрузке MSLib
# Настройки отсутствуют
```

**Как работает:**

1. Перехватывает `VoIPHelper.startCall()`
2. Проверяет, что это исходящий звонок
3. Автоматически вызывает метод подтверждения
4. Блокирует показ диалога

**Пример кода хука:**

```python
class NoCallConfirmationHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=VoIPHelper,
            target_method="startCall",
            hook_strategy=HookStrategy.BEFORE
        )
    
    def before(self, param):
        # Получаем параметры звонка
        activity = param.args[0]  # Activity
        user = param.args[1]  # TLRPC.User
        is_video = param.args[2]  # boolean
        
        # Автоматически начинаем звонок
        self._initiate_call(activity, user, is_video)
        
        # Блокируем оригинальный метод (с диалогом)
        return HookResult(prevent_default=True)
```

**Влияние:**
- ✅ Быстрее звонки (нет лишнего клика)
- ⚠️ Невозможно отменить случайный звонок через диалог
- ✅ Можно сбросить звонок сразу после начала

---

### OldBottomForwardHook

Возвращает старый стиль диалога пересылки (внизу экрана).

**Проблема:**
В новых версиях Telegram диалог пересылки открывается в центре экрана, что некоторым пользователям кажется неудобным.

**Решение:**
Заменяет новый диалог на старый вариант, который открывается внизу.

**Использование:**

```python
# Автоматически активируется при загрузке MSLib
# Настройки отсутствуют
```

**Как работает:**

1. Перехватывает создание диалога пересылки
2. Изменяет параметры layout (gravity)
3. Устанавливает анимацию появления снизу
4. Сохраняет всю функциональность

**Пример кода хука:**

```python
class OldBottomForwardHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=ShareAlert,
            target_method="onCreate",
            hook_strategy=HookStrategy.AFTER
        )
    
    def after(self, param, result):
        # Получаем диалог
        dialog = param.this_object
        window = dialog.getWindow()
        
        if window:
            # Устанавливаем gravity внизу
            layout_params = window.getAttributes()
            layout_params.gravity = Gravity.BOTTOM
            window.setAttributes(layout_params)
            
            # Устанавливаем анимацию
            window.setWindowAnimations(R.style.SlideFromBottom)
        
        return HookResult()
```

**Влияние:**
- ✅ Привычный интерфейс для пользователей старых версий
- ✅ Вся функциональность сохраняется
- ⚠️ Может конфликтовать с другими плагинами, модифицирующими диалоги

## 🎯 Примеры использования

### Пример 1: Отключение конкретного хука

```python
from MSLib import MSPlugin
from base_plugin import BasePlugin

class MyPlugin(MSPlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Получить список всех хуков MSLib
        # (это внутренняя функциональность, обычно не нужна)
        
        # Отключить хук (пример)
        # self._disable_hook("ArticleViewerFixHook")
        
        self.logger.info("My plugin loaded")
```

### Пример 2: Проверка активных хуков

```python
from MSLib import logger, command, BulletinHelper
from base_plugin import HookResult

class HookCheckerPlugin(BasePlugin):
    @command("hooks")
    def check_hooks(self, param, account):
        """Показать активные хуки MSLib"""
        
        hooks = [
            "🏷️ HashTagsFixHook - Локальный поиск хэштегов",
            "📖 ArticleViewerFixHook - Блокировка свайпа в Instant View",
            "📞 NoCallConfirmationHook - Автоподтверждение звонков",
            "💬 OldBottomForwardHook - Старый диалог пересылки"
        ]
        
        msg = "**Активные хуки MSLib:**\n\n" + "\n".join(hooks)
        BulletinHelper.show_info(msg)
        
        return HookResult()
```

### Пример 3: Создание собственного хука по аналогии

```python
from base_plugin import MethodHook, HookStrategy, HookResult
from org.telegram.ui import ChatActivity

class CustomChatHook(MethodHook):
    """Пример пользовательского хука"""
    
    def __init__(self):
        super().__init__(
            target_class=ChatActivity,
            target_method="onResume",
            hook_strategy=HookStrategy.AFTER
        )
    
    def after(self, param, result):
        """Вызывается после onResume"""
        
        # Получаем activity
        activity = param.this_object
        
        # Получаем ID чата
        dialog_id = activity.getDialogId()
        
        # Логируем
        logger.info(f"Chat opened: {dialog_id}")
        
        # Можно показать уведомление
        # BulletinHelper.show_info(f"Chat ID: {dialog_id}")
        
        return HookResult()

# Регистрация хука
class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        self.custom_hook = CustomChatHook()
        self.custom_hook.install()
        
        logger.info("Custom hook installed")
    
    def on_plugin_unload(self):
        if hasattr(self, 'custom_hook'):
            self.custom_hook.uninstall()
```

## 💡 Лучшие практики

### 1. Не удаляйте хуки без необходимости

```python
# ✅ Хорошо - хуки работают автоматически
# Ничего не нужно делать

# ❌ Плохо - удаление хуков
# self._disable_all_mslib_hooks()  # Не делайте так
```

### 2. Проверяйте совместимость

```python
# ✅ Хорошо - проверка перед модификацией
if hasattr(obj, 'method_name'):
    # Безопасная модификация
    obj.method_name()

# ❌ Плохо - прямой вызов без проверки
obj.method_name()  # Может сломаться
```

### 3. Используйте HookStrategy правильно

```python
# ✅ Хорошо - BEFORE для блокировки
class BlockingHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=SomeClass,
            target_method="someMethod",
            hook_strategy=HookStrategy.BEFORE
        )
    
    def before(self, param):
        # Проверка условия
        if should_block:
            return HookResult(prevent_default=True)
        return HookResult()

# ✅ Хорошо - AFTER для модификации результата
class ModifyingHook(MethodHook):
    def __init__(self):
        super().__init__(
            target_class=SomeClass,
            target_method="someMethod",
            hook_strategy=HookStrategy.AFTER
        )
    
    def after(self, param, result):
        # Модификация результата
        return HookResult(result=modified_result)
```

## 🐛 Troubleshooting

### Хук не работает

```python
# Проверьте, что MSLib загружен
from MSLib import get_plugin

mslib = get_plugin("mslib")
if not mslib:
    logger.error("MSLib not loaded!")

# Проверьте версию MSLib
if mslib:
    logger.info(f"MSLib version: {mslib.__version__}")
```

### Конфликт хуков

```python
# Если ваш хук конфликтует с MSLib:

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        # Загрузите ваш плагин после MSLib
        # Укажите зависимость в манифесте:
        # "dependencies": ["mslib"]
        
        # Или используйте другую стратегию
        self.my_hook = MyHook(hook_strategy=HookStrategy.AROUND)
```

### Проверка активности хука

```python
from base_plugin import MethodHook

class TestHook(MethodHook):
    def __init__(self):
        super().__init__(...)
        self.call_count = 0
    
    def before(self, param):
        self.call_count += 1
        logger.debug(f"Hook called {self.call_count} times")
        return HookResult()

# После использования
logger.info(f"Hook was called {test_hook.call_count} times")
```

## 📋 Сводка хуков

| Хук | Цель | Стратегия | Эффект |
|-----|------|-----------|--------|
| **HashTagsFixHook** | `ChatActivityContainer.openHashtag()` | BEFORE | Локальный поиск хэштегов |
| **ArticleViewerFixHook** | `ArticleViewer.onTouchEvent()` | BEFORE | Блокирует свайп для закрытия |
| **NoCallConfirmationHook** | `VoIPHelper.startCall()` | BEFORE | Автоподтверждение звонков |
| **OldBottomForwardHook** | `ShareAlert.onCreate()` | AFTER | Диалог пересылки внизу |

---

**Next:** [API Reference →](api-reference.md)
