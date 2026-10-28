#!/usr/bin/env python
"""Проверка окружения разработки проекта adperf.

Запуск (из корня проекта, при активированном .venv):
    python scripts/check_env.py

Что проверяет:
    1. версию Python (нужен 3.11+);
    2. что виртуальное окружение активно;
    3. архитектуру процессора (на Apple Silicon ожидаем arm64);
    4. наличие git;
    5. что сам проект (adperf) установлен в editable-режиме;
    6. установленные пакеты и их минимальные версии;
    7. «дымовой» тест: pandas, matplotlib и SQLAlchemy реально работают.

Код возврата: 0 — всё хорошо, 1 — есть критические ошибки.
"""

from __future__ import annotations

import importlib.metadata as metadata
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass

MIN_PYTHON = (3, 11)

# Пакеты, которые должны быть установлены: имя дистрибутива -> минимальная версия.
RUNTIME_PACKAGES = {
    "sqlalchemy": "2.0.30",
    "alembic": "1.13",
    "pandas": "2.2",
    "numpy": "1.26",
    "plotly": "5.22",
    "matplotlib": "3.9",
    "typer": "0.12",
    "streamlit": "1.36",
    "pydantic": "2.7",
    "pydantic-settings": "2.3",
    "loguru": "0.7",
    "Faker": "25",
    "Jinja2": "3.1",
    "openpyxl": "3.1",
    "rich": "13.7",
    "PyYAML": "6",
    "Babel": "2.15",
}
DEV_PACKAGES = {
    "pytest": "8",
    "pytest-cov": "5",
    "ruff": "0.5",
    "black": "24",
    "mypy": "1.10",
    "pandas-stubs": "2.2",
    "pre-commit": "3.7",
}

OK, WARN, FAIL = "ok", "warn", "fail"
ICONS = {OK: "✅", WARN: "⚠️ ", FAIL: "❌"}


@dataclass
class Check:
    """Результат одной проверки: название, статус и пояснение."""

    name: str
    status: str
    details: str


def parse_version(text: str) -> tuple[int, ...]:
    """Превращает строку версии в кортеж чисел для сравнения.

    '2.0.36' -> (2, 0, 36); '25.1.0rc1' -> (25, 1, 0).
    Берём не более трёх числовых компонентов, суффиксы (rc, post) отбрасываем.
    """
    parts: list[int] = []
    for chunk in text.split(".")[:3]:
        match = re.match(r"\d+", chunk)
        if not match:
            break
        parts.append(int(match.group()))
    return tuple(parts)


def check_python() -> Check:
    """Версия интерпретатора должна быть не ниже MIN_PYTHON."""
    current = sys.version_info[:3]
    text = ".".join(map(str, current))
    if current >= MIN_PYTHON:
        return Check("Python", OK, f"{text} (need >= 3.11)")
    return Check("Python", FAIL, f"{text} is too old; use python3.12 to create .venv")


def check_venv() -> Check:
    """Внутри venv sys.prefix отличается от sys.base_prefix."""
    if sys.prefix != sys.base_prefix:
        return Check("Virtualenv", OK, f"active: {sys.prefix}")
    return Check("Virtualenv", FAIL, "not active; run: source .venv/bin/activate")


def check_architecture() -> Check:
    """На Apple Silicon Python должен работать нативно (arm64), а не через Rosetta."""
    machine = platform.machine()
    if platform.system() != "Darwin":
        return Check("Architecture", WARN, f"{platform.system()} {machine} (tested on macOS)")
    if machine == "arm64":
        return Check("Architecture", OK, "arm64 (Apple Silicon, native)")
    return Check("Architecture", WARN, f"{machine}: Python runs under Rosetta, use native arm64")


def check_git() -> Check:
    """Git нужен для версионирования проекта (занятие 2)."""
    path = shutil.which("git")
    if path is None:
        return Check("Git", FAIL, "not found; run: xcode-select --install")
    result = subprocess.run([path, "--version"], capture_output=True, text=True, check=False)
    return Check("Git", OK, result.stdout.strip())


def check_project() -> Check:
    """Пакет adperf должен импортироваться — значит, editable-установка прошла."""
    try:
        import adperf
    except ImportError:
        return Check("Project package", FAIL, 'cannot import adperf; run: pip install -e ".[dev]"')
    return Check("Project package", OK, f"adperf {adperf.__version__} (editable install)")


def check_package(name: str, minimum: str) -> Check:
    """Проверяет, что пакет установлен и его версия не ниже минимальной."""
    try:
        installed = metadata.version(name)
    except metadata.PackageNotFoundError:
        return Check(name, FAIL, f"not installed (need >= {minimum})")
    if parse_version(installed) >= parse_version(minimum):
        return Check(name, OK, f"{installed} (min {minimum})")
    return Check(name, FAIL, f"{installed} is too old (need >= {minimum})")


def check_smoke() -> Check:
    """Мини-тест: ключевые библиотеки не только установлены, но и работают.

    Считаем CAC на крошечном примере вручную:
        CAC = расходы / новые клиенты
        100 / 4 = 25.0,  200 / 5 = 40.0
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # рисуем без окон — стабильно на macOS и в CI
        import pandas as pd
        from sqlalchemy import create_engine, text

        df = pd.DataFrame({"spend": [100.0, 200.0], "customers": [4, 5]})
        df["cac"] = df["spend"] / df["customers"]
        assert df["cac"].tolist() == [25.0, 40.0], "pandas arithmetic is wrong"

        engine = create_engine("sqlite:///:memory:")
        with engine.connect() as conn:
            value = conn.execute(text("SELECT 1 + 1")).scalar_one()
        assert value == 2, "SQLAlchemy/SQLite query failed"
    except Exception as exc:  # noqa: BLE001 — нужно поймать любую проблему окружения
        return Check("Smoke test", FAIL, f"{type(exc).__name__}: {exc}")
    return Check("Smoke test", OK, f"pandas + matplotlib + SQLAlchemy (SQLite {sqlite3.sqlite_version})")


def main() -> int:
    """Запускает все проверки, печатает таблицу и возвращает код выхода."""
    checks = [check_python(), check_venv(), check_architecture(), check_git(), check_project()]
    checks += [check_package(n, v) for n, v in {**RUNTIME_PACKAGES, **DEV_PACKAGES}.items()]
    checks.append(check_smoke())

    print("adperf - environment check")
    print("=" * 64)
    for item in checks:
        print(f"{ICONS[item.status]} {item.name:<18} {item.details}")
    print("=" * 64)

    failed = [c for c in checks if c.status == FAIL]
    warned = [c for c in checks if c.status == WARN]
    if failed:
        print(f"Result: {len(failed)} check(s) FAILED. Fix them and run the script again.")
        return 1
    print(f"Result: all checks passed ({len(warned)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())