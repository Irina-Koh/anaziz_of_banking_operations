from black import datetime
from src.views import main_info
from pprint import pprint
from src.services import profitable_cashback_categories
from src.reports import spending_report_by_category



if __name__ == "__main__":
    print(main_info('2018-05-20 15:30:00'))
    print(profitable_cashback_categories(2020, 1))
    print(spending_report_by_category("Супермаркеты", "13.05.2018"))