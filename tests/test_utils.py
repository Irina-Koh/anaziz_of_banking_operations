import pytest
from src.utils import get_date_time, get_path_and_period


@pytest.mark.parametrize("date, expected", [
    ("2021-02-17 12:17:15", ["01.02.2021 00:00:00", '17.02.2021 12:17:15']),
    ("2023-01-15 12:34:56", ["01.01.2023 00:00:00", "15.01.2023 12:34:56"]),
    ("2023-12-15 12:34:56", ["01.12.2023 00:00:00", "15.12.2023 12:34:56"]),
    ("12/05/2023", [])
    ])
def test_get_date_time(date, expected):
    assert get_date_time(date) == expected


def test_get_path_and_period(transactions_df, date_str):
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
















