from data_grabber_func import data_grabber, get_smallest_frequency
def series_interval(database, series):
    if database == "FRED":
        valid_freq = get_smallest_frequency(series)
        all_freq = [{'label': '1d', 'value': 'd'}, {'label': '5d', 'value': 'w'}, {'label': '10d', 'value': 'bw'},
                    {'label': '1mo', 'value': 'm'}, {'label': '3mo', 'value': 'q'}, {'label': '6mo', 'value': 'sa'},
                    {'label': '1y', 'value': 'a'}]
        if valid_freq is None:
            return all_freq
        else:
            return [all_freq[i] for i in range(len(all_freq)) if all_freq[i]["value"] in valid_freq]
from data_grabber_func import data_grabber, get_smallest_frequency
def series_interval(database, series):
    if database == "FRED":
        valid_freq = get_smallest_frequency(series)
        all_freq = [{'label': '1d', 'value': 'd'}, {'label': '5d', 'value': 'w'}, {'label': '10d', 'value': 'bw'},
                    {'label': '1mo', 'value': 'm'}, {'label': '3mo', 'value': 'q'}, {'label': '6mo', 'value': 'sa'},
                    {'label': '1y', 'value': 'a'}]
        if valid_freq is None:
            return all_freq
        else:
            return [all_freq[i] for i in range(len(all_freq)) if all_freq[i]["value"] in valid_freq]

    elif database == "YF":
        return ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"]
    else:
        return [{"label": "1d", "value": "daily"}, {"label": "5d", "value": "weekly"},
                {"label": "1mo", "value": "monthly"}, {"label": "3mo", "value": "quarterly"},
                {"label": "1y", "value": "annual"}]
def has_candle(series, database):
    if database != "FRED":
        ser_df_columns = data_grabber(series, database, period="1y").columns
        return "High" in ser_df_columns and "Low" in ser_df_columns
    return False
def one_month(database):
    if database == "FRED":
        return "m"
    elif database == "YF":
        return "1mo"
    else:
        return "monthly"