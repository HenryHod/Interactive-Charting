<<<<<<< HEAD
# %%
from datetime import datetime
import yaml
import numpy as np
import plotly.graph_objects as go
import plotly.subplots
from dash import Dash, Output, Input, ALL, html, dcc, callback_context, no_update
from data_grabber_func import data_grabber
from sql_comm import get_parent_cat, get_sub_cat, get_ser_options, search_all_ser, get_ser_dict
import time

app = Dash(__name__, external_stylesheets=["int_chart.css"], suppress_callback_exceptions=True)
server=app.server
app.layout = html.Div([
    dcc.Store(data={"1m": 1, "2m": 2, "5m": 5, "15m": 15, "30m": 30, "60m": 60, "90m": 90,
                "1d": 1440, "5d": 5 * 1440, "1wk": 7 * 1440, "10d": 10 * 1440,
                "1mo": 30 * 1440, "3mo": 90 * 1440, "6mo": 180 * 1440, "1y": 360 * 1440},
                id="options_dict"),
    dcc.Store(data=['#CC9900', '#548DD4', '#FFCC00', '#00203e', '#386295', '#17365D'], id="colors"),
    dcc.Store(data=[], id="all series"),
    dcc.Store(id="ser_del_index"),
    dcc.Loading([
    html.Div([
        html.Div([
            html.Div([html.H3("Select Series Group:"),
                    dcc.Dropdown(
                        id="parent category dropdown",
                        options=get_parent_cat(),
                        clearable=True,
                        multi=False,
                        optionHeight=30
                    )
                    ], id="parent category choice"),
            html.Div([html.H3("Select Series Category:"),
                    dcc.Dropdown(
                        id="category dropdown",
                        options=[],
                        clearable=True,
                        multi=False,
                        optionHeight=30
                    )
                    ], id="category choice", style={"display": "none"}),
            html.Div([html.H3("Select Series:"),
                    dcc.Dropdown(
                        id="series dropdown",
                        options=[],
                        clearable=True,
                        optionHeight=30
                    )
                    ], id="series choice", style={"display": "none"})
        ], style={"display": "flex"}, id="dropdown_search"),
        html.Div(children=[
            html.H3("Search All Series:"),
            html.Div([
                dcc.Input(style={'resize': 'none'}, id="search_text", type="text", spellCheck='false', debounce=True),
                html.Button(["Search"], id="search_button")
            ], id="search_bar"),
            dcc.Dropdown(id="search_result", options=[],
                        optionHeight=30, style={'display': 'none'})]
            , id="search_series")
    ], id="series_selection")]),
    html.Div(
        [html.Div(id="ticker_preferences", className="menu", style={"display": "none"}),
        html.A(href="#ticker_preferences", id="ticker_preferences_icon"),
        dcc.Loading([dcc.Graph(id="graph", config={'displaylogo': False})], type="graph")], id="figure")
], id="master")
@app.callback(
    Output("ticker_preferences", "children"),
    Output("ticker_preferences_icon", "children"),
    Output("category dropdown", "options"),
    Output("series dropdown", "options"),
    Output("category choice", "style"),
    Output("series choice", "style"),
    Output("all series", "data"),
    Output("ticker_preferences", "style"),
    Output("search_result", "options"),
    Output("search_result", "style"),
    Output("ser_del_index", "data"),
    Input("parent category dropdown", "value"),
    Input("category dropdown", "value"),
    Input("series dropdown", "value"),
    Input("search_result", "value"),
    Input("search_button", "n_clicks"),
    Input("search_text", "value"),
    Input("category dropdown", "options"),
    Input("series dropdown", "options"),
    Input("all series", "data"),
    Input("ticker_preferences", "children"),
    Input({"type": "ticker_close", "index": ALL}, "n_clicks"))
