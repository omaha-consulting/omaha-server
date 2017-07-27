(function ()
{
    var $start = $("#month-statistics input[name='start']"),
        $end = $("#month-statistics input[name='end']"),
        $ajaxButton = $('#month-statistics button'),
        app = $('#app_name'),
        appName = app.data('name'),
        appStartDate = moment(app.data('startDate')),
        appPlatforms = app.data('platforms'),
        charts = {},
        chartDatas = {};

    function applyRange() {
        var start = moment.utc($start.val(), 'YYYY-MM', true);
        var end = moment.utc($end.val(), 'YYYY-MM', true);
        if (start > end) {
            var tmp = start;
            start = end;
            end = tmp;
            $start.val(start.format('YYYY-MM'));
            $end.val(end.format('YYYY-MM'));
        }
        updateGraph({
            start: start.isValid() ? start.format('YYYY-MM') : '',
            end: end.isValid() ? end.format('YYYY-MM') : ''
        })
    }


    function getData(data){
        if (data.hasOwnProperty('uninstalls'))
            data.uninstalls.forEach(function(el, index, arr){arr[index][1] = -el[1]});
        var res = Object.keys(data).map(function(d){
            return {
                key: d,
                values: data[d]
            }
        });
        res.unshift(res.pop());
        return res;
    }


    function getMonths(data) {
        if (Object.keys(data).length) {
            return data[Object.keys(data)[0]].map(function (d) {
                return d[0]
            });
        }
        else return [];
    }


    function makeGraphForPlatform(data, platform){
        nv.addGraph(function() {
            var months = getMonths(data);
            var chart = nv.models.multiBarChart()
                        .x(function(d) { return d[0] })
                        .y(function(d) { return d[1] })
                        .stacked(true)
                        .showControls(false)
                        .color(['#00f', 'green', 'red']);
            var graphSelector = ''.concat('#', platform, '-months-chart svg');

            chart.xAxis.showMaxMin(false)
                .tickValues(months);

            chart.yAxis
                .tickFormat(d3.format(',f'));

            chart.duration(1000);
            var chartData = d3.select(graphSelector)
                .datum(getData(data)).call(chart);

            nv.utils.windowResize(chart.update);
            charts[platform] = chart;
            chartDatas[platform] = chartData;
        });
    }

    function makeGraph(options){
        $.ajax({
            url: "/api/statistics/months/" + appName + '/',
            data: options,
            success: function (result) {
                var data = result.data;
                appPlatforms.forEach(function (platform) {
                    makeGraphForPlatform(data[platform], platform);
                })
            }
        });
    }


    function updateGraphForPlatform(platform, data) {
        var months = getMonths(data),
            chart = charts[platform],
            chartData = chartDatas[platform];
        chart.xAxis.showMaxMin(false)
            .tickValues(months);

        chartData.datum(getData(data)).transition().duration(1000).call(chart);
    }


    function updateGraph(options) {
        var $ajaxCompleted = $('#ajax-completed');
        var $ajaxLoading = $('#ajax-loading');
        $ajaxLoading.show();
        $ajaxCompleted.hide();
        $ajaxButton.prop("disabled", true);
        $.ajax({
            url: "/api/statistics/months/" + appName + '/',
            data: options,
            success: function (result) {
                var data = result.data;
                appPlatforms.forEach(function (platform){
                    updateGraphForPlatform(platform, data[platform]);
                });
            },
            complete: function () {
                $ajaxLoading.hide();
                $ajaxCompleted.show();
                $ajaxButton.prop("disabled", false);
            }
        });
    }


    $(document).ready(function() {
        var now = moment();
        $end.val(now.format('YYYY-MM'));
        $start.val(moment.max(appStartDate, now.subtract(1, 'years')).format('YYYY-MM'));
        $ajaxButton.prop("disabled", false);
        $ajaxButton.click(applyRange);
        makeGraph({
            start: $start.val(),
            end: $end.val()
        });
    });
})();