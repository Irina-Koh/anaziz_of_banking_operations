from datetime import datetime, timedelta
from time import strptime
import pandas as pd
from pandas import DataFrame
import json
import requests
import pytz
from itertools import groupby
from operator import itemgetter
from functools import wraps
from typing import Optional
import logging
import os


URL = "https://api.apilayer.com/exchangerates_data/convert"
API_KEY = "S7onde8V2jerpwvAsMnPEZCRHGS00PUR"
URL_2 = "https://www.alphavantage.co/query"
API_KEY_2 = "0WEGYQ7OA78ECY4L"


# Создание директории logs, если её нет
os.makedirs("./logs", exist_ok=True)

# Получаем экземпляр логгера
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
# Настройка файлового обработчика
file_handler = logging.FileHandler(filename="./logs/utils.log", encoding="utf-8", mode="w")
file_formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formater)
# Регистрируем обработчик
logger.addHandler(file_handler)


def get_time_for_greeting():
    """
    Функция возращает приветствие в зависимости от текущего времени
    """
    user_datetime = datetime.now()
    hour = user_datetime.hour
    if 5 <= hour < 12:
        return 'Доброе утро'
    elif 12 <= hour < 18:
        return 'Добрый день'
    elif 18 <= hour < 23:
        return 'Добрый вечер'
    else:
        return 'Доброй ночи'


def get_date_time(date_time, date_format='%Y-%m-%d %H:%M:%S') -> list[str]:
    try:
        dt = datetime.strptime(date_time, date_format)
        start_of_month = dt.replace(day=1, hour=0, minute=0, second=0)
        return [
            start_of_month.strftime('%d.%m.%Y %H:%M:%S'),
            dt.strftime('%d.%m.%Y %H:%M:%S')
        ]
    except ValueError as ve:
        logger.error(f"Неверный формат даты: {ve}")
        return []
    except Exception as e:
        logger.critical(f"Произошла неизвестная ошибка: {e}")
        return []


def get_path_and_period(path_to_file: str, period_data: list) -> pd.DataFrame:
    """
    Функция принимает путь к Excel файлу и список дат, и возвращает таблицу в заданном периоде.
    """
    try:
        # Чтение данных из Excel файла
        logger.info(f"Считывание данных из файла: {path_to_file}, лист 'Отчет по операциям'")
        df = pd.read_excel(path_to_file, sheet_name='Отчет по операциям')

        # Преобразование столбца с датой операций в формат datetime
        logger.info("Преобразование столбца 'Дата операции' в формат datetime")
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

        # Разбор начальных и конечных дат из списка period_data
        logger.info(f"Разбор дат: {period_data}")
        start_date = datetime.strptime(period_data[0], '%d.%m.%Y %H:%M:%S')
        end_date = datetime.strptime(period_data[1], '%d.%m.%Y %H:%M:%S')

        # Фильтрация по указанным датам
        logger.info(f"Фильтрация данных за период: {start_date} - {end_date}")
        filtered_df = df[
            (df['Дата операции'] >= start_date) &
            (df['Дата операции'] <= end_date)
        ]

        # Сортировка результатов по дате операции
        logger.info("Сортировка результата по дате операции")
        sorted_df = filtered_df.sort_values(by='Дата операции', ascending=True)

        return sorted_df

    except FileNotFoundError:
        logger.error(f"Файл '{path_to_file}' не найден.")
        return None
    except ValueError as err:
        logger.error(f"Ошибка разбора даты: {err}")
        return None
    except Exception as err:
        logger.error(f"Неконтролируемая ошибка: {err}")
        return None