def div_maker(parent, category, series_selection, search_series_selection, search_button_clicks, search_bar_input, cat_options, ser_options, all_series,
            ticker_preferences,
            close_clicks):
    ctx = callback_context
    callback_id = ctx.triggered[0]['prop_id'].split(".")[0]
    div_list = []
    link = []
    search_selection = callback_id == "search_result" and search_series_selection is not None
    search_result_options = []
    search_display = {"display": "none"}
    cat_display = {"display": "none"}
    ser_display = {"display": "none"}
    menu_display = {"display": "none"}
    ser_del_index = None
    if callback_id == "search_button" or callback_id == "search_text":
        search_display = {"display": "block"}
        search_result_options = search_all_ser(search_bar_input)
    if callback_id == "parent category dropdown" or callback_id == "category dropdown":
        if callback_id == "parent category dropdown":
            category = None
        series_selection = None
    if parent is not None or search_selection:
        if not search_selection:
            cat_options = get_sub_cat(parent)
            cat_display = {"display": "block"}
        if category is not None or search_selection:
            if not search_selection:
                ser_options = get_ser_options(category)
                ser_display = {"display": "block"}
            if series_selection is not None or search_selection:
                if search_selection:
                    series_selection = search_series_selection
                series_dict, ser_name = get_ser_dict(series_selection)
                database = series_dict[series_selection]
                if str(series_dict) not in all_series:
                    print(series_selection)
                    if all_series is None:
                        all_series = [str(series_dict)]
                    else:
                        all_series.append(str(series_dict))
                    if len(all_series) == 1:
                        div_list = [html.A(href="#", id="close")]
                    def series_interval(database):
                        if database == "FRED":
                            return [{"label": "1d", "value": "d"}, {"label": "5d", "value": "w"}, {"label": "10d", "value": "bw"},
                                    {"label": "1mo", "value": "m"}, {"label": "3mo", "value": "q"}, {"label": "6mo", "value": "sa"},
                                    {"label": "1y", "value": "a"}]
                        elif database == "YF":
                            return ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"]
                        else:
                            return [{"label": "1d", "value": "daily"}, {"label": "5d", "value": "weekly"},
                                    {"label": "1mo", "value": "monthly"}, {"label": "3mo", "value": "quarterly"},
                                    {"label": "1y", "value": "annual"}]
                    def has_candle(series, database):
                        ser_df_columns = data_grabber(series, database, period="max").columns
                        return "High" in ser_df_columns and "Low" in ser_df_columns
                    div_list.append(html.Div([

                        html.Button('X', className="ticker_menu_close",
                                    id={"type": "ticker_close", "index": len(all_series) - 1},
                                    n_clicks=0),
                        html.H3(series_selection + ": " + ser_name, id="ticker_title"),

                        html.Div([
                            html.Div([html.Div([
                                dcc.DatePickerRange(className="date_range_picker",
                                                    id={"type": "date_picker", "index": len(all_series) - 1},
                                                    min_date_allowed=datetime.strptime("1970-01-01T00:00:00",
                                                                                    "%Y-%m-%dT%H:%M:%S")),
                                html.A(children=[html.Img(src="/assets/calendar.png", className="calendar_png")])]
                                , id="calendar_div" + str(len(all_series) - 1), className="date_picker_div")] +
                                    [(html.Button(period, id=dict(type="period_btn", index=a * (len(all_series))),
                                                className="period_button") if period != "max" else html.Button(
                                        period, id={"type": "period_btn", "index": a}, className="period_button",
                                        autoFocus=True, n_clicks=1))
                                    for a, period in
                                    enumerate(
                                        ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"])
                                    ], id={"type": "period_select", "index": len(all_series) - 1},
                                    className="period_buttons_container " + str(len(all_series) - 1)),

                            html.Div([

                                html.Div([
                                    html.H6("Interval:", className="interval_title"),
                                    dcc.Dropdown(id={"type": "interval_select", "index": len(all_series) - 1},
                                                options=series_interval(database), value="1d", clearable=False,
                                                searchable=False,
                                                className="interval_select")
                                ], className="option",
                                    style={"display": "block"}),

                                html.Div([
                                    html.H6("Line Type:", className="line_title"),
                                    dcc.Dropdown(clearable=False, searchable=False, className="line_select",
                                                id={"type": "line_type", "index": len(all_series) - 1},
                                                options=["Linear", "Area", "Candle"] if has_candle(series_selection,
                                                                                                    database) else [
                                                    "Linear", "Area"]
                                                , value="Linear")
                                ], className="option"),

                                html.Div([
                                    html.H6("Transform:", className="transform_title"),
                                    dcc.Dropdown(searchable=False, clearable=False,
                                                id={"type": "transform", "index": len(all_series) - 1},
                                                className="transform_select",
                                                options=["Level", "Natural Log", "Change", "%Change", "Cumulative",
                                                        "%Cumulative"],
                                                value="Level")
                                ], className="option"),

                                html.Div([
                                    (dcc.Checklist(id={"type": "axis", "index": len(all_series)},
                                                className="axis_select",
                                                labelStyle=dict(display="block"),
                                                options=["Secondary Y-axis", "Secondary X-axis"], value=["None"],
                                                style={"padding": "0px 10px"}))], className="axis_option"
                                )], className="options_list")])], className="ticker_menu",
                        id={"type": "ticker", "index": len(all_series) - 1}, title=series_selection))
    if "ticker_close" in callback_id:
        if len(all_series) > 1:
            print(all_series)
            for index in range(len(all_series)):
                if close_clicks[index] >= 1:
                    all_series.pop(index)
                    ticker_preferences.pop(index + 1)
                    ser_del_index = index
        else:
            all_series = []
            ticker_preferences = []
            link = []
            ser_del_index = 0
    if ticker_preferences is None:
        ticker_preferences = div_list
    else:
        ticker_preferences = ticker_preferences + div_list
    if len(all_series) > 0:
        menu_display = {}
        link = [html.Img(src="/assets/hamburger.png", id="hamburger")]
    print("close clicks: ", close_clicks, "ticker_preferences: ", len(ticker_preferences))
    return ticker_preferences, link, cat_options, ser_options, cat_display, ser_display, all_series, menu_display, search_result_options, search_display, ser_del_index


@app.callback(Output({"type": "interval_select", "index": ALL}, "value"),
            Output({"type": "interval_select", "index": ALL}, "options"),
            Output({"type": "date_picker", "index": ALL}, "start_date"),
            Output({"type": "date_picker", "index": ALL}, "end_date"),
            Input("all series", "data"),
            Input({"type": "interval_select", "index": ALL}, "options"),
            Input({"type": "period_btn", "index": ALL}, "n_clicks"),
            Input({"type": "period_btn", "index": ALL}, "children"),
            Input({"type": "date_picker", "index": ALL}, "start_date"),
            Input({"type": "date_picker", "index": ALL}, "end_date"),
            Input("options_dict", "data")
            )
def interval_defaults(seriess_dicts, all_options, button_clicks, buttons, start_dates, end_dates, options_dict):
    ctx = callback_context
    callback_id = ctx.triggered[0]['prop_id'].split(".")[0]
    print(button_clicks)
    new_interval_choices = []
    new_full_options_list = []
    for i, series_dict in enumerate(seriess_dicts):
        options = all_options[i]
        options_time = [options_dict[option['label']] for option in options]
        print(options_time)
        series_dict = yaml.safe_load(series_dict)
        series = list(series_dict.keys())[0]
        database = series_dict[series]
        if "date_picker" in callback_id:
            print("use date")
            if len(start_dates[i]) == 10:
                start_dates[i] += "T00:00:00"
            if len(end_dates[i]) == 10:
                end_dates[i] += "T00:00:00"
            start_date = datetime.strptime(start_dates[i], "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_dates[i], "%Y-%m-%dT%H:%M:%S")
        elif ("period_btn" in callback_id and i * 11 < eval(callback_id)["index"] < (i + 1) * 11) or any(
                button_clicks[i * 11:(i + 1) * 11]):
            print("use period")
            print("callback_id")
            button_name = "max" if "period_btn" not in callback_id else buttons[eval(callback_id)["index"]]
            print(button_name)
            ser_df = data_grabber(series, database, period=button_name)
            x_data = ser_df["Date"]
            start_date = x_data[0] if x_data[0] > datetime.strptime("1970-01-01T00:00:00",
                                                                    "%Y-%m-%dT%H:%M:%S") else datetime.strptime(
                "1970-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
            end_date = x_data[len(x_data) - 1]
            start_dates[i] = start_date
            end_dates[i] = end_date
        delta_minutes = (end_date - start_date).days * 1440
        print(delta_minutes)
        options_list = []
        for a in range(len(options)):
            if (delta_minutes / 1440 < 7 and 1 < delta_minutes / options_time[a] <= 5000) or \
                    (delta_minutes / 1440 <= 60 and 1 < delta_minutes / options_time[a] <= 5000) or \
                    (1 < delta_minutes / options_time[a] <= 5000):
                options_list.append(options[a])
        new_interval_choices.append([options_list[0]['value']])
        new_full_options_list.append(options_list)
        print(start_dates)
    return new_interval_choices, new_full_options_list, start_dates, end_dates


@app.callback(
    Output("graph", "figure"),
    Input("all series", "data"),
    Input({"type": "axis", "index": ALL}, "value"),
    Input({"type": "transform", "index": ALL}, "value"),
    Input({"type": "line_type", "index": ALL}, "value"),
    Input({"type": "date_picker", "index": ALL}, "start_date"),
    Input({"type": "date_picker", "index": ALL}, "end_date"),
    Input({"type": "interval_select", "index": ALL}, "value"),
    Input("colors", "data"),
    Input("graph", "figure"),
    Input("ser_del_index", "data"))
def display_ticker(all_series_dicts, axis_selections, transform_selections, line_selections, start_dates, end_dates,
                intervals, colors, fig, ser_del_index):
    print("indexes", all_series_dicts, "axis", axis_selections, "transform", transform_selections, "line",
        line_selections,
        "start", start_dates, "end", end_dates, "intervals", intervals)
    ctx = callback_context
    callback_id = ctx.triggered[0]['prop_id'].split(".")[0]
    if ser_del_index is not None:
        fig.data = list(fig.data).pop(ser_del_index)
    if fig is None:
        fig = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]], vertical_spacing=0.5)
        fig.update_layout(margin=dict(r=0, l=50, t=10, b=10, pad=0),
                        legend=dict(yanchor="top", y=1.1, xanchor="center", x=0.5, orientation="h"),
                        xaxis=dict(
                            rangeslider=dict(
                                visible=True,
                                thickness=0.1,
                                yaxis=dict(rangemode="auto")
                            )))
    elif all_series_dicts is not None and (len(fig["data"]) < len(all_series_dicts) or any(pref in callback_id for pref in ["axis", "transform", "line_type", "date_picker", "interval_select"])):
            if len(fig["data"]) < len(all_series_dicts):
                i = -1
            else:
                i = yaml.safe_load(callback_id)["index"]
                fig.data[i].visible=False
            print(fig)
            fig = go.Figure(fig)
            series_dict = yaml.safe_load(all_series_dicts[i])
            series = list(series_dict.keys())[0]
            database = series_dict[series]
            print(series, database)
            ser_df = data_grabber(series, database, start_dates[i], end_dates[i], intervals[i])
            x_data = ser_df["Date"].values.copy()
            y_data = ser_df["Close"].replace(".", np.NaN).values.copy().astype("float")
            x_axis = 'x'
            second_y = False
            fill = None
            line_type = line_selections[i]
            if line_type == "Area":
                fill = "tonexty"
            transform_selection = transform_selections[i]
            transform_dict = {"Level": (lambda y: y),
                            "Natural Log": (lambda y: np.log(y)),
                            "Change": (lambda y: [y[x] - y[x - 1] for x in range(1, len(y))]),
                            "%Change": (lambda y: [(y[x] - y[x - 1]) / y[x - 1] for x in range(1, len(y))]),
                            "Cumulative": (lambda y: [y[x] - y[0] for x in range(len(y))]),
                            "%Cumulative": (lambda y: [(y[x] - y[0]) / y[0] for x in range(len(y))])}
            y_data = transform_dict[transform_selection](y_data)
            x_data = x_data[1:] if transform_selection == "Change" or transform_selection == "%Change" else x_data
            if line_type == "Candle":
                if "Open" not in ser_df.columns:
                    ser_df["Open"] = np.concatenate((ser_df["Close"].values[:1], ser_df["Close"].values[:-1]))
                open_data = transform_dict[transform_selection](ser_df["Open"])
                high_data = transform_dict[transform_selection](ser_df["High"])
                low_data = transform_dict[transform_selection](ser_df["Low"])
            if len(all_series_dicts) > 1:
                if "Secondary Y-axis" in axis_selections[i]:
                    second_y = True
                if "Secondary X-axis" in axis_selections[i]:
                    fig.update_layout(xaxis2=dict(anchor=('y' if not second_y else 'y2'), overlaying='x', side='top',
                                                rangeslider=dict(
                                                    visible=True,
                                                    thickness=0.05,
                                                    yaxis=dict(rangemode="auto"), ),
                                                type="date"),
                                    yaxis_domain=[0, 0.94],
                                    xaxis2_type="date", xaxis_rangeslider_borderwidth=35,
                                    xaxis_rangeslider_bordercolor="white", xaxis_rangeslider_thickness=0.05)
                    x_axis = 'x2'
            if line_type != "Candle":
                fig.add_trace(
                    go.Scatter(x=x_data, y=y_data, mode="lines", name=series, xaxis=x_axis, fill=fill, connectgaps=True,
                            line=dict(color=colors[i % (len(colors) - 1)])), secondary_y=second_y)
            else:
                fig.add_trace(go.Candlestick(x=x_data, close=y_data, open=open_data, high=high_data, low=low_data,
                                            name=series[1:], xaxis=x_axis))
            fig.data[i].update(xaxis=x_axis)
            # fig.update_xaxes(
            #    rangebreaks=[
            #    (dict(bounds=[17, 9], pattern="hour"),dict(bounds = ["sat","mon"])) if intervals[i] not in ["1d","5d","1wk","1mo","3mo",None] else dict(bounds = ["sat","mon"]),
            #    ]
            # )
    return fig
