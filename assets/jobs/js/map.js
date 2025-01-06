$(document).ready(function () {
    var map = new mapboxgl.Map({
        container: 'map-fr-metro',
        style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json',
        center: [2.6, 45.5],
        zoom: 4.7
    });

    // CUSTOM MAP
    // disable map rotation using right click + drag
    map.dragRotate.disable();
    // disable map rotation using touch rotation gesture
    map.touchZoomRotate.disableRotation();

    // Add zoom and rotation controls to the map.
    map.addControl(new mapboxgl.NavigationControl());

    // ADD DATA
    map.on('load', function () {
        map.addLayer({
            id: "boundaries",
            type: 'circle',
            source: {
                type: 'geojson',
                data: static_url + "jobs/geojson/fr_departements_jobs_centroids.geojson"
            },
            // filter: ['>=', ['number', ['get', 'JOBS_TOTAL']], 1],
            paint: {
                'circle-radius': [
                    'interpolate',
                    ['linear'],
                    ['number', ['get', 'JOBS_TOTAL']],
                    0, 4,
                    5, 24
                ],
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['number', ['get', 'JOBS_TOTAL']],
                    0, '#2DC4B2',
                    1, '#3BB3C3',
                    2, '#669EC4',
                    3, '#8B88B6',
                    4, '#A2719B',
                    5, '#AA5E79'
                ],
                'circle-opacity': 0.8
            }
        });

        document.getElementById('slider').addEventListener('input', function (e) {
            var year = parseInt(e.target.value);
            console.log("selected year: " + year);
            console.log("selected property: " + 'JOBS_' + year);

            // update the map
            // map.setFilter('boundaries', ['==', 'JOBS_' + year, 'JOBS_' + year]);
            map.setPaintProperty('boundaries', 'circle-radius', ['number', ['get', 'JOBS_' + year]]);

            // update text in the UI
            document.getElementById('active-year').innerText = year;
        });

        // Change the cursor to a pointer when the mouse is over the states layer.
        map.on('mouseenter', 'boundaries', function () {
            map.getCanvas().style.cursor = 'pointer';
        });
        // Change it back to a pointer when it leaves.
        map.on('mouseleave', 'boundaries', function () {
            map.getCanvas().style.cursor = '';
        });


        // When a click event occurs on a feature in the states layer, open a popup at the
        // location of the click, with description HTML from its properties.
        map.on('click', 'boundaries', function (e) {
            new mapboxgl.Popup()
                .setLngLat(e.lngLat)
                .setHTML('</h4>' + e.features[0].properties.nom + '</h4>' +
                    ' (' + e.features[0].properties.code + ')<br />' + e.features[0].properties.JOBS_TOTAL + ' offres')
                .addTo(map);
        });

        map.on("load", function (e) {
            map.resize();
        });
    });

});
