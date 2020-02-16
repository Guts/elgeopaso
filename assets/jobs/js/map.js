$(document).ready(function(){
    /* Basemap and basics */
    var map = L.map('map_lf_metro', {
                        scrollWheelZoom: false,
                        zoomControl: false
                    }).setView([46.279229, 2.454071], 6);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      minZoom: 5,
      maxZoom: 6,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'mapbox.light'
    }).addTo(map);

    /* Info on hover */
    var info = L.control();
        info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = (props ? '<h4>' + props.NOM_DEPT + '</h4>' + 
            '(' + props.NOM_REGION + ')<br />' + props.JOBS_TOTAL + ' offres'
          : 'Survolez un département'
          );
        };
    info.addTo(map);

    /* STYLE */
    var style_dpts = {
        "color": "#666699",
        "weight": 1,
        "fillOpacity": 0.1,
        "opacity": 0.5
    };

    /* HIGLIGHTS */
    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 2,
            color: '#009999',
            dashArray: '',
            fillOpacity: 0.7
        });

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            layer.bringToFront();
        }
        info.update(layer.feature.properties);
    }

    function resetHighlight(e) {
        geojsonLayer.resetStyle(e.target);
    };
    function whenClicked(e) {
   // e = event
   
        $("#title_dpt_histo").text("Statistique historique du département");

   /* CHART https://stackoverflow.com/a/37479585/2556577 */
      nv.addGraph(function(){
        var chart = nv.models.historicalBarChart();
        chart.margin({left: 100, bottom: 100})
             .useInteractiveGuideline(true)
             .duration(250)
            ;
        chart.xAxis
            .axisLabel("Années")
            .tickFormat(d3.format('.f'));

        chart.yAxis
            .axisLabel('Offres')
            .tickFormat(d3.format('.f'));

        chart.showXAxis(true);

        /*d3.select('#chart-' + e.CODE_DEPT + ' svg')*/
        d3.select('svg#chart_dpt_histo')
          .datum(e.histo)
          .transition()
          .call(chart)

        nv.utils.windowResize(chart.update);
        chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });
        return chart
      })
    }

    /* POPUP */
    function popUp(feature, layer) {
        layer.bindPopup("<b>Région : </b>" + feature.properties.NOM_REGION + "<br>"
                        + "<b>Département : </b>" + feature.properties.NOM_DEPT + "<br>"
                        + "<b>Nombre total d'offres parues : </b>" + feature.properties.JOBS_TOTAL.toString()
                        + "<br>Nombre d'offres par années :<br>"
                        + "<ul style='list-style-type:circle'>\
                            <li>2007 : " + feature.properties.JOBS_2007.toString() + "</li>\
                            <li>2008 : " + feature.properties.JOBS_2008.toString() + "</li>\
                            <li>2009 : " + feature.properties.JOBS_2009.toString() + "</li>\
                            <li>2010 : " + feature.properties.JOBS_2010.toString() + "</li>\
                            <li>2011 : " + feature.properties.JOBS_2011.toString() + "</li>\
                            <li>2012 : " + feature.properties.JOBS_2012.toString() + "</li>\
                            <li>2013 : " + feature.properties.JOBS_2013.toString() + "</li>\
                            <li>2014 : " + feature.properties.JOBS_2014.toString() + "</li>\
                            <li>2015 : " + feature.properties.JOBS_2015.toString() + "</li>\
                            <li>2016 : " + feature.properties.JOBS_2016.toString() + "</li>\
                            <li>2017 : " + feature.properties.JOBS_2017.toString() + "</li>\
                            <li>2018 : " + feature.properties.JOBS_2018.toString() + "</li>\
                        </ul>"
                        );
        layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                /* openPopup: whenClicked(feature.properties) */
                }
                );
    }

    /* Input GeoJSON */
    var geojsonLayer = new L.GeoJSON.AJAX(static_url  + 'jobs/geojson/dpts_metro_jobs.json',
                                          {onEachFeature: popUp,
                                           style: style_dpts}
                                          );
    geojsonLayer.addTo(map);
});
