import json
from typing import Dict, Any

from openpyxl.styles.builtins import currency_0

from src.utils import (
    get_time_for_greeting,
    get_date_time,
    get_path_and_period,
    get_gards_with_spend,
    get_top_transactions,
    get_currency,
    get_stock)


def main_info(date_time) -> Dict[str, Any]:
    '''
        Реализуйте набор функций и главную функцию, принимающую на вход строку с датой и временем в формате
        YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ со следующими данными:
    '''

    greeting = get_time_for_greeting()
    # делаем срез экселя на определенный диапозон
    time_period = get_date_time(date_time)
    sorted_df = get_path_and_period("./data/operations.xlsx", time_period)
    cards = get_gards_with_spend(sorted_df)
    top_transactions = get_top_transactions(sorted_df, 5)
    currency_rates = get_currency("./data/user_settings.json")
    stocks_prices = get_stock("./data/user_settings.json")
    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stocks_prices": stocks_prices
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data