def get_gards_with_spend(sorted_df: DataFrame) -> list[dict]:
    '''
        Функция принимает DataFrame и возвращает список карт с расходами
    '''
    # Логируем входящий аргумент
    logger.info(f'Получили DataFrame размером {len(sorted_df)} строк.')

    card_spend_transactions = []
    card_sorted = sorted_df[
        [
            "Номер карты",
            "Сумма операции",
            "Кэшбэк",
            "Сумма операции с округлением"
        ]
    ]

    # Логируем сортировку столбцов
    logger.info('Отсортируем необходимые колонки.')

    for index, row in card_sorted.iterrows():
        if row['Сумма операции'] < 0:
            last_digits = str(row['Номер карты']).replace("*", "")

            # Проверка корректности суммы операций
            try:
                total_spent = float(row['Сумма операции с округлением'])
            except ValueError as e:
                logger.error(f'Ошибка преобразования строки "{row["Сумма операции с округлением"]}" в число: {e}')
                continue

            cashback = int(total_spent / 100)

            # Создаем словарь транзакций
            transaction_row = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback
            }

            # Добавляем транзакцию в итоговый список
            card_spend_transactions.append(transaction_row)

            # Логируем каждую операцию расхода
            logger.info(
                f'Обработана операция с картой №{last_digits}, сумма расхода: {total_spent}. Полученный кэшбек: {cashback}')

    # Возвращаем финальный список транзакций
    logger.info(f'Возвращено {len(card_spend_transactions)} записей расходов.')
    return card_spend_transactions


def get_top_transactions(sorted_df: pd.DataFrame, get_top: int):
    '''
    Функция принимает DataFrame и возвращает топ-транзакций по сумме платежа
    '''
    # Проверка типа аргументов
    if not isinstance(sorted_df, pd.DataFrame):
        raise TypeError("Первый аргумент должен быть объектом Pandas DataFrame.")
    if not isinstance(get_top, int) or get_top <= 0:
        raise ValueError("Второй аргумент должен быть положительным целым числом.")

    # Логи входящего аргумента
    logger.info(f'Получили DataFrame размером {len(sorted_df)} строк и значение get_top={get_top}.')

    top_pay_transations = []
    try:
        # Отсортировываем DataFrame по 'Сумме операции'
        sorted_pay_df = sorted_df.sort_values(by='Сумма операции', ascending=False)

        # Логируем сортировку
        logger.info('Отсортировали транзакции по убыванию суммы.')

        # Выбираем верхние записи
        top_transations = sorted_pay_df.head(get_top)

        # Логируем выбор верхних N транзакций
        logger.info(f'Выбираем первые {get_top} транзакций.')

        # Оставляем нужные поля
        top_pay_transations_sorted = top_transations[
            ["Дата платежа", "Сумма операции", "Категория", "Описание"]
        ]

        # Формируем список объектов
        for index, row in top_pay_transations_sorted.iterrows():
            transation = {
                "data": f"{row['Дата платежа']}",
                "amount": f"{row['Сумма операции']}",
                "category": f"{row['Категория']}",
                "description": f"{row['Описание']}"
            }
            top_pay_transations.append(transation)

            # Логируем обработку каждой транзакции
            logger.info(
                f'Обработали транзакцию: дата - {transation["data"]}, '
                f'сумма - {transation["amount"]}, '
                f'категория - {transation["category"]}, '
                f'описание - {transation["description"]}'
            )
    except KeyError as ke:
        logger.error(f'Ошибочный ключ в DataFrame: {ke}')
        raise
    except Exception as ex:
        logger.error(f'Неожиданная ошибка: {ex}')
        raise

    # Логируем успешное завершение функции
    logger.info(f'Вернули {len(top_pay_transations)} записей топ-транзакций.')
    return top_pay_transations

