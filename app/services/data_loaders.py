from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

from app.services.cache import ensure_file_with_cache, is_file_stale

COVID_DATA_URL = "https://www.berlin.de/lageso/_assets/gesundheit/publikationen/corona/fallzahlen_und_indikatoren.csv"


def covid_data_path(root_path: str | Path) -> Path:
    app_root = Path(root_path).resolve()
    project_root = app_root.parent
    return project_root / "static" / "assets" / "data" / "fallzahlen_und_indikatoren.csv"


def fetch_covid_csv(root_path: str | Path, *, max_age_seconds: float = 86400) -> Path:
    path = covid_data_path(root_path)

    def fetcher() -> bytes:
        response = requests.get(COVID_DATA_URL, timeout=30)
        response.raise_for_status()
        return response.content

    return ensure_file_with_cache(path, fetcher, max_age_seconds=max_age_seconds)


def load_covid_dataframe(root_path: str | Path, *, max_age_seconds: float = 86400) -> pd.DataFrame:
    path = covid_data_path(root_path)
    if not path.exists() or is_file_stale(path, max_age_seconds):
        path = fetch_covid_csv(root_path, max_age_seconds=max_age_seconds)

    data = pd.read_csv(path, sep=";", decimal=",")
    data["Datum"] = pd.to_datetime(data["Datum"], format="%d.%m.%Y")
    return data
