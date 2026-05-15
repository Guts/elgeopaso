// map.js - accès direct à l'API elgeopasso avec filtre par type de contrat
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
        [-11.5, 40.0],
        [17.5, 52.0]
    ]);

    // LIMITES DE ZOOM
    map.setMinZoom(3);
    map.setMaxZoom(20);

    // Variables pour stocker les données
    var jobsData = [];
    var jobCountsByDepartment = {};
    var currentFilter = 'all'; // 'all', 'CDI', 'CDD', 'Stage', etc.
    var availableContractTypes = new Set();




    // Fonction pour récupérer les données directement depuis l'API geoelpasso
    // Pas de proxy Django, on appelle l'API directe
    // function fetchJobsData() {
    //     // URL directe de l'API - plus de /jobs/proxy/jobs/
    //     const externalApiUrl = 'https://elgeopaso.georezo.net/api/offres/?format=json&offset=25635&limit=100';

    //     // console.log('Tentative d\'accès direct à l\'API externe:', externalApiUrl);
    //     // console.warn('⚠️ Une erreur CORS, l\'API ne permet pas l\'accès direct depuis le navigateur');

    //     return fetch(externalApiUrl)
    //         .then(response => {
    //             if (!response.ok) {
    //                 throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
    //             }
    //             return response.json();
    //         })
    //         .then(data => {
    //             // console.log('✅ Données récupérées avec succès (CORS autorisé apparemment)');

    //             if (data.error) {
    //                 // console.error('Erreur dans les données:', data.error);
    //                 jobsData = [];
    //             } else {
    //                 // La nouvelle API retourne un objet avec une propriété "results"
    //                 if (data.results && Array.isArray(data.results)) {
    //                     jobsData = data.results;
    //                     // console.log(`${jobsData.length} offres chargées depuis data.results`);
    //                 } else if (Array.isArray(data)) {
    //                     jobsData = data;
    //                     // console.log(`${jobsData.length} offres chargées (format tableau direct)`);
    //                 } else {
    //                     // console.warn('Format de données non reconnu:', data);
    //                     jobsData = [];
    //                 }
    //                 jobCountsByDepartment = countJobsByDepartment(jobsData);
    //                 // console.log(`${Object.keys(jobCountsByDepartment).length} départements concernés`);
    //             }
    //             return jobsData;
    //         })
    //         .catch(error => {
    //             // Erreur CORS: "Failed to fetch" ou "Cross-Origin Request Blocked"
    //             // console.error('❌ Erreur fetchJobsData:', error);
    //             // console.error('Une erreur CORS - le navigateur bloque l\'accès à l\'API externe');
    //             jobsData = [];
    //             return [];
    //         });
    // }














    // Fonction pour récupérer les données directement depuis l'API geoelpasso
    function fetchJobsData() {
        const countUrl = 'https://cors-anywhere.herokuapp.com/https://elgeopaso.georezo.net/api/offres/?format=json&limit=1';

        return fetch(countUrl, {
            method: 'GET',
            headers: {
                'Origin': window.location.origin,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const totalCount = data.count;
            const offset = Math.max(0, totalCount - 60);
            const externalApiUrl = `https://cors-anywhere.herokuapp.com/https://elgeopaso.georezo.net/api/offres/?format=json&offset=${offset}&limit=60`;

            return fetch(externalApiUrl, {
                method: 'GET',
                headers: {
                    'Origin': window.location.origin,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.results && Array.isArray(data.results)) {
                jobsData = data.results;
            } else if (Array.isArray(data)) {
                jobsData = data;
            } else {
                jobsData = [];
            }

            // Collecter les types de contrats disponibles
            availableContractTypes.clear();
            jobsData.forEach(job => {
                if (job.contract && job.contract.abbrv) {
                    availableContractTypes.add(job.contract.abbrv);
                }
            });

            // Mettre à jour l'UI du filtre
            updateFilterUI();

            // Appliquer le filtre actuel
            applyFilter();

            return jobsData;
        })
        .catch(error => {
            console.error('❌ Erreur fetchJobsData:', error);
            jobsData = [];
            return [];
        });
    }

    // Fonction pour compter les offres par département avec filtre
    function countJobsByDepartment(jobs) {
        var counts = {};

        jobs.forEach(job => {
            if (job.place && job.place.code) {
                var code = String(job.place.code).padStart(2, '0');
                counts[code] = (counts[code] || 0) + 1;
            }
        });

        return counts;
    }

    // Appliquer le filtre actuel
    function applyFilter() {
        var filteredJobs = jobsData;

        if (currentFilter !== 'all') {
            filteredJobs = jobsData.filter(job => {
                return job.contract && job.contract.abbrv === currentFilter;
            });
        }

        jobCountsByDepartment = countJobsByDepartment(filteredJobs);

        // Mettre à jour les cercles sur la carte
        if (window.geojsonData) {
            updateJobCircles(window.geojsonData);
        }
    }

    // Mettre à jour l'interface du filtre
    function updateFilterUI() {
        // Créer ou mettre à jour le conteneur du filtre
        var filterContainer = document.getElementById('contract-filter');
        if (!filterContainer) {
            filterContainer = document.createElement('div');
            filterContainer.id = 'contract-filter';
            filterContainer.style.cssText = `
                position: absolute;
                top: 60px;
                left: 10px;
                z-index: 1000;
                background: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                font-family: Arial, sans-serif;
                min-width: 150px;
            `;
            document.body.appendChild(filterContainer);
        }

        // Trier les types de contrats
        var sortedTypes = Array.from(availableContractTypes).sort();

        var html = `
            <div style="font-weight: bold; margin-bottom: 8px; color: #333;">
                📋 Filtrer par contrat
            </div>
            <select id="contract-type-select" style="
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                cursor: pointer;
            ">
                <option value="all" ${currentFilter === 'all' ? 'selected' : ''}>
                    Tous les contrats (${jobsData.length})
                </option>
        `;

        sortedTypes.forEach(type => {
            var count = jobsData.filter(job => job.contract && job.contract.abbrv === type).length;
            html += `
                <option value="${type}" ${currentFilter === type ? 'selected' : ''}>
                    ${type} (${count})
                </option>
            `;
        });

        html += `</select>`;

        // Ajouter des statistiques
        html += `
            <div style="margin-top: 10px; font-size: 11px; color: #666; border-top: 1px solid #eee; padding-top: 8px;">
                <div>📊 Affichés: ${Object.values(jobCountsByDepartment).reduce((a,b) => a+b, 0)} offres</div>
                <div>🗺️ ${Object.keys(jobCountsByDepartment).length} départements</div>
            </div>
        `;

        filterContainer.innerHTML = html;

        // Ajouter l'événement de changement
        document.getElementById('contract-type-select').addEventListener('change', function(e) {
            currentFilter = e.target.value;
            applyFilter();

            // Mettre à jour l'UI avec les nouvelles stats
            updateFilterUI();

            // Rafraîchir la popup si elle est ouverte
            if (window.currentPopupDept) {
                showJobListPopup(window.currentPopupDept.code, window.currentPopupDept.name, window.currentPopupDept.location);
            }
        });
    }

    // Fonction pour récupérer les offres d'un département spécifique (avec filtre)
    function getJobsForDepartment(deptCode) {
        var filteredJobs = jobsData;

        if (currentFilter !== 'all') {
            filteredJobs = jobsData.filter(job => {
                return job.contract && job.contract.abbrv === currentFilter;
            });
        }

        return filteredJobs.filter(job => {
            if (!job.place || !job.place.code) return false;
            var code = String(job.place.code).padStart(2, '0');
            return code === deptCode;
        });
    }

    // Fonction pour créer l'URL de l'offre
    function getJobUrl(job) {
        if (job.raw_offer) {
            return `https://georezo.net/forum/viewtopic.php?id=${job.raw_offer}`;
        }
        if (job.id) {
            return `https://georezo.net/forum/viewtopic.php?id=${job.id}`;
        }
        return '#';
    }

    // Fonction pour afficher la popup avec la liste des offres
    function showJobListPopup(deptCode, deptName, clickLocation) {
        // Stocker les infos pour rafraîchissement
        window.currentPopupDept = {
            code: deptCode,
            name: deptName,
            location: clickLocation
        };

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
                    ${currentFilter !== 'all' ? `
                        <div style="
                            margin-top: 8px;
                            font-size: 12px;
                            background: rgba(255,255,255,0.15);
                            padding: 4px 8px;
                            border-radius: 4px;
                            display: inline-block;
                        ">
                            🔍 Filtre: ${currentFilter}
                        </div>
                    ` : ''}
                </div>

                <div style="padding: 15px; max-height: 350px; overflow-y: auto;">
        `;

        if (jobCount > 0) {
            departmentJobs.forEach((job, index) => {
                var jobTitle = job.title || 'Sans titre';
                var jobUrl = getJobUrl(job);

                // Supprimer le code département à la fin si présent
                jobTitle = jobTitle.replace(/\s*\(\d+\)\s*$/, '');

                // Extraire le type de poste entre crochets
                var jobType = '';
                var typeMatch = jobTitle.match(/^\[(.*?)\]/);
                if (typeMatch) {
                    jobType = typeMatch[1];
                    jobTitle = jobTitle.replace(/^\[.*?\]\s*/, '');
                }

                // Utiliser contract.abbrv si disponible
                var contractType = job.contract?.abbrv || jobType || 'Non spécifié';
                var contractName = job.contract?.name || '';

                // Tronquer les titres longs
                var displayTitle = jobTitle;
                if (jobTitle.length > 80) {
                    displayTitle = jobTitle.substring(0, 77) + '...';
                }

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
                                <div style="margin-top: 5px;">
                                    <span style="
                                        display: inline-block;
                                        background: ${contractType === 'Stage' ? '#10b981' : contractType === 'CDI' ? '#3b82f6' : contractType === 'CDD' ? '#f59e0b' : '#8b5cf6'};
                                        color: white;
                                        padding: 2px 8px;
                                        border-radius: 12px;
                                        font-size: 11px;
                                        font-weight: bold;
                                        margin-right: 5px;
                                    ">
                                        ${contractType}
                                    </span>
                                    ${job.place?.name ? `
                                        <span style="
                                            display: inline-block;
                                            background: #e0e7ff;
                                            color: #4f46e5;
                                            padding: 2px 8px;
                                            border-radius: 12px;
                                            font-size: 11px;
                                        ">
                                            📍 ${job.place.name}
                                        </span>
                                    ` : ''}
                                </div>
                                ${jobTitle.length > 80 ? `
                                    <div style="margin-top: 5px; font-size: 11px; color: #666; font-style: italic;">
                                        ${jobTitle}
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
                    Aucune offre ${currentFilter !== 'all' ? `de type "${currentFilter}" ` : ''}disponible dans ce département
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

        if (window.jobListPopup) {
            window.jobListPopup.remove();
        }

        window.jobListPopup = new mapboxgl.Popup({
            closeButton: true,
            closeOnClick: true,
            maxWidth: '500px',
            className: 'job-list-popup'
        })
        .setLngLat(clickLocation)
        .setHTML(popupContent)
        .addTo(map);

        // Nettoyer la référence quand la popup est fermée
        window.jobListPopup.on('close', function() {
            window.currentPopupDept = null;
        });
    }

    // Mettre à jour les cercles sur la carte
    function updateJobCircles(geojsonData) {
        var circleFeatures = [];

        geojsonData.features.forEach(feature => {
            var deptCode = feature.properties.dep || feature.properties.code;
            var jobCount = jobCountsByDepartment[deptCode];

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

    // Fonctions utilitaires pour les cercles
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
        fetch('/static/geojson/fr_departements_jobs.geojson')
            .then(response => response.json())
            .then(geojsonData => {
                window.geojsonData = geojsonData;

                map.addSource('departments', {
                    type: 'geojson',
                    data: geojsonData
                });

                map.addLayer({
                    id: 'departments-fill',
                    type: 'fill',
                    source: 'departments',
                    paint: {
                        'fill-color': '#ADD8E6',
                        'fill-opacity': 0.3
                    }
                });

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

                fetchJobsData().then(() => {
                    updateJobCircles(geojsonData);
                });

                var hoverPopup = null;

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
                                ${currentFilter !== 'all' ? `<small style="display:block;">🔍 Filtre: ${currentFilter}</small>` : ''}
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
                            ${currentFilter !== 'all' ? `<small style="display:block;">🔍 Filtre: ${currentFilter}</small>` : ''}
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

                map.on('click', 'departments-fill', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.dep || props.code;
                        var deptName = props.nom || props.name || 'Département';
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        highlightDepartment(deptCode, geojsonData);
                    }
                });

                map.on('click', 'job-circles', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.deptCode;
                        var deptName = props.deptName;
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        highlightDepartment(deptCode, geojsonData);
                    }
                });

                map.on('click', 'job-circle-labels', function(e) {
                    if (e.features.length > 0) {
                        var props = e.features[0].properties;
                        var deptCode = props.deptCode;
                        var deptName = props.deptName;
                        showJobListPopup(deptCode, deptName, e.lngLat);
                        highlightDepartment(deptCode, geojsonData);
                    }
                });

                function highlightDepartment(deptCode, geojsonData) {
                    if (map.getLayer('highlight-layer')) {
                        map.removeLayer('highlight-layer');
                    }
                    if (map.getSource('highlight')) {
                        map.removeSource('highlight');
                    }

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

    // Ajouter le CSS personnalisé
    var style = document.createElement('style');
    style.textContent = `
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