def get_currency(path_to_json: str) -> list[dict]:
    """
    Функция принимает путь к файлу JSON и возвращает курсы валют относительно RUB.
    """
    currency_rates = []

    try:
        # Чтение файла JSON
        with open(path_to_json, 'r', encoding="utf-8") as file:
            data = json.load(file)
            currencies = data.get('user_currencies')  # Используйте метод .get() для безопасности
            if not currencies:
                logger.warning("Нет данных о валютах в файле")
                return []

            # Обрабатываем валюты одну за одной
            for currency in currencies:
                # Параметры запроса
                params = {
                    "amount": 1,
                    "from": currency,
                    "to": "RUB"
                }
                headers = {"apikey": API_KEY}

                # Отправляем GET-запрос
                response = requests.get(URL, headers=headers, params=params)
                status_code = response.status_code

                if status_code != 200:
                    logger.error(f"Ошибка HTTP ({status_code}) при получении курса для {currency}")
                    continue

                # Парсим JSON ответ
                result = response.json()
                currence_code_response = result.get("query", {}).get("from")
                currence_amount = result.get("rates", {}).get("RUB")

                if currence_code_response is None or currence_amount is None:
                    logger.error(f"Некорректный ответ сервера для валюты {currency}: {response.text}")
                    continue

                # Добавляем полученный курс в список
                currency_rates.append({
                    "currency": currence_code_response,
                    "rate": currence_amount
                })

                logger.info(f"Успешно получили курс для {currency}: {currence_amount} руб.")

    except FileNotFoundError:
        logger.error(f"Файл '{path_to_json}' не найден!")
    except json.JSONDecodeError:
        logger.error(f"Ошибка парсинга JSON-файла: файл '{path_to_json}' поврежден или неверного формата.")
    except requests.RequestException as req_err:
        logger.error(f"Произошла ошибка при отправке запроса: {req_err}")
    except Exception as err:
        logger.error(f"Необработанная ошибка: {err}")

    return currency_rates

def get_stock(path_to_json: str):
    """
    Функция получает котировки акций из указанного файла JSON.
    """
    stock_rates = []
    try:
        # Открываем файл и загружаем данные
        with open(path_to_json, 'r', encoding="utf-8") as file:
            data = json.load(file)
            stocks = data.get('user_stocks', [])
            if not stocks:
                logger.warning("Список акций пуст! Пожалуйста, проверьте данные в файле.")
                return []

            # Проходим по каждому символу акции
            for stock in stocks:
                # Форматируем параметры запроса
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": stock,
                    "apikey": API_KEY_2,
                    "outputsize": "compact",  # Ограничиваем объем данных
                    "datatype": "json"
                }

                # Выполняем запрос
                response = requests.get(URL_2, params=params)
                status_code = response.status_code

                if status_code != 200:
                    logger.error(f"Ошибка при загрузке данных для акции {stock}: "
                                  f"HTTP-статус-код {status_code}, Ответ: {response.text[:100]}...")
                    continue

                # Преобразование ответа в JSON
                r = response.json()
                print(r)

                # Определяем вчерашнюю дату
                local_time = datetime.now()
                yesterday = local_time - timedelta(days=1)
                date_str = yesterday.strftime('%d.%m.%Y')

                # Извлекаем цену закрытия за предыдущий день
                closing_price = r.get("Time Series (Daily)", {}).get(date_str, {}).get('4. close')

                if closing_price is None:
                    logger.error(f"Не найдена цена закрытия для акции {stock} на дату {date_str}. "
                                  f"Данные от API: {r.keys()} ")
                    continue

                # Конвертируем цену в число и добавляем в результат
                stocks_code_response = float(closing_price)
                stocks_amount = stocks_code_response

                stock_rates.append({
                    "stock": stock,
                    "price": stocks_amount
                })

                logger.info(f"Акция {stock}: Цена закрытия {yesterday.date()} составляет {stocks_amount:.2f} USD.")

    except FileNotFoundError:
        logger.error(f"Файл '{path_to_json}' не найден.")
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON-файла '{path_to_json}'. Возможно, файл поврежден или имеет неправильный формат.")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Ошибка отправки запроса: {req_err}")
    except Exception as err:
        logger.error(f"Непредвиденная ошибка: {err}")


