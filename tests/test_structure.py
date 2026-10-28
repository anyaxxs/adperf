"""Тест структуры проекта: все подпакеты на месте, импортируются и описаны.

Запуск:  pytest -q
Тест страхует от двух типичных ошибок: забытого __init__.py и случайного
попадания папки с кодом под правила .gitignore (тогда на другом компьютере
пакет просто не найдётся).
"""

from __future__ import annotations

import importlib
import pkgutil

import adperf

# Полный перечень подпакетов, которые создаёт scripts/scaffold.py.
EXPECTED_PACKAGES = {
    "adperf.config",
    "adperf.db",
    "adperf.db.models",
    "adperf.repositories",
    "adperf.loaders",
    "adperf.loaders.generator",
    "adperf.loaders.adapters",
    "adperf.metrics",
    "adperf.analytics",
    "adperf.reports",
    "adperf.reports.static",
    "adperf.reports.interactive",
    "adperf.cli",
    "adperf.cli.commands",
    "adperf.ui",
    "adperf.ui.components",
}


def _all_packages() -> set[str]:
    """Находит все подпакеты adperf, обходя дерево src/adperf."""
    found = pkgutil.walk_packages(adperf.__path__, prefix="adperf.")
    return {module.name for module in found if module.ispkg}


def test_version_has_three_numeric_parts() -> None:
    """Версия имеет вид X.Y.Z (например, 0.1.0)."""
    parts = adperf.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_expected_packages_exist() -> None:
    """Все запланированные подпакеты присутствуют."""
    missing = EXPECTED_PACKAGES - _all_packages()
    assert not missing, f"Не найдены подпакеты: {sorted(missing)}"


def test_all_packages_importable_and_documented() -> None:
    """Каждый подпакет импортируется и содержит docstring."""
    for name in sorted(_all_packages()):
        module = importlib.import_module(name)
        assert module.__doc__, f"У пакета {name} нет docstring"