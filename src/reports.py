import pandas as pd
from src.utils import spending_by_category


def spending_report_by_category(category: str, date: str = None):
    data = pd.read_excel("./data/operations.xlsx")
    df = pd.DataFrame(data)
    result_default = spending_by_category(df, date=date, category=category)
    return result_default