def analyze_categories(path_to_file: str, year: int, month: int) -> dict:
    '''
    Функция для анализа категорий платежей
    '''
    try:
        # Читаем Excel-файл
        df = pd.read_excel(path_to_file)
        logger.info(f"Загружен файл {path_to_file}. Количество строк: {len(df)}.")

        # Переводим в формат списка словарей
        data = df.to_dict('records')

        # Проверка правильности указанных года и месяца
        if year < 1900 or month < 1 or month > 12:
            raise ValueError("Недопустимые значения года или месяца.")

        # Фильтрация данных по году и месяцу
        filtered_data = filter(lambda x: (
                datetime.strptime(x['Дата операции'], "%d.%m.%Y %H:%M:%S").year == year and
                datetime.strptime(x['Дата операции'], "%d.%m.%Y %H:%M:%S").month == month
        ), data)

        # Сортируем данные по категориям для последующей группировки
        sorted_data = sorted(filtered_data, key=itemgetter('Категория'))

        # Группировка данных по категориям
        grouped_data = groupby(sorted_data, key=itemgetter('Категория'))

        # Подсчет общей суммы расходов и кэшбэков
        result = {}
        for category, transactions in grouped_data:
            # Сумма платежей по группе транзакций
            total_spent = sum(map(itemgetter('Сумма платежа'), transactions))

            # Рассчитываем кэшбэк только для отрицательных трат
            if total_spent <= 0:
                cashback = int(total_spent // 100 * (-1))
                result[category] = cashback

        logger.info(f"Анализ выполнен успешно. Результат включает {len(result)} категорий.")
        return result

    except FileNotFoundError:
        logger.error(f"Файл {path_to_file} не найден.")
        return {}
    except pd.errors.EmptyDataError:
        logger.error(f"Файл {path_to_file} пуст или содержит недопустимый формат данных.")
        return {}
    except ValueError as ve:
        logger.error(f"Ошибка в данных: {ve}")
        return {}
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return {}


# Функция для преобразования результата в JSON
def to_json(data: dict) -> str:
    try:
        json_result = json.dumps(data, indent=4, ensure_ascii=False)
        logger.info("Результат успешно сериализован в JSON.")
        return json_result
    except json.JSONDecodeError as jde:
        logger.error(f"Ошибка при сериализации в JSON: {jde}")
        return "{}"
    except Exception as e:
        logger.error(f"Неизвестная ошибка при сериализации: {e}")
        return "{}"


# Декоратор для автоматического сохранения отчета в файл
def report_to_file(filename=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Определим имя файла, используя корректный формат даты и времени
            if isinstance(filename, str):
                file_name = filename
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"{func.__name__}_{timestamp}.txt"

            try:
                with open(file_name, 'w') as f:
                    f.write(result.to_string())
                logger.info(f"Отчет сохранен в файл: {file_name}")
            except OSError as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
                raise

            return result

        return wrapper
    return decorator


@report_to_file()  # Использует автоматический способ формирования имени файла
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    '''
         Основная функция для расчета расходов по определенной категории
    '''
    try:
        # Преобразуем строку даты в объект datetime
        if date:
            current_date = datetime.strptime(date, "%d.%m.%Y")
        else:
            current_date = datetime.now()

        # Устанавливаем начало периода (за последние 3 месяца)
        start_date = current_date - timedelta(days=90)
        formatted_start_date = start_date.strftime('%d.%m.%Y')
        # Проверяем наличие нужного столбца в таблице
        if 'Дата платежа' not in transactions.columns:
            raise ValueError("Колонка 'Дата платежа' отсутствует в данных.")

        # Преобразуем колонку дат в формат datetime
        transactions['Дата платежа'] = pd.to_datetime(transactions['Дата платежа'], dayfirst=True)

        # Фильтруем транзакции по указанной категории и временному интервалу
        filtered_by_category = transactions[transactions['Категория'] == category]
        relevant_transactions = filtered_by_category[
            (filtered_by_category['Дата платежа'] >= start_date) &
            (filtered_by_category['Дата платежа'] <= current_date)
            ]

        # Группируем и суммируем расходы
        summary = relevant_transactions.groupby('Дата платежа').sum()['Сумма платежа']

        logger.info(f"Итоговый отчет по категории '{category}' подготовлен.")
        return summary
    except ValueError as ve:
        logger.error(f"Ошибка обработки данных: {ve}")
        raise
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        raise

