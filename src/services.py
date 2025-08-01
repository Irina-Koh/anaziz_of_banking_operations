from src.utils import analyze_categories, to_json

def profitable_cashback_categories(year: int, month: int):
    analysis_result = analyze_categories("./data/operations.xlsx", year=year , month=month)
    analysis_result_json = to_json(analysis_result)
    return analysis_result_json