if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True)
# %%
=======
# %%
from datetime import datetime
import yaml
import plotly.subplots
from dash import Dash, State, Output, Input, ALL, html, dcc, callback_context
from data_grabber_func import data_grabber
from sql_comm import get_parent_cat, get_sub_cat, get_ser_options, search_all_ser, get_ser_dict
from int_chart_funcs import series_interval, has_candle, one_month
import time
app = Dash(__name__, external_stylesheets=["int_chart.css"], suppress_callback_exceptions=True)
server=app.server
app.layout = html.Div([
    dcc.Store(data={"1m": 1, "2m": 2, "5m": 5, "15m": 15, "30m": 30, "60m": 60, "90m": 90,
                "1d": 1440, "5d": 5 * 1440, "1wk": 7 * 1440, "10d": 10 * 1440,
                "1mo": 30 * 1440, "3mo": 90 * 1440, "6mo": 180 * 1440, "1y": 360 * 1440},
                id="options_dict"),
    dcc.Store(data=['#CC9900', '#548DD4', '#FFCC00', '#00203e', '#386295', '#17365D'], id="colors"),
    dcc.Store(data=[], id="all series"),
    dcc.Store(id="ser_del_index"),
    dcc.Store(id="graph_dict"),
    dcc.Store(data=[], id="dataframes"),
    dcc.Store(data=[], id="ser_ids"),
    dcc.Loading([
    html.Div([
        html.Div([
            html.Div([html.H3("Select Series Group:"),
                    dcc.Dropdown(
                        id="parent category dropdown",
                        options=get_parent_cat(),
                        clearable=True,
                        multi=False,
                        optionHeight=30
                    )
                    ], id="parent category choice"),
            html.Div([html.H3("Select Series Category:"),
                    dcc.Dropdown(
                        id="category dropdown",
                        options=[],
                        clearable=True,
                        multi=False,
                        optionHeight=30
                    )
                    ], id="category choice", style={"display": "none"}),
            html.Div([html.H3("Select Series:"),
                    dcc.Dropdown(
                        id="series dropdown",
                        options=[],
                        clearable=True,
                        optionHeight=50,
                        multi=False
                    )
                    ], id="series choice", style={"display": "none"})
        ], style={"display": "flex"}, id="dropdown_search"),
        html.Div(children=[
            html.H3("Search All Series:"),
            html.Div([
                dcc.Input(style={'resize': 'none'}, id="search_text", type="text", spellCheck='false', debounce=True),
                html.Button(["Search"], id="search_button")
            ], id="search_bar"),
            dcc.Dropdown(id="search_result", options=[],
                        optionHeight=50, style={'display': 'none'})]
            , id="search_series")
    ], id="series_selection")]),
    html.Div(
        [html.Div(id="ticker_preferences", className="menu", style={"display": "none"}),
        html.A(href="#ticker_preferences", id="ticker_preferences_icon"),
        dcc.Loading([dcc.Graph(id="graph", config={'displaylogo': False})], type="graph")], id="figure")
], id="master")
@app.callback(
    Output("ticker_preferences", "children"),
    Output("ticker_preferences_icon", "children"),
    Output("category dropdown", "options"),
    Output("series dropdown", "options"),
    Output("category choice", "style"),
    Output("series choice", "style"),
    Output("all series", "data"),
    Output("ticker_preferences", "style"),
    Output("search_result", "options"),
    Output("search_result", "style"),
    Output("ser_del_index", "data"),
    Output("ser_ids", "data"),
    Input("parent category dropdown", "value"),
    Input("category dropdown", "value"),
    Input("series dropdown", "value"),
    Input("search_result", "value"),
    Input("search_button", "n_clicks"),
    Input("search_text", "value"),
    State("category dropdown", "options"),
    State("series dropdown", "options"),
    State("all series", "data"),
    State("ticker_preferences", "children"),
    Input({"type": "ticker_close", "index": ALL}, "n_clicks"),
    State("ser_ids", "data"))
