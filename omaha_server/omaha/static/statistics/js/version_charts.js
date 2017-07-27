(function ()
{
    var $statistics = $("#version-statistics"),
        $date = $statistics.find("input[name='date']"),
        $ajaxButton = $statistics.find('button'),
        app = $('#app_name'),
        appName = app.data('name'),
        appPlatforms = app.data('platforms'),
        charts = {},
        chartDatas = {},
        tables = {};

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


    function makeGraphForPlatform(data, platform) {
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
            charts[platform] = chart;
            chartDatas[platform] = chartData;
        });
    }


    function makeGraph() {
        $.ajax({
            url: "/api/statistics/versions/" + appName + '/',
            success: function (result) {
                var data = result.data;
                appPlatforms.forEach(function (platform) {
                    makeGraphForPlatform(data[platform], platform);
                    tables[platform].rows.add(getRows(data[platform])).draw();
                });
            }
        });
    }


    function updateGraphForPlatform(platform, data) {
        var chart = charts[platform],
            chartData = chartDatas[platform];
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
                appPlatforms.forEach(function (platform) {
                    updateGraphForPlatform(platform, data[platform]);
                    tables[platform].clear().rows.add(getRows(data[platform])).draw();
                });

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
        appPlatforms.forEach(function (platform) {
            tables[platform] = $("#" + platform + "-table table").DataTable( {
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
    });
    window.onresize = function () {
        appPlatforms.forEach(function(platform){
            tables[platform].columns.adjust();
        });
    }
})();
