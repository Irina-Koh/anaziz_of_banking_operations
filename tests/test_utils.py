import pytest
from src.utils import get_date_time, get_path_and_period, get_time_for_greeting
from datetime import datetime
from unittest.mock import patch

@pytest.mark.parametrize(
    "hour,expected",
    [
        (1, "Доброй ночи"),
        (9, "Доброе утро"),
        (13, "Добрый день"),
        (21, "Добрый вечер"),
    ],
)

def test_get_greeting(hour, expected):
    date = datetime(2024, 5, 22, hour, 0, 0)
    assert get_time_for_greeting(date) == expected


@pytest.mark.parametrize("date, transactions_dict, expected", [
    ("2021-02-17 12:17:15", ["01.02.2021 00:00:00", '17.02.2021 12:17:15']),
    ("2023-01-15 12:34:56", ["01.01.2023 00:00:00", "15.01.2023 12:34:56"]),
    ("2023-12-15 12:34:56", ["01.12.2023 00:00:00", "15.12.2023 12:34:56"]),
    ("12/05/2023", [])
    ])

def test_get_date_time(date, expected):
    assert get_date_time(date) == expected


@pytest.mark.parametrize("date_str, transactions_df", [
    ("2021-02-17 12:17:15", ["01.02.2021 00:00:00", '17.02.2021 12:17:15']),
    ("2023-01-15 12:34:56", ["01.01.2023 00:00:00", "15.01.2023 12:34:56"]),
    ("2023-12-15 12:34:56", ["01.12.2023 00:00:00", "15.12.2023 12:34:56"]),
    ("12/05/2023", [])
    ])
def test_get_path_and_period(transactions_df, date_str):
    get_path_and_period(path_to_file: str, time_period: list) -> pd.DataFrame:
    expected_result =  [
        {
            "last_digits": "7197",
            "total_spent": 160.89,
            "cashback": 1
        },
        {
            "last_digits": "7197",
            "total_spent": 64.00,
            "cashback": 0
        },
        {
            "last_digits": "7197",
            "total_spent": 118.12,
            "cashback": 1
        },
        {
            "last_digits": "7197",
            "total_spent": 78,
            "cashback": 0
        },
        {
            "last_digits": "nan",
            "total_spent": 20000.00,
            "cashback": 200
        }
    ]

    assert get_path_and_period(transactions_df, date_str) == expected_result


def test_get_gards_with_spend() -> None:
    get_gards_with_spend(sorted_df: DataFrame) -> list[dict]
    pass
def test_get_top_transactions() -> None:
    get_top_transactions(sorted_df: pd.DataFrame, get_top: int):
    pass
def test_get_currency() -> None:
    get_currency(path_to_json: str) -> list[dict]:
    pass
def test_get_stock() -> None:
    get_currency(path_to_json: str) -> list[dict]:
    pass
def test_analyze_categories() -> None:
    analyze_categories(path_to_file: str, year: int, month: int) -> dict:
    pass
def test_to_json() -> None:
    to_json(data: dict) -> str:
    pass
def test_report_to_file() -> None:
    report_to_file(filename=None):

    pass
def test_spending_by_category() -> None:
    spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    pass

