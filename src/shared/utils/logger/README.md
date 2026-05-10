# Logger

Логгер для нашего приложения. Есть обертка на structlog.

## Быстрый старт

```python
import structlog
from src.shared.utils.logger import LoggerConfig, configure_logger

config = LoggerConfig(
    environment="prod",
    json_output=True,
    log_file="./test.json",
    log_level="INFO",
    console_output=True,
)
configure_logger(config)
log = structlog.getLogger("demo")
log_with_bind = log.bind(key="test")
log.critical("we start")
```

Конфигурацию задаем спомощью LoggerConfig

## Разбор конфига:
Что означают поля:
- `environment` - задает окружение. Если включен `json_output` то в `dev` и `testing` окружение будет "красивый" вывод json. `Default="dev"`
- `json-output` - флаг, который задет нужно ли форматировать в json. `Default=false`
- `log_file` - **абсолютный путь** до файла. При отсутвие просто не будет писать ни в какой файл
- `console_output` - флаг, который задает нужно ли выводить в **stdin**. `Default=true`
- `time_format` - формат для отабражения времени в **формате datetime**. `Default="iso"`
- `log_level` - фильтрует логи по уровне. **ВАЖНО!!! рабоатет на уровне** `logging`. На уровне structlog нужно дополнительно **устаналвивать самим!**.