def div_maker(parent, category, series_selection, search_series_selection, search_button_clicks, search_bar_input, cat_options, ser_options, all_series,
            ticker_preferences,
            close_clicks,
            ser_ids):
    start = time.time()
    ctx = callback_context
    callback_id = ctx.triggered[0]['prop_id'].split(".")[0]
    div_list = []
    link = []
    search_selection = callback_id == "search_result" and search_series_selection is not None
    search_result_options = []
    search_display = {"display": "none"}
    cat_display = {"display": "none"}
    ser_display = {"display": "none"}
    menu_display = {"display": "none"}
    ser_del_index = None
    if callback_id == "search_button" or callback_id == "search_text":
        search_display = {"display": "block"}
        search_result_options = search_all_ser(search_bar_input)
    if callback_id == "parent category dropdown" or callback_id == "category dropdown":
        if callback_id == "parent category dropdown":
            category = None
        series_selection = None
    if parent is not None or search_selection:
        if not search_selection:
            if callback_id == "parent category dropdown":
                cat_options = get_sub_cat(parent)
            cat_display = {"display": "block"}
        if category is not None or search_selection:
            if not search_selection:
                if callback_id == "category dropdown":
                    cat_search_time_start = time.time()
                    ser_options = get_ser_options(category)
                    cat_search_time_end = time.time()
                    print("cat search time:", cat_search_time_end - cat_search_time_start)
                ser_display = {"display": "block"}
            if series_selection is not None or search_selection:
                if search_selection:
                    search_ser_info = eval(search_series_selection)
                    series_selection = search_ser_info[0]
                    database, ser_name = search_ser_info[2], search_ser_info[1]
                    series_dict = {series_selection: database}
                else:
                    ser_dict_start = time.time()
                    series_dict, ser_name = get_ser_dict(series_selection, category)
                    ser_dict_end = time.time()
                    print("ser_dict time:", ser_dict_end - ser_dict_start)
                    database = series_dict[series_selection]
                if str(series_dict) not in all_series:
                    if all_series is None:
                        all_series = [str(series_dict)]
                    else:
                        all_series.append(str(series_dict))
                    if len(all_series) == 1:
                        div_list = [html.A(href="#", id="close")]
                    index = len(all_series) - 1
                    ser_ids.append(index)
                    options=series_interval(database, series_selection)
                    options_list = [option["label"] for option in options]
                    periods = ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]
                    div_list.append(html.Div([

                        html.Button('X', className="ticker_menu_close",
                                    id={"type": "ticker_close", "index": index},
                                    n_clicks=0),
                        html.H3(series_selection + ": " + ser_name, id="ticker_title"),

                        html.Div([
                            html.Div([html.Div([
                                dcc.DatePickerRange(className="date_range_picker",
                                                    id={"type": "date_picker", "index": index},
                                                    min_date_allowed=datetime.strptime("1970-01-01T00:00:00",
                                                                                    "%Y-%m-%dT%H:%M:%S")),
                                html.A(children=[html.Img(src="/assets/calendar.png", className="calendar_png")])]
                                , id="calendar_div" + str(index), className="date_picker_div")] +
                                    [(html.Button(period, 
                                    id=dict(type="period_btn", index=a + (index * 11)),
                                                className="period_button") if period != "max" else html.Button(
                                        period, id={"type": "period_btn", "index": a + (11 * index)}, className="period_button",
                                        autoFocus=True, n_clicks=1))
                                    for a, period in enumerate(periods)], id={"type": "period_select", "index": index},
                                    className="period_buttons_container " + str(index)),

                            html.Div([

                                html.Div([
                                    html.H6("Interval:", className="interval_title"),
                                    dcc.Dropdown(id={"type": "interval_select", "index": index},
                                                options=options,
                                                value=one_month(database) if "1mo" in options_list else options[0]["value"], 
                                                clearable=False,
                                                searchable=False,
                                                className="interval")
                                ], className="option",
                                    style={"display": "block"}),

                                html.Div([
                                    html.H6("Line Type:", className="line_title"),
                                    dcc.Dropdown(clearable=False, 
                                                searchable=False, 
                                                className="line_select",
                                                id={"type": "line_type", "index": index},
                                                options=["Linear", "Area"] if not has_candle(series_selection, database) else ["Linear", "Area", "Candle"]
                                                , value="Linear"),
                                ], className="option"),

                                html.Div([
                                    html.H6("Transform:", className="transform_title"),
                                    dcc.Dropdown(searchable=False, 
                                                clearable=False,
                                                id={"type": "transform", "index": index},
                                                className="transform_select",
                                                options=["Level", "Natural Log", "Change", "%Change", "Cumulative",
                                                        "%Cumulative"],
                                                value="Level")
                                ], className="option"),

                                html.Div([
                                    (dcc.Checklist(id={"type": "axis", "index": index},
                                                className="axis_select",
                                                labelStyle=dict(display="block"),
                                                options=["Secondary Y-axis", "Secondary X-axis"],
                                                style={"padding": "0px 10px"}))], className="axis_option"
                                )], className="options_list")])], className="ticker_menu",
                        id={"type": "ticker", "index": index}, title=series_selection))
    if "ticker_close" in callback_id:
        if len(all_series) > 1:
            for index in range(len(all_series)):
                if close_clicks[index] >= 1:
                    all_series.pop(index)
                    ticker_preferences.pop(index + 1)
                    ser_del_index = index
                    ser_ids.pop(index)
        else:
            all_series = []
            ticker_preferences = []
            link = []
            ser_del_index = 0
            ser_ids = []
    if ticker_preferences is None:
        ticker_preferences = div_list
    else:
        ticker_preferences = ticker_preferences + div_list
    if len(all_series) > 0:
        menu_display = {}
        link = [html.Img(src="/assets/hamburger.png", id="hamburger")]
    print("close clicks: ", close_clicks, "ticker_preferences: ", len(ticker_preferences))
    end = time.time()
    print("div_maker time:", end - start)
    return ticker_preferences, link, cat_options, ser_options, cat_display, ser_display, all_series, menu_display, search_result_options, search_display, ser_del_index, ser_ids


