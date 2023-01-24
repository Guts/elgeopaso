$(document).ready(function () {
    var map = new mapboxgl.Map({
        container: 'map-fr-idf',
        style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json',
        center: [2.35, 48.86],
        zoom: 8
    });

    // CUSTOM MAP
    // disable map rotation using right click + drag
    map.dragRotate.disable();
    // disable map rotation using touch rotation gesture
    map.touchZoomRotate.disableRotation();

    // Add zoom and rotation controls to the map.
    // map.addControl(new mapboxgl.NavigationControl());

    // ADD DATA
    map.on('load', function () {
        map.addSource("departements-fr", {
            "type": "geojson",
            "data": static_url + "jobs/geojson/fr_departements_jobs.geojson"
        });

        map.addLayer({
            "id": "boundaries",
            'type': 'fill',
            'layout': {},
            "source": "departements-fr",
            'paint': {
                'fill-color': '#AEBBFF',
                'fill-opacity': 0.7,
                'fill-outline-color': '#000000'

            }
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
