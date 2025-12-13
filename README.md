<div align="center">

# 🚀 MSLib

**Мощная библиотека для разработки плагинов exteraGram**

[![Version](https://img.shields.io/badge/version-1.1.0--beta-blue.svg)](LICENSE)
[![License](https://img.shields.io/badge/license-Custom-orange.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-@MiracleStudios-blue.svg)](https://t.me/MiracleStudios)

</div>

## О проекте

**MSLib** предоставляет всё необходимое для создания плагинов **exteraGram** — система команд, кеширование, локализацию, UI компоненты и встроенные улучшения Telegram.

## ⚡ Возможности

- 🎯 Система команд с автоматической регистрацией
- 🔄 Автоматическое обновление плагинов
- 📦 Эффективное кеширование данных
- 🌐 Поддержка русского и английского языков
- 🎨 UI компоненты для настроек
- 🔌 Встроенные плагины для улучшения Telegram

## 🚀 Быстрый старт

```python
from MSLib import *

# Создание команды
@command("hello", "Тестовая команда")
def hello(message):
    send_message(message.peer_id, "Привет!")

# Работа с кешем
cache = CacheFile("data.json")
cache.write({"key": "value"})
```

## 📖 Документация

Полная документация доступна в [папке docs](/docs):
- [API Reference](docs/api-reference.md)
- [Getting Started](docs/getting-started.md)
- [Встроенные плагины](docs/integrated-plugins.md)

## 📝 Лицензия

```
PLEASE DO NOT COPY THIS CODE WITHOUT NOTIFYING ME.
```

---

<div align="center">

**Версия:** 1.1.0-beta | Made with ❤️ by [Miracle Studios](https://t.me/MiracleStudios)

</div>