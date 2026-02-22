$(document).ready(function () {
    // Création de la carte
    var map = new mapboxgl.Map({
        container: 'map-container',
        style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json',
        center: [2.6, 45.5],
        zoom: 4,
        wheelZoomRate: 1.0,
        wheelPitchRate: 0.5,
        interactive: true,
        attributionControl: false
    });
    
    // OPTIMISATION DU ZOOM
    map.scrollZoom.setWheelZoomRate(1.0);
    map.scrollZoom.setZoomRate(1.0);
    
    // LIMITES DE LA CARTE - EMPÊCHER DE QUITTER LA FRANCE
    map.setMaxBounds([
        [-11.5, 35.0],
        [17.5, 55.5]
    ]);
    
    // LIMITES DE ZOOM
    map.setMinZoom(3);
    map.setMaxZoom(20);

    // Variables pour stocker les données
    var jobsData = [];
    var jobCountsByDepartment = {};
    
    // Fonction pour récupérer les données via le proxy Django (adaptée à la nouvelle structure)
    function fetchJobsData() {
        return fetch('/jobs/proxy/jobs/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur de réponse du proxy Django');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    jobsData = [];
                } else {
                    // La nouvelle API retourne un objet avec une propriété "results"
                    if (data.results && Array.isArray(data.results)) {
                        jobsData = data.results;
                    } else if (Array.isArray(data)) {
                        // Fallback pour l'ancien format si nécessaire
                        jobsData = data;
                    } else {
                        jobsData = [];
                    }
                    jobCountsByDepartment = countJobsByDepartment(jobsData);
                }
                return jobsData;
            })
            .catch(error => {
                console.error('Erreur fetchJobsData:', error);
                jobsData = [];
                return [];
            });
    }
    
    // Fonction pour compter les offres par département (adaptée à la nouvelle structure)
    function countJobsByDepartment(jobs) {
        var counts = {};
        
        jobs.forEach(job => {
            // Dans la nouvelle structure, le lieu est dans un objet "place"
            if (job.place && job.place.code) {
                var code = String(job.place.code).padStart(2, '0');
                counts[code] = (counts[code] || 0) + 1;
            }
            
            // Note: place_2 n'existe plus dans la nouvelle structure
            // Si vous avez besoin de gérer un deuxième lieu, il faudrait adapter
        });
        
        return counts;
    }
    
    // Fonction pour récupérer les offres d'un département spécifique (adaptée)
    function getJobsForDepartment(deptCode) {
        if (!jobsData.length) return [];
        
        return jobsData.filter(job => {
            if (!job.place || !job.place.code) return false;
            var code = String(job.place.code).padStart(2, '0');
            return code === deptCode;
        });
    }
    
    // Fonction pour créer l'URL de l'offre (adaptée)
    function getJobUrl(job) {
        // Utilisation de raw_offer comme identifiant (nouveau champ)
        if (job.raw_offer) {
            return `https://georezo.net/forum/viewtopic.php?id=${job.raw_offer}`;
        }
        // Fallback sur l'id si raw_offer n'existe pas
        if (job.id) {
            return `https://georezo.net/forum/viewtopic.php?id=${job.id}`;
        }
        return '#';
    }
    
    // Fonction pour afficher la popup avec la liste des offres (adaptée)
    function showJobListPopup(deptCode, deptName, clickLocation) {
        var departmentJobs = getJobsForDepartment(deptCode);
        var jobCount = departmentJobs.length;
        
        // Création du contenu de la popup
        var popupContent = `
            <div style="padding: 0; max-width: 450px; max-height: 500px; overflow: hidden;">
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px;
                    margin: 0;
                ">
                    <h3 style="margin: 0 0 5px 0; font-size: 18px;">
                        ${deptName}
                    </h3>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 14px; opacity: 0.9;">
                            Code: ${deptCode}
                        </div>
                        <div style="
                            background: rgba(255,255,255,0.2);
                            padding: 4px 12px;
                            border-radius: 20px;
                            font-weight: bold;
                            font-size: 16px;
                        ">
                            ${jobCount} offre${jobCount !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
                
                <div style="padding: 15px; max-height: 350px; overflow-y: auto;">
        `;
        
        if (jobCount > 0) {
            departmentJobs.forEach((job, index) => {
                // Nettoyage du titre (utilisation de "title" au lieu de "lib")
                var jobTitle = job.title || 'Sans titre';
                var jobUrl = getJobUrl(job);
                
                // Supprimer le code département à la fin si présent
                jobTitle = jobTitle.replace(/\s*\(\d+\)\s*$/, '');
                
                // Extraire le type de poste entre crochets (à partir de "title")
                var jobType = '';
                var typeMatch = jobTitle.match(/^\[(.*?)\]/);
                if (typeMatch) {
                    jobType = typeMatch[1];
                    jobTitle = jobTitle.replace(/^\[.*?\]\s*/, '');
                }
                
                // Si le type n'est pas dans le titre, on peut aussi utiliser job.contract?.abbrv
                if (!jobType && job.contract && job.contract.abbrv) {
                    jobType = job.contract.abbrv;
                }
                
                // Tronquer les titres longs
                var displayTitle = jobTitle;
                if (jobTitle.length > 80) {
                    displayTitle = jobTitle.substring(0, 77) + '...';
                }
                
                // Déterminer l'identifiant à afficher (raw_offer ou id)
                var jobId = job.raw_offer || job.id || '';
                
                popupContent += `
                    <div style="
                        padding: 12px;
                        margin-bottom: 10px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        border-left: 4px solid #667eea;
                        transition: all 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.background='#eef2ff'; this.style.transform='translateY(-2px)';" 
                       onmouseout="this.style.background='#f8f9fa'; this.style.transform='translateY(0)';"
                       onclick="window.open('${jobUrl}', '_blank');">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="flex: 1;">
                                <div style="font-weight: bold; color: #2c3e50; margin-bottom: 4px; font-size: 14px;">
                                    ${displayTitle}
                                    <span style="margin-left: 8px; font-size: 12px; color: #667eea;">
                                        🔗
                                    </span>
                                </div>
                                ${jobType ? `
                                    <div style="
                                        display: inline-block;
                                        background: #e0e7ff;
                                        color: #4f46e5;
                                        padding: 2px 8px;
                                        border-radius: 12px;
                                        font-size: 11px;
                                        font-weight: bold;
                                        margin-top: 5px;
                                        margin-right: 5px;
                                    ">
                                        ${jobType}
                                    </div>
                                ` : ''}
                                ${jobTitle.length > 80 ? `
                                    <div style="
                                        display: inline-block;
                                        color: #666;
                                        font-size: 11px;
                                        font-style: italic;
                                        margin-top: 5px;
                                    ">
                                        (cliquer pour voir les détails)
                                    </div>
                                ` : ''}
                            </div>
                            ${jobId ? `
                                <div style="
                                    background: #f1f5f9;
                                    color: #64748b;
                                    padding: 4px 8px;
                                    border-radius: 4px;
                                    font-size: 11px;
                                    font-family: monospace;
                                    margin-left: 10px;
                                    white-space: nowrap;
                                ">
                                    #${jobId}
                                </div>
                            ` : ''}
                        </div>
                        ${jobTitle.length > 80 ? `
                            <div style="margin-top: 5px; font-size: 11px; color: #666; font-style: italic;">
                                ${jobTitle}
                            </div>
                        ` : ''}
                        <div style="margin-top: 8px; font-size: 11px; color: #4f46e5;">
                            <span style="background: #e0e7ff; padding: 2px 6px; border-radius: 3px;">
                                Cliquer pour voir l'offre complète →
                            </span>
                        </div>
                    </div>
                `;
            });
        } else {
            popupContent += `
                <div style="
                    text-align: center;
                    padding: 40px 20px;
                    color: #94a3b8;
                    font-size: 16px;
                ">
                    <div style="font-size: 48px; margin-bottom: 40px;">📭</div>
                    Aucune offre disponible dans ce département
                </div>
            `;
        }
        
        popupContent += `
                </div>
                
                ${jobCount > 0 ? `
                    <div style="
                        padding: 10px 15px;
                        background: #f8fafc;
                        border-top: 1px solid #e2e8f0;
                        font-size: 12px;
                        color: #64748b;
                        text-align: center;
                    ">
                        <div>
                            <span style="color: #4f46e5; font-weight: bold;">💡 Astuce :</span> 
                            Cliquez sur une offre pour l'ouvrir sur Georezo.net
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Supprimer la popup existante si elle existe
        if (window.jobListPopup) {
            window.jobListPopup.remove();
        }
        
        // Créer et afficher la nouvelle popup
        window.jobListPopup = new mapboxgl.Popup({
            closeButton: true,
            closeOnClick: true,
            maxWidth: '500px',
            className: 'job-list-popup'
        })
        .setLngLat(clickLocation)
        .setHTML(popupContent)
        .addTo(map);
    }
    
    // Fonction pour ajouter les CERCLES avec le nombre d'offres (inchangée)
    function addJobCircles(geojsonData) {
        var circleFeatures = [];
        
        geojsonData.features.forEach(feature => {
            var deptCode = feature.properties.dep || feature.properties.code;
            var jobCount = jobCountsByDepartment[deptCode];
            
            // Ajouter un cercle seulement si le département a des offres
            if (jobCount && jobCount > 0) {
                var center = getFeatureCenter(feature);
                
                if (center) {
                    circleFeatures.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: center
                        },
                        properties: {
                            deptCode: deptCode,
                            jobCount: jobCount,
                            deptName: feature.properties.nom || feature.properties.name
                        }
                    });
                }
            }
        });
        
        // Ajouter ou mettre à jour la source des cercles
        if (map.getSource('job-circles')) {
            map.getSource('job-circles').setData({
                type: 'FeatureCollection',
                features: circleFeatures
            });
        } else {
            map.addSource('job-circles', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: circleFeatures
                }
            });
            
            // Ajouter la couche des cercles
            map.addLayer({
                id: 'job-circles',
                type: 'circle',
                source: 'job-circles',
                paint: {
                    'circle-radius': [
                        'interpolate',
                        ['linear'],
                        ['get', 'jobCount'],
                        1, 10,
                        5, 15,
                        10, 20,
                        20, 25,
                        50, 30
                    ],
                    'circle-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'jobCount'],
                        1, '#4CAF50',
                        5, '#FF9800',
                        10, '#FF5722',
                        20, '#F44336',
                        50, '#D32F2F'
                    ],
                    'circle-opacity': 0.8,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#FFFFFF',
                    'circle-stroke-opacity': 0.9
                }
            });
            
            // Ajouter une couche pour les labels dans les cercles
            map.addLayer({
                id: 'job-circle-labels',
                type: 'symbol',
                source: 'job-circles',
                layout: {
                    'text-field': ['get', 'jobCount'],
                    'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
                    'text-size': [
                        'interpolate',
                        ['linear'],
                        ['get', 'jobCount'],
                        1, 10,
                        5, 12,
                        10, 14,
                        20, 16,
                        50, 18
                    ],
                    'text-allow-overlap': true,
                    'text-ignore-placement': true
                },
                paint: {
                    'text-color': '#FFFFFF',
                    'text-halo-color': 'rgba(0, 0, 0, 0.3)',
                    'text-halo-width': 1
                }
            });
        }
    }
    
    // Fonctions getCircleSize, getCircleColor, getFeatureCenter, getPolygonCenter (inchangées)
    function getCircleSize(jobCount) {
        if (jobCount >= 50) return 30;
        if (jobCount >= 20) return 25;
        if (jobCount >= 10) return 20;
        if (jobCount >= 5) return 15;
        return 10;
    }
    
    function getCircleColor(jobCount) {
        if (jobCount >= 50) return '#D32F2F';
        if (jobCount >= 20) return '#F44336';
        if (jobCount >= 10) return '#FF5722';
        if (jobCount >= 5) return '#FF9800';
        return '#4CAF50';
    }
    
    function getFeatureCenter(feature) {
        var coordinates = feature.geometry.coordinates;
        
        if (feature.geometry.type === 'Polygon') {
            return getPolygonCenter(coordinates);
        } else if (feature.geometry.type === 'MultiPolygon') {
            return getPolygonCenter(coordinates[0]);
        }
        return null;
    }
    
    function getPolygonCenter(coordinates) {
        var totalLat = 0;
        var totalLng = 0;
        var count = 0;
        
        coordinates[0].forEach(point => {
            totalLng += point[0];
            totalLat += point[1];
            count++;
        });
        
        return count > 0 ? [totalLng / count, totalLat / count] : null;
    }
    
    // Quand la carte est chargée
    map.on('load', function () {
        // Charger le GeoJSON des départements
        fetch('/static/geojson/fr_departements_jobs.geojson')
            .then(response => response.json())
            .then(geojsonData => {
                // Ajouter la source des départements
                map.addSource('departments', {
                    type: 'geojson',
                    data: geojsonData
                });
                
                // Couche de remplissage
                map.addLayer({
                    id: 'departments-fill',
                    type: 'fill',
                    source: 'departments',
                    paint: {
                        'fill-color': '#ADD8E6',
                        'fill-opacity': 0.3
                    }
                });
                
                // Couche des bordures
                map.addLayer({
                    id: 'departments-border',
                    type: 'line',
                    source: 'departments',
                    paint: {
                        'line-color': '#6474ff',
                        'line-width': 2,
                        'line-opacity': 0.9
                    }
                });
                
                // Récupérer les données et ajouter les cercles
                fetchJobsData().then(() => {
                    addJobCircles(geojsonData);
                });
                
                // Popup au survol des cercles
                var hoverPopup = null;
                
                // Gestion du survol des départements
                map.on('mousemove', 'departments-fill', function(e) {
                    map.getCanvas().style.cursor = 'pointer';
                    
                    if (e.features.length > 0) {
                        if (hoverPopup) hoverPopup.remove();
                        
                        var props = e.features[0].properties;
                        var deptCode = props.dep || props.code;
                        var jobCount = jobCountsByDepartment[deptCode] || 0;
                        
                        var popupContent = `
                            <div style="padding: 10px; min-width: 180px;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <strong style="flex: 1;">${props.nom || props.name}</strong>
                                    ${jobCount > 0 ? `
                                        <span style="
                                            background: ${getCircleColor(jobCount)};
                                            color: white;
                                            padding: 4px 8px;
                                            border-radius: 50%;
                                            font-weight: bold;
                                            width: 30px;
                                            height: 30px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                        ">
                                            ${jobCount}
                                        </span>
                                    ` : ''}
                                </div>
                                <small>Code: ${deptCode}</small>
                                ${jobCount > 0 ? `
                                    <div style="margin-top: 8px; font-size: 12px; color: #4f46e5;">
                                        <span style="background: #e0e7ff; padding: 2px 6px; border-radius: 3px;">
                                            Cliquer pour voir ${jobCount} offre${jobCount !== 1 ? 's' : ''} →
                                        </span>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                        
                        hoverPopup = new mapboxgl.Popup({
                            closeButton: false,
                            closeOnClick: false
                        })
                        .setLngLat(e.lngLat)
                        .setHTML(popupContent)
                        .addTo(map);
                    }
                });
                
                // Gestion du survol des cercles
                map.on('mousemove', 'job-circles', function(e) {
                    map.getCanvas().style.cursor = 'pointer';
                    
                    if (hoverPopup) hoverPopup.remove();
                    
                    var props = e.features[0].properties;
                    var deptName = props.deptName;
                    var jobCount = props.jobCount;
                    var deptCode = props.deptCode;
                    
                    var popupContent = `
                        <div style="padding: 10px; min-width: 180px;">
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <strong style="flex: 1;">${deptName}</strong>
                                <span style="
                                    background: ${getCircleColor(jobCount)};
                                    color: white;
                                    padding: 4px 8px;
                                    border-radius: 50%;
                                    font-weight: bold;
                                    width: 30px;
                                    height: 30px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                                    ${jobCount}
                                </span>
                            </div>
                            <small>Code: ${deptCode}</small>
                            <div style="margin-top: 8px; font-size: 12px; color: #4f46e5;">
                                <span style="background: #e0e7ff; padding: 2px 6px; border-radius: 3px;">
                                    Cliquer pour voir ${jobCount} offre${jobCount !== 1 ? 's' : ''} →
                                </span>
                            </div>
                        </div>
                    `;
                    
                    hoverPopup = new mapboxgl.Popup({
                        closeButton: false,
                        closeOnClick: false
                    })
                    .setLngLat(e.lngLat)
                    .setHTML(popupContent)
                    .addTo(map);
                });
                
                map.on('mouseleave', ['departments-fill', 'job-circles'], function() {
                    map.getCanvas().style.cursor = '';
                    if (hoverPopup) {
                        hoverPopup.remove();
                        hoverPopup = null;
                    }
                });
                
                // Événement CLIC sur les départements
                map.on('click', 'departments-fill', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.dep || props.code;
                        var deptName = props.nom || props.name || 'Département';
                        
                        // Afficher la popup avec la liste des offres
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        
                        // Mettre en évidence le département cliqué
                        highlightDepartment(deptCode, geojsonData);
                    }
                });
                
                // Événement CLIC sur les cercles
                map.on('click', 'job-circles', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.deptCode;
                        var deptName = props.deptName;
                        
                        // Afficher la popup avec la liste des offres
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        
                        // Mettre en évidence le département cliqué
                        highlightDepartment(deptCode, geojsonData);
                    }
                });
                
                // Événement CLIC sur les labels dans les cercles
                map.on('click', 'job-circle-labels', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.deptCode;
                        var deptName = props.deptName;
                        
                        // Afficher la popup avec la liste des offres
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        
                        // Mettre en évidence le département cliqué
                        highlightDepartment(deptCode, geojsonData);
                    }
                });
                
                // Fonction pour mettre en évidence le département cliqué (inchangée)
                function highlightDepartment(deptCode, geojsonData) {
                    // Supprimer la surbrillance existante
                    if (map.getLayer('highlight-layer')) {
                        map.removeLayer('highlight-layer');
                    }
                    if (map.getSource('highlight')) {
                        map.removeSource('highlight');
                    }
                    
                    // Trouver le département
                    var feature = geojsonData.features.find(f => 
                        (f.properties.dep || f.properties.code) === deptCode
                    );
                    
                    if (feature) {
                        map.addSource('highlight', {
                            type: 'geojson',
                            data: {
                                type: 'FeatureCollection',
                                features: [feature]
                            }
                        });
                        
                        map.addLayer({
                            id: 'highlight-layer',
                            type: 'fill',
                            source: 'highlight',
                            paint: {
                                'fill-color': '#FFD700',
                                'fill-opacity': 0.3,
                                'fill-outline-color': '#FFA500'
                            }
                        }, 'departments-border');
                    }
                }
            })
            .catch(error => {
                console.error('Erreur de chargement du GeoJSON:', error);
            });
    });
    
    // Ajouter le CSS personnalisé (inchangé)
    var style = document.createElement('style');
    style.textContent = `
        /* Masquer tous les contrôles Mapbox */
        .mapboxgl-ctrl-top-right,
        .mapboxgl-ctrl-top-left,
        .mapboxgl-ctrl-bottom-right,
        .mapboxgl-ctrl-bottom-left,
        .mapboxgl-ctrl-group,
        .mapboxgl-ctrl {
            display: none !important;
        }
        
        .job-list-popup .mapboxgl-popup-content {
            padding: 0 !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        }
        
        .job-list-popup .mapboxgl-popup-close-button {
            color: white !important;
            font-size: 20px !important;
            padding: 10px !important;
            z-index: 1000;
        }
        
        .job-list-popup div[onclick] {
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        
        .job-list-popup div[onclick]:hover {
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        }
        
        .job-list-popup div[style*="overflow-y: auto"]::-webkit-scrollbar {
            width: 8px;
        }
        
        .job-list-popup div[style*="overflow-y: auto"]::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .job-list-popup div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        
        .job-list-popup div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
    `;
    document.head.appendChild(style);
});