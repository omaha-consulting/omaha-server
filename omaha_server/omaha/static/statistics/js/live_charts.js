var macChartData, macChart, winChartData, winChart;

function applyRange() {
    var app_name = document.getElementById('app_name').dataset.name;
    var $start = $("#range-start input");
    var $end = $("#range-end input");
    var start = moment($start.val(), 'YYYY-MM-DD HH:mm:ss', true).utc();
    var end = moment($end.val(), 'YYYY-MM-DD HH:mm:ss', true).utc();

    if (start > end){
        var tmp = start;
        start = end;
        end = tmp;
        $start.val(start.format('YYYY-MM-DD HH:mm:ss'));
        $end.val(end.format('YYYY-MM-DD HH:mm:ss'));
    }
    updateGraph({
        app_name: app_name,
        start: start.isValid() ? start.format(): '',
        end: end.isValid() ? end.format(): ''
    })
}


function getVersions(data){
    return Object.keys(data).sort();
}


function getData(data){
    return getVersions(data).map(function(d){
        return {
            key: d,
            values: data[d]
        }
    });
}


function getHours(data){
    if (Object.keys(data).length) {
        return data[Object.keys(data)[0]].map(function (d) {
            return new Date(d[0])
        });
    }
    else return [];
}


function getLiveStatisticsAPIurl(options){
    var url = "/api/statistics/live/" + options['app_name'] + "/";
    var start = options['start'];
    var end = options['end'];
    if (start || end){
        url += "?";
        url += start ? 'start=' + start + '&': '';
        url += end ? 'end=' + end: '';
    }
    return url.replace(/\+/g, '%2B');
}


function makePlatformGraph(chartName, chartDataName, data, platform){
    nv.addGraph(function () {
        var graphSelector = ''.concat('#', platform, '-chart svg');
        var hours = getHours(data);
        var tickSize = Math.ceil(hours.length / 8);
        var chart = nv.models.stackedAreaChart()
                .x(function(d) { return new Date(d[0]) })
                .y(function(d) { return d[1] })
                .useInteractiveGuideline(true)
                .showControls(false);

        chart.xAxis.showMaxMin(false)
            .tickValues(hours.filter(function(d, i){
                return !(i % tickSize);
            }))
            .tickFormat(function (d) {
                return d3.time.format('%b %d %I:%M %p')(new Date(d));
            });

        chart.duration(1000);
        var chartData = d3.select(graphSelector)
            .datum(getData(data)).call(chart);

        nv.utils.windowResize(chart.update);

        window[chartName] = chart;
        window[chartDataName] = chartData;
        return chart;
    });
}


function makeGraph(options){
    $.ajax({
        url: getLiveStatisticsAPIurl(options),
        success: function (result) {
            var data = result.data;
            makePlatformGraph('winChart', 'winChartData', data.win, 'win');
            makePlatformGraph('macChart', 'macChartData', data.mac, 'mac');
        }
    });
}


function updatePlatformGraph(chart, chartData, data){
    var hours = getHours(data);
    var tickSize = Math.ceil(hours.length / 8);
    chart.xAxis.showMaxMin(false)
        .tickValues(hours.filter(function(d, i){
            return !(i % tickSize);
        }));

    chartData.datum(getData(data)).transition().duration(1000).call(chart);
    nv.utils.windowResize(chart.update);
}


function updateGraph(options){
    var $ajaxCompleted = $('#ajax-completed');
    var $ajaxLoading = $('#ajax-loading');
    var $ajaxButton = $('#btn-apply');

    $ajaxLoading.show();
    $ajaxCompleted.hide();
    $ajaxButton.prop( "disabled", true );
    $.ajax({
        url: getLiveStatisticsAPIurl(options),
        success: function (result) {
            var data = result.data;
            updatePlatformGraph(winChart, winChartData, data.win);
            updatePlatformGraph(macChart, macChartData, data.mac);
        },
        complete: function() {
            $ajaxLoading.hide();
            $ajaxCompleted.show();
            $ajaxButton.prop( "disabled", false);
        }
    });
}


$(document).ready(function() {
    var now = moment()
    $("#range-end input").val(now.format('YYYY-MM-DD HH:mm:00'));
    $("#range-start input").val(now.subtract(1, 'days').format('YYYY-MM-DD HH:mm:00'));
    $('#btn-apply').click(applyRange);
    var app = document.getElementById('app_name');
    var app_name = app.dataset.name;
    makeGraph({app_name:app_name});
});
