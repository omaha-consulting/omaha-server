(function ()
{
    var $statistics = $("#version-statistics"),
        $date = $statistics.find("input[name='date']"),
        $ajaxButton = $statistics.find('button'),
        app = $('#app_name'),
        appName = app.data('name'),
        charts = {},
        winTable,
        macTable;

    function applyRange() {
        var date = moment.utc($date.val(), 'YYYY-MM', true);
        updateGraph({
            date: date.isValid() ? date.format('YYYY-MM') : ''
        })
    }


    function getData(data) {
        return Object.keys(data).map(function (d) {
            return {
                label: d,
                value: data[d]
            }
        });
    }


    function getRows(data) {
        return Object.keys(data).map(function (v) {
            return [v, data[v]];
        });
    }


    function makeGraphForPlatform(chartName, chartDataName, data, platform) {
        nv.addGraph(function () {
            var chart = nv.models.pieChart()
                .x(function (d) {
                    return d.label
                })
                .y(function (d) {
                    return d.value
                })
                .showLabels(true);
            var graphSelector = ''.concat('#', platform, '-versions-chart svg');
            var chartData = d3.select(graphSelector)
                .datum(getData(data))
                .call(chart);
            nv.utils.windowResize(chart.update);
            charts[chartName] = chart;
            charts[chartDataName] = chartData;
            return chart;
        });
    }


    function makeGraph() {
        $.ajax({
            url: "/api/statistics/versions/" + appName + '/',
            success: function (result) {
                var data = result.data;
                makeGraphForPlatform('winChart', 'winChartData', data.win, 'win');
                winTable.rows.add(getRows(data.win)).draw();
                makeGraphForPlatform('macChart', 'macChartData', data.mac, 'mac');
                macTable.rows.add(getRows(data.mac)).draw();
            }
        });
    }


    function updateGraphForPlatform(chart, chartData, data) {
        chartData.html("").datum(getData(data)).transition().duration(1000).call(chart);
    }


    function updateGraph(options) {
        var $ajaxCompleted = $statistics.find('.ajax-completed');
        var $ajaxLoading = $statistics.find('.ajax-loading');
        $ajaxLoading.show();
        $ajaxCompleted.hide();
        $ajaxButton.prop("disabled", true);
        $.ajax({
            url: "/api/statistics/versions/" + appName + '/',
            data: options,
            success: function (result) {
                var data = result.data;
                updateGraphForPlatform(charts['winChart'], charts['winChartData'], data.win);
                winTable.clear().rows.add(getRows(data.win)).draw();
                updateGraphForPlatform(charts['macChart'], charts['macChartData'], data.mac);
                macTable.clear().rows.add(getRows(data.mac)).draw();
            },
            complete: function () {
                $ajaxLoading.hide();
                $ajaxCompleted.show();
                $ajaxButton.prop("disabled", false);
            }
        });
    }


    $(document).ready(function () {
        var now = moment();
        $date.val(now.format('YYYY-MM'));
        $ajaxButton.prop("disabled", false);
        $ajaxButton.click(applyRange);
        makeGraph();
        winTable = $('#win-table table').DataTable( {
            "paging":   false,
            "info": false,
            "scrollY": "300px",
            "scrollCollapse": true,
            "searching": false,
            "columnDefs": [
                { className: "dt-center", "targets": [ 0, 1 ] }
            ]
            } );
        macTable = $('#mac-table table').DataTable( {
            "paging":   false,
            "info": false,
            "scrollY": "300px",
            "scrollCollapse": true,
            "searching": false,
            "columnDefs": [
                { className: "dt-center", "targets": [ 0, 1 ] }
            ]
            } );
    });
    window.onresize = function () {
        macTable.columns.adjust();
    }
})();
