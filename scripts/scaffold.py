#!/usr/bin/env python
"""Создание каркаса пакетов и папок проекта adperf.

Запуск из корня проекта:
    python scripts/scaffold.py --dry-run   # только показать, что будет создано
    python scripts/scaffold.py             # создать

Скрипт идемпотентен: существующие файлы он никогда не перезаписывает,
поэтому его безопасно запускать повторно.
"""

from __future__ import annotations

import argparse
from pathlib import Path

# Корень проекта: scripts/scaffold.py -> на уровень выше папки scripts.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "adperf"

# Подпакеты: относительный путь -> (краткое название, что появится и когда).
PACKAGES: dict[str, tuple[str, str]] = {
    "config": ("Настройки и логирование.", "pydantic-settings, .env, loguru (занятия 3, 63-64)."),
    "db": ("Слой базы данных.", "Base, engine, session (занятия 6-8)."),
    "db/models": ("ORM-модели SQLAlchemy.", "Channel, Campaign, AdSpend, Lead и др. (занятия 6-7)."),
    "repositories": ("Репозитории (DAO).", "Доступ к данным без SQL в бизнес-логике (занятия 9-10)."),
    "loaders": ("Загрузка данных.", "CSV-загрузчик и генераторы (занятия 11-15)."),
    "loaders/generator": ("Генератор синтетических данных.", "Расходы, воронка (занятия 11-12)."),
    "loaders/adapters": ("Адаптеры выгрузок.", "Рекламные кабинеты, CRM, платежи (занятия 14-15)."),
    "metrics": ("Формулы метрик.", "CPL, CAC, ROMI, LTV, MRR, churn (занятия 16-21)."),
    "analytics": ("Аналитика на pandas.", "Агрегации, сравнения, когорты (занятия 22-29)."),
    "reports": ("Построение отчётов.", "Графики, HTML, экспорт (занятия 30-40)."),
    "reports/static": ("Статичные отчёты.", "Графики matplotlib в PNG (занятия 31-33)."),
    "reports/interactive": ("Интерактивные отчёты.", "Графики plotly (занятия 34-35)."),
    "cli": ("Командная строка.", "Приложение на Typer (занятия 41-47)."),
    "cli/commands": ("Команды CLI.", "import, report, compare, export (занятия 42-46)."),
    "ui": ("Веб-дашборд.", "Приложение на Streamlit (занятия 48-54)."),
    "ui/components": ("Компоненты дашборда.", "KPI-карточки, кнопки экспорта (занятия 49, 54)."),
}

# Папки в корне, которые должны попасть в Git, хотя пока пусты (через .gitkeep).
KEEP_DIRS = ["data/sample", "docs", "reports"]
# Локальные папки, которых в Git быть не должно (см. .gitignore).
LOCAL_DIRS = ["data/private"]


def write_if_missing(path: Path, content: str, dry_run: bool) -> bool:
    """Создаёт файл, только если его ещё нет. Возвращает True, если файл создан."""
    if path.exists():
        return False
    print(f"[create] {path.relative_to(ROOT)}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    """Создаёт __init__.py подпакетов, .gitkeep и локальные папки."""
    parser = argparse.ArgumentParser(description="Создание каркаса проекта adperf")
    parser.add_argument("--dry-run", action="store_true", help="ничего не создавать")
    args = parser.parse_args(argv)

    created = existing = 0
    for rel, (summary, details) in PACKAGES.items():
        # В каждом __init__.py лежит docstring: что это за пакет и что в нём будет.
        content = f'"""{summary}\n\n{details}\n"""\n'
        if write_if_missing(SRC / rel / "__init__.py", content, args.dry_run):
            created += 1
        else:
            existing += 1

    for rel in KEEP_DIRS:
        if write_if_missing(ROOT / rel / ".gitkeep", "", args.dry_run):
            created += 1
        else:
            existing += 1

    for rel in LOCAL_DIRS:
        if not args.dry_run:
            (ROOT / rel).mkdir(parents=True, exist_ok=True)
        print(f"[mkdir]  {rel}/ (локальная папка, в Git не попадёт)")

    mode = "dry-run" if args.dry_run else "done"
    print(f"Итог ({mode}): создано {created}, уже существовало {existing}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())