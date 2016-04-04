(function ()
{
    var $statistics = $("#channel-statistics"),
        $date = $statistics.find("input[name='date']"),
        $ajaxButton = $statistics.find('button'),
        app = $('#app_name'),
        appName = app.data('name'),
        charts = {},
        table;

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


    function makeChannelsGraph(chartName, chartDataName, data) {
        nv.addGraph(function () {
            var chart = nv.models.pieChart()
                .x(function (d) {
                    return d.label
                })
                .y(function (d) {
                    return d.value
                })
                .showLabels(true);
            var chartData = d3.select('#channels-chart svg')
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
            url: "/api/statistics/channels/" + appName + '/',
            success: function (result) {
                var data = result.data;
                makeChannelsGraph('chart', 'chartData', data);
                table.rows.add(getRows(data)).draw();
            }
        });
    }


    function updatePlatformGraph(chart, chartData, data) {
        chartData.html("").datum(getData(data)).transition().duration(1000).call(chart);
    }


    function updateGraph(options) {
        var $ajaxCompleted = $statistics.find('.ajax-completed');
        var $ajaxLoading = $statistics.find('.ajax-loading');
        $ajaxLoading.show();
        $ajaxCompleted.hide();
        $ajaxButton.prop("disabled", true);
        $.ajax({
            url: "/api/statistics/channels/" + appName + '/',
            data: options,
            success: function (result) {
                var data = result.data;
                updatePlatformGraph(charts['chart'], charts['chartData'], data);
                table.clear().rows.add(getRows(data)).draw();
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
        table = $('#channels-table table').DataTable( {
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
})();