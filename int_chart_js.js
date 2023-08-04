function chart_settings(figure, axisSelections, transSelections, lineTypes, allSeriesJSON, dfs, colors, ser_del_index, button_clicks, interval_options, intervals, ser_ids) {
    var triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id)[0].split(".")[0]; 
    var now = new Date();
    var start = new Date(now.getFullYear(), 0, 0);
    var diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
    var oneDay = 1000 * 60 * 60 * 24;
    var days = Math.floor(diff / oneDay);
    var periods = ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]
    var interval_days = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 92, "6mo": 183, "1y": 365}
    let new_figure = JSON.parse(JSON.stringify(figure))
        function transform (y, trans) {
            newArr = []
            if (trans === "Level"){
                return y
            } else if (trans === "Natural Log") {
                return y.map(i => Math.log(i))
            } else if (trans === "Change") {
                for (var x = 1; x < y.length; x++) {
                newArr[x] = y[x] - y[x-1]
                }
                return newArr
            } else if (trans === "%Change") {
                for (var x = 1; x < y.length; x++) {
                newArr[x] = (y[x] - y[x-1]) / y[x - 1]
                }
                return newArr
            } else if (trans === "Cumulative") {
                for (var x = 0; x < y.length; x++) {
                newArr[x] = y[x] - y[0]
                }
                return newArr
            } else if (trans === "%Cumulative") {
                for (var x = 0; x < y.length; x++) {
                newArr[x] = (y[x] - y[0]) / y[0]
                }
                return newArr
            }
        }
        var nonNullAxisSelections = axisSelections.filter(selection => selection !== undefined)
        function add_axes (index) {
            if (axisSelections[index].includes("Secondary Y-axis")) {
                new_figure["data"][index]["yaxis"] = "y2";
                if (axisSelections[index].includes("Secondary X-axis")) {
                    new_figure["layout"]["xaxis2"]["anchor"] = "y2"
                    //console.log(new_figure["layout"]["xaxis2"]["rangeslider"]["yaxis2"]["rangemode"])
                    new_figure["layout"]["xaxis2"]["domain"] = [0, 0.94]
                }
                new_figure["layout"]["xaxis"]["rangeslider"]["yaxis"]["rangemode"] = "auto"
                new_figure["layout"]["xaxis"]["rangeslider"]["yaxis2"] = {"rangemode": "auto"}
            }
            if (axisSelections[index].includes("Secondary X-axis")) {
                new_figure["data"][index]["xaxis"] = "x2"
            }
        }
        if (ser_del_index !== undefined) {
            new_figure["data"].splice(ser_del_index, ser_del_index)
        }
        for (var i = 0; i < dfs.length; i++) {
            var lineType = lineTypes[i]
            if (lineType !== undefined) {
                const seriesJSON = JSON.parse(allSeriesJSON[i].replaceAll("'",'"'))
                const series = Object.keys(seriesJSON)[0]
                new_figure["data"][i] = {
                    connectGaps: true,
                    line: {color: colors[i % (colors.length - 1)]},
                    mode: "lines",
                    name: series,
                    type: "scatter",
                    x: dfs[i]["Date"].map(date => new Date(date / 1000000)),
                    y: dfs[i]["Close"],
                    xaxis: "x",
                    yaxis: "y"
                }
                if (lineType === "Area") {
                    new_figure["data"][i]["fill"] = "tozeroy"
                } else if (lineType === "Candle") {
                    if (!Object.keys(dfs[i]).includes("Open")) {
                        dfs[i]["Open"] = [dfs[i]["Close"][0]].concat(dfs[i]["Close"].slice(0, -1))
                    }
                    new_figure["data"][i]["type"] = "candlestick"
                    new_figure["data"][i]["close"] = dfs[i]["Close"]
                    new_figure["data"][i]["high"] = dfs[i]["High"]
                    new_figure["data"][i]["open"] = dfs[i]["Open"]
                    new_figure["data"][i]["low"] = dfs[i]["Low"]
                }
            }
            if (axisSelections[i] !== undefined) {
                add_axes(i)
            }
            if (transSelections[i] !== undefined) {
                new_figure["data"][i]["y"] = transform(new_figure["data"][i]["y"], transSelections[i])
                if (["Change", "%Change"].includes(transSelections[i])) {
                    new_figure["data"][i]["x"] = new_figure["data"][i]["x"].slice(1)
                }
                if (lineTypes[i] === "Candle") {
                    new_figure["data"][i]["open"] =  transform(new_figure["data"][i]["open"], transSelections[i])
                    new_figure["data"][i]["high"] =  transform(new_figure["data"][i]["high"], transSelections[i])
                    new_figure["data"][i]["close"] =  transform(new_figure["data"][i]["close"], transSelections[i])
                }
            }
            var current_interval_days = interval_days[interval_options[i].find(interval => interval["value"] == intervals[i])["label"]]
            for (var a = 0; a < 11; a++) {
                if (interval_days[periods[a]] <= current_interval_days | (a === 5 & days <= current_interval_days)) {
                    document.getElementById('{"index":' + (a + ser_ids[i] * 11) + ',"type":"period_btn"}').style.display = "none"
                }
            }
        }
        if (nonNullAxisSelections.some(selection => selection.includes("Secondary X-axis") & nonNullAxisSelections.some(selection => !selection.includes("Secondary X-axis")))) {
            new_figure["layout"]["xaxis2"]["borderwidth"] = 35
            new_figure["layout"]["xaxis2"]["bordercolor"] = "white"
            new_figure["layout"]["xaxis2"]["rangeslider"]["thickness"] = 0.05
        }
        console.log(triggered)
        console.log(new_figure)
        return new_figure
    }
