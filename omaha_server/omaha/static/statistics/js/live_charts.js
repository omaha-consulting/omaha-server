function get_versions(data){
    return Object.keys(data).sort();
}


function get_data(data){
    return get_versions(data).map(function(d){
        return {
            key: d,
            values: data[d]
        }
    });
}


function get_hours(data){
    if (Object.keys(data).length) {
        return data[Object.keys(data)[0]].map(function (d) {
            return new Date(d[0])
        });
    }
    else return [];
}


$(document).ready(function() {
    var app = document.getElementById('app_name');
    var app_name = app.dataset.name;
    $.ajax({
        url: "/api/statistics/live/" + app_name, success: function (result) {
            var data = result.data;

            nv.addGraph(function () {
                var local_data=data.win;
                var chart = nv.models.stackedAreaChart()
                        .x(function(d) { return new Date(d[0]) })
                        .y(function(d) { return d[1] })
                        .useInteractiveGuideline(true)
                        .showControls(false);

                chart.xAxis.showMaxMin(false)
                    .tickValues(get_hours(local_data).filter(function(d, i){
                        return !(i%3);
                    }))
                    .tickFormat(function (d) {
                        return d3.time.format('%b %d %I:%M %p')(new Date(d));
                    });

                chart.duration(1000);
                d3.select('#win-chart svg')
                    .datum(get_data(local_data)).call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });

            nv.addGraph(function () {
                var local_data=data.mac;
                var chart = nv.models.stackedAreaChart()
                        .x(function(d) { return new Date(d[0]) })
                        .y(function(d) { return d[1] })
                        .useInteractiveGuideline(true)
                        .showControls(false);

                chart.xAxis.showMaxMin(false)
                    .tickValues(get_hours(local_data).filter(function(d, i){
                        return !(i%3);
                    }))
                    .tickFormat(function (d) {
                        return d3.time.format('%b %d %I:%M %p')(new Date(d));
                    });

                chart.duration(1000);
                d3.select('#mac-chart svg')
                    .datum(get_data(local_data)).call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        }
    });
});
