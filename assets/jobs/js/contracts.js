function offers_by_period(period) {
    $.ajax({
     type: "GET",
     url: 'get_offers_by_period',
     data: {period: period},
     dataType: "json",
     success: function(json) {
        if (period === 'year') {
            $("#title_offers_period").text("Nombre d'offres par année");
            $("#title_types_contract_period").text("Répartition des types de contrats par année");
        }
        else if (period === 'month') {
            $("#title_offers_period").text("Nombre d'offres par mois");
            $("#title_types_contract_period").text("Répartition des types de contrats par mois");
        }
        // weeks
        else  {
            $("#title_offers_period").text("Nombre d'offres par semaine");
            $("#title_types_contract_period").text("Répartition des types de contrats par semaine");
        }

        var chart;
        nv.addGraph(function() {
            chart = nv.models.historicalBarChart();
            chart
                .useInteractiveGuideline(true)
                .duration(250)
                ;

            // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately
            chart.xAxis
                .axisLabel("Années")
                .tickFormat(d3.format('.f'));

            chart.yAxis
                .axisLabel('Offres')
                .tickFormat(d3.format('.f'));

            chart.showXAxis(true);

            d3.select('svg#chart_offers_period')
                .datum(json)
                .transition()
                .call(chart);

            nv.utils.windowResize(chart.update);
            chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });
            return chart;
        });

     },
     crossDomain: false
    });
}



function types_contract_global(in_data) {
    $("#title_contracts_type_pie").text("Proportion par type de contrat");
    nv.addGraph(function () {
            chart = nv.models.pieChart()
                .x(function (d) { return d.x })
                .y(function (d) { return d.y })
                .donut(true)
                .padAngle(.08)
                .cornerRadius(5)
                .labelsOutside(true).donut(true)
                .showTooltipPercent(true)
                .valueFormat(d3.format(".0f"))
                .duration(300);

            d3.select('svg#chart_contracts_type_pie')
                .datum(in_data)
                .transition().duration(1000)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
        };


function types_contract_by_period(period) {
    $.ajax({
     type: "GET",
     url: 'get_types_contract_by_period',
     data: {period: period},
     dataType: "json",
     success: function(json) {

        var chart;
        nv.addGraph(function() {
            chart = nv.models.stackedAreaChart()
                .useInteractiveGuideline(true)
                .x(function(d) { return d[0] })
                .y(function(d) { return d[1] })
                .controlLabels({stacked: "Cumul", stream: "Flux", expanded: "Proportion"})
                .duration(300);

            chart.xAxis
                .axisLabel("Années")
                .tickFormat(d3.format('.f'));

            chart.yAxis
                .axisLabel('Offres')
                .tickFormat(d3.format('.f'));

            chart.legend.vers('furious');

            d3.select('svg#chart_types_contract_period')
                .datum(json)
                .transition().duration(1000)
                .call(chart)
                .each('start', function() {
                    setTimeout(function() {
                        d3.selectAll('svg#chart_types_contract_period *').each(function() {
                            if(this.__transition__)
                                this.__transition__.duration = 1;
                        })
                    }, 0)
                });

            nv.utils.windowResize(chart.update);
            return chart;
        });


     },
     crossDomain: false
    });
};


function contracts_by_technos() {
    $.ajax({
     type: "GET",
     url: 'get_contracts_by_technos',
     dataType: "json",
     success: function(json) {
        $("#title_technos_pie").text("Nombre d'offres par technologie (top 5)");

        var chart;
        nv.addGraph(function() {
            chart = nv.models.lineChart();
            chart
                .margin({left: 30, bottom: 50, up: 10})  //Adjust chart margins to give the axis some breathing room
                .showLegend(true)
                .useInteractiveGuideline(true)  // tooltips and guideline
                .x(function(d) { return d[0] })
                .y(function(d) { return d[1] })
                .duration(400)
                ;

            // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately
            chart.xAxis
                .axisLabel("Années")
                .tickFormat(d3.format('.f'))
                .staggerLabels(false)
                ;

            chart.yAxis
                .axisLabel('Offres')
                .tickFormat(d3.format('.f'))
                ;

            /*chart.showXAxis(true);*/

            d3.select('svg#chart_technos_pie')
                .datum(json)
                .call(chart)
                ;

            nv.utils.windowResize(chart.update());
            return chart;
        });

     },
     crossDomain: false
    });
};

function contracts_by_french_dpts_toms() {
    $.ajax({
        type: "GET",
        url: 'get_fr_dpts_top10',
        dataType: "json",
        success: function (json) {
            $("#title_fr_dpts_toms_pie").text("Top 10 des départements français");
            nv.addGraph(function () {
                chart = nv.models.pieChart()
                    .x(function (d) { return d.x })
                    .y(function (d) { return d.y })
                    .cornerRadius(5)
                    .labelsOutside(true).donut(true)
                    .showTooltipPercent(true)
                    .valueFormat(d3.format(".0f"))
                    .duration(300);

                d3.select('svg#chart_fr_dpts_toms_pie')
                    .datum(json)
                    .transition().duration(1000)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        },
        crossDomain: false
    });
};


function contracts_by_countries() {
    $.ajax({
        type: "GET",
        url: 'get_countries_top5',
        dataType: "json",
        success: function (json) {
            $("#title_countries_pie").text("Top 5 pays étrangers");
            nv.addGraph(function () {
                chart = nv.models.pieChart()
                    .x(function (d) { return d.x })
                    .y(function (d) { return d.y })
                    .cornerRadius(5)
                    .labelsOutside(true).donut(true)
                    .showTooltipPercent(true)
                    .valueFormat(d3.format(".0f"))
                    .duration(300);

                d3.select('svg#chart_countries_pie')
                    .datum(json)
                    .transition().duration(1000)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        },
        crossDomain: false
    });
};