function chart_settings(figure, axisSelections, transSelections, lineTypes, allSeriesJSON, dfs, colors, ser_del_index, button_clicks, interval_options, intervals, ser_ids) {
    var triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id)[0].split(".")[0]; 
    var now = new Date();
    var start = new Date(now.getFullYear(), 0, 0);
    var diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
    var oneDay = 1000 * 60 * 60 * 24;
    var days = Math.floor(diff / oneDay);
    var periods = ["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]
    var interval_days = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 92, "6mo": 183, "1y": 365}
    let new_figure = JSON.parse(JSON.stringify(figure))
        function transform (y, trans) {
            newArr = []
            if (trans === "Level"){
                return y
            } else if (trans === "Natural Log") {
                return y.map(i => Math.log(i))
            } else if (trans === "Change") {
                for (var x = 1; x < y.length; x++) {
                newArr[x] = y[x] - y[x-1]
                }
                return newArr
            } else if (trans === "%Change") {
                for (var x = 1; x < y.length; x++) {
                newArr[x] = (y[x] - y[x-1]) / y[x - 1]
                }
                return newArr
            } else if (trans === "Cumulative") {
                for (var x = 0; x < y.length; x++) {
                newArr[x] = y[x] - y[0]
                }
                return newArr
            } else if (trans === "%Cumulative") {
                for (var x = 0; x < y.length; x++) {
                newArr[x] = (y[x] - y[0]) / y[0]
                }
                return newArr
            }
        }
        var nonNullAxisSelections = axisSelections.filter(selection => selection !== undefined)
        function add_axes (index) {
            if (axisSelections[index].includes("Secondary Y-axis")) {
                new_figure["data"][index]["yaxis"] = "y2";
                if (axisSelections[index].includes("Secondary X-axis")) {
                    new_figure["layout"]["xaxis2"]["anchor"] = "y2"
                    //console.log(new_figure["layout"]["xaxis2"]["rangeslider"]["yaxis2"]["rangemode"])
                    new_figure["layout"]["xaxis2"]["domain"] = [0, 0.94]
                }
                new_figure["layout"]["xaxis"]["rangeslider"]["yaxis"]["rangemode"] = "auto"
                new_figure["layout"]["xaxis"]["rangeslider"]["yaxis2"] = {"rangemode": "auto"}
            }
            if (axisSelections[index].includes("Secondary X-axis")) {
                new_figure["data"][index]["xaxis"] = "x2"
            }
        }
        if (ser_del_index !== undefined) {
            new_figure["data"].splice(ser_del_index, ser_del_index)
        }
        for (var i = 0; i < dfs.length; i++) {
            var lineType = lineTypes[i]
            if (lineType !== undefined) {
                const seriesJSON = JSON.parse(allSeriesJSON[i].replaceAll("'",'"'))
                const series = Object.keys(seriesJSON)[0]
                new_figure["data"][i] = {
                    connectGaps: true,
                    line: {color: colors[i % (colors.length - 1)]},
                    mode: "lines",
                    name: series,
                    type: "scatter",
                    x: dfs[i]["Date"].map(date => new Date(date / 1000000)),
                    y: dfs[i]["Close"],
                    xaxis: "x",
                    yaxis: "y"
                }
                if (lineType === "Area") {
                    new_figure["data"][i]["fill"] = "tozeroy"
                } else if (lineType === "Candle") {
                    if (!Object.keys(dfs[i]).includes("Open")) {
                        dfs[i]["Open"] = [dfs[i]["Close"][0]].concat(dfs[i]["Close"].slice(0, -1))
                    }
                    new_figure["data"][i]["type"] = "candlestick"
                    new_figure["data"][i]["close"] = dfs[i]["Close"]
                    new_figure["data"][i]["high"] = dfs[i]["High"]
                    new_figure["data"][i]["open"] = dfs[i]["Open"]
                    new_figure["data"][i]["low"] = dfs[i]["Low"]
                }
            }
            if (axisSelections[i] !== undefined) {
                add_axes(i)
            }
            if (transSelections[i] !== undefined) {
                new_figure["data"][i]["y"] = transform(new_figure["data"][i]["y"], transSelections[i])
                if (["Change", "%Change"].includes(transSelections[i])) {
                    new_figure["data"][i]["x"] = new_figure["data"][i]["x"].slice(1)
                }
                if (lineTypes[i] === "Candle") {
                    new_figure["data"][i]["open"] =  transform(new_figure["data"][i]["open"], transSelections[i])
                    new_figure["data"][i]["high"] =  transform(new_figure["data"][i]["high"], transSelections[i])
                    new_figure["data"][i]["close"] =  transform(new_figure["data"][i]["close"], transSelections[i])
                }
            }
            var current_interval_days = interval_days[interval_options[i].find(interval => interval["value"] == intervals[i])["label"]]
            for (var a = 0; a < 11; a++) {
                if (interval_days[periods[a]] <= current_interval_days | (a === 5 & days <= current_interval_days)) {
                    document.getElementById('{"index":' + (a + ser_ids[i] * 11) + ',"type":"period_btn"}').style.display = "none"
                }
            }
        }
        if (nonNullAxisSelections.some(selection => selection.includes("Secondary X-axis") & nonNullAxisSelections.some(selection => !selection.includes("Secondary X-axis")))) {
            new_figure["layout"]["xaxis2"]["borderwidth"] = 35
            new_figure["layout"]["xaxis2"]["bordercolor"] = "white"
            new_figure["layout"]["xaxis2"]["rangeslider"]["thickness"] = 0.05
        }
        console.log(triggered)
        console.log(new_figure)
        return new_figure
    }