@app.callback(
            Output({"type": "date_picker", "index": ALL}, "start_date"),
            Output({"type": "date_picker", "index": ALL}, "end_date"),
            Output("dataframes", "data"),
            Input("all series", "data"),
            Input({"type": "period_btn", "index": ALL}, "n_clicks"),
            Input({"type": "date_picker", "index": ALL}, "start_date"),
            Input({"type": "date_picker", "index": ALL}, "end_date"),
            Input({"type": "interval_select", "index": ALL}, "value"),
            State({"type": "period_btn", "index": ALL}, "children"),
            State({"type": "interval_select", "index": ALL}, "options"),
            State("dataframes", "data"),
            State("ser_del_index", "data"),
            State("ser_ids", "data")
            )
def interval_defaults(seriess_dicts, button_clicks, start_dates, end_dates, interval_selections, buttons, all_options,  dfs, ser_del_index, ser_ids):
    start = time.time()
    ctx = callback_context
    callback_id = ctx.triggered[0]['prop_id'].split(".")[0]
    if ser_del_index is not None:
        dfs.pop(ser_del_index)
        ser_del_index = None
    elif (len(seriess_dicts) > 0 and len(seriess_dicts) > len(dfs)) or any(id in callback_id for id in ["period_btn", "date_picker", "interval_select"]):
        if callback_id == "all series":
            index = len(seriess_dicts) - 1
        else:
            index = yaml.safe_load(callback_id)["index"]
            if "period_btn" in callback_id:
                index = ser_ids.index(index // 11)
        print("options, index:", len(all_options), index)
        series_dict = yaml.safe_load(seriess_dicts[index])
        series = list(series_dict.keys())[0]
        database = series_dict[series]
        if "date_picker" in callback_id:
            print("use date")
            if len(start_dates[index]) == 10:
                start_dates[index] += "T00:00:00"
            if len(end_dates[index]) == 10:
                end_dates[index] += "T00:00:00"
            start_date = datetime.strptime(start_dates[index], "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_dates[index], "%Y-%m-%dT%H:%M:%S")
            ser_df = data_grabber(series, database, start_date=start_date, end_date=end_date, \
            interval= interval_selections[index] if "interval_select" in callback_id else None)
        elif ("period_btn" in callback_id and index * 11 < eval(callback_id)["index"] < (index + 1) * 11) or any(
                button_clicks[index * 11:(index + 1) * 11]):
            button_name = "max" if "period_btn" not in callback_id else buttons[eval(callback_id)["index"]]
            data_grab_start = time.time()
            ser_df = data_grabber(series, database, period=button_name, \
                interval= interval_selections[index])
            data_grab_end = time.time()
            print(ser_df)
            print("data_grab time:", data_grab_end - data_grab_start)
        #new_interval_choices.append([options_list[0]['value']])
        #new_full_options_list.append(options_list)
        print("dfs: ", len(dfs))
        if len(dfs) > index:
            print("changed dfs")
            dfs[index] = {column: ser_df[column].values.tolist() for column in ser_df.columns}
        else:
            dfs.append({column: ser_df[column].values.tolist() for column in ser_df.columns})
    end = time.time()
    print("interval_defaults time:", end - start)
    return start_dates, end_dates, dfs


@app.callback(
    Output("graph_dict", "data"),
    Input("graph_dict", "data"))
def display_ticker(fig):
    start = time.time()
    if fig is None:
        fig = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]], vertical_spacing=0.5)
        fig.update_layout(margin=dict(r=10, l=50, t=15, b=10, pad=0),
                        legend=dict(yanchor="top", y=1.15, xanchor="center", x=0.5, orientation="h"),
                        xaxis=dict(
                            rangeslider=dict(
                                visible=True,
                                thickness=0.1,
                                yaxis=dict(rangemode="auto"),
                            ),
                            type="date"), 
                        xaxis2=dict(
                            anchor='y', 
                            overlaying='x', 
                            side='top',       
                            rangeslider=dict(
                                visible=True,
                                thickness = 0.1,
                                yaxis=dict(rangemode="auto")),
                        type="date"))
    """
    elif all_series_dicts is not None and (len(fig["data"]) < len(all_series_dicts) or (any(pref in callback_id for pref in ["transform", "line_type"]) and len(ctx.triggered )== 1)):
            print(len(fig["data"]), len(all_series_dicts), len(dfs))
            if len(fig["data"]) < len(all_series_dicts):
                i = -1
            else:
                i = yaml.safe_load(callback_id)["index"]
            fig = plotly.subplots.make_subplots(figure = go.Figure(fig))
            series_dict = yaml.safe_load(all_series_dicts[i])
            series = list(series_dict.keys())[0]
            database = series_dict[series]
            print(i, series, database)
            ser_df = dfs[i]
            x_data = list(map(pd.to_datetime, ser_df["Date"]))
            y_data = list(map(float, ser_df["Close"]))
            fill = None
            line_type = line_selections[i]
            if line_type == "Area":
                fill = "tonexty"
            if line_type == "Candle":
                if "Open" not in ser_df.keys():
                    ser_df["Open"] = np.concatenate((ser_df["Close"][:1], ser_df["Close"][:-1]))
            if line_type != "Candle":
                fig.add_trace(
                    go.Scatter(x=x_data, y=y_data, mode="lines", name=series, fill=fill, connectgaps=True,
                            line=dict(color=colors[i % (len(colors) - 1)])))
            else:
                fig.add_trace(go.Candlestick(x=x_data, close=y_data, open=ser_df["Open"], high=ser_df["High"], low=ser_df["Low"],
                                            name=series[1:]))
            # fig.update_xaxes(
            #    rangebreaks=[
            #    (dict(bounds=[17, 9], pattern="hour"),dict(bounds = ["sat","mon"])) if intervals[i] not in ["1d","5d","1wk","1mo","3mo",None] else dict(bounds = ["sat","mon"]),
            #    ]
            # )
    """
    end = time.time()
    print("display_ticker time:", end - start)
    return fig
app.clientside_callback(''.join(line for line in open('int_chart_js.js','r')),
    Output("graph", "figure"),
    Input("graph_dict", "data"),
    Input({"type": "axis","index": ALL}, "value"),
    Input({"type": "transform", "index": ALL}, "value"),
    Input({"type": "line_type", "index": ALL}, "value"),
    Input("all series", "data"),
    Input("dataframes", "data"),
    Input("colors", "data"),
    Input("ser_del_index", "data"),
    Input({"type": "period_btn", "index": ALL}, "n_clicks"),
    Input({"type": "interval_select", "index": ALL}, "options"),
    Input({"type": "interval_select", "index": ALL}, "value"),
    Input("ser_ids", "data"))


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(debug=True, use_reloader=False)
# %%
>>>>>>> 70d0c6876fcc65d16a9ee7764662b7c79d45eea0
