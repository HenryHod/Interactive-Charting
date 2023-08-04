from fredapi import Fred
import nasdaqdatalink as ndl
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas_datareader.fred import FredReader
from re import findall
import time
fred = Fred(api_key="179a8a574defbe5d2bb69cc07b59beb2")
ndl.ApiConfig.api_key = "HP2mLCTfC38KJsseJSos"
periods_dict = {"max": datetime.strptime("1970-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
                    "10y": datetime.now() + relativedelta(years=-10),
                    "5y": (datetime.now() + relativedelta(years=-5)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "2y": (datetime.now() + relativedelta(years=-2)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "1y": (datetime.now() + relativedelta(years=-1)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "ytd": datetime.strptime(f"{datetime.now().strftime('%Y')}-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
                    "6mo": (datetime.now() + relativedelta(months=-6)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "3mo": (datetime.now() + relativedelta(months=-3)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "1mo": (datetime.now() + relativedelta(months=-1)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "5d": (datetime.now() + relativedelta(days=-5)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "1d": (datetime.now() + relativedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%S")}
def data_grabber(series, database, start_date=None, end_date=None, interval=None, period=None):
    if database == "FRED":
        if period is None:
            if interval is not None:
                try:
                    series_df = FredReader(series, start=start_date, end=end_date, freq=interval).read()
                except Exception as e:
                    print(e)
                    series_df = fred.get_series(series, observation_start=start_date[:10], observation_end=end_date[:10])
            else:
                series_df = FredReader(series, start=start_date, end=end_date).read()
                #series_df = fred.get_series(series, observation_start=start_date[:10], observation_end=end_date[:10])

        else:
            if interval is not None:
                try:
                    print(type(periods_dict[period]), periods_dict[period])
                    series_df = FredReader(series, start=periods_dict[period], freq=interval).read()
                    #series_df = fred.get_series(series, observation_start=periods_dict[period], frequency=interval)
                except Exception as e:
                    print(e)
                    series_df = fred.get_series(series, observation_start=periods_dict[period])
            else:
                print(type(periods_dict[period]), periods_dict[period])
                series_df = FredReader(series, start=periods_dict[period]).read()
                #series_df = fred.get_series(series, observation_start=periods_dict[period])
        series_df = series_df.reset_index().rename({"DATE": "Date", series: "Close"}, axis=1)
        return series_df
    else:
        ndl_start = time.time()
        if period is None:
            series_df = ndl.get(f"{database}/{series}", start_date=start_date[:10], end_date=end_date[:10],
                                collapse=interval)
        else:
            print(type(periods_dict[period]), periods_dict[period])
            series_df = ndl.get(f"{database}/{series}", start_date=periods_dict[period], collapse=interval)
        series_df = series_df.reset_index().rename(
            {column: "Close" for column in ["Value", "Prev. Day Open Interest", "Last"]}, axis=1)
        series_df = series_df.rename({series_df.columns[0]:"Date"}, axis = 1)
        if series_df.shape[1] >= 2 and "Close" not in series_df.columns:
            series_df = series_df.rename({series_df.columns[1]:"Close"}, axis = 1)
        ndl_end = time.time()
        print("ndl time:", ndl_end - ndl_start)
        print(series_df)
        return series_df


def get_smallest_frequency(series):
    try:
        ser_df = fred.get_series(series, frequency="d")
        print("worked")
    except Exception as e:
        matches = findall("'(\w+)'", str(e))
        return matches
        