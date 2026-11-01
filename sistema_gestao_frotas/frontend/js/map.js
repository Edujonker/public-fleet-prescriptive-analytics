/**
 * Controlador do Mapa Interativo Leaflet.js para Telemetria em Tempo Real e Geofencing
 */

let mapInstance = null;
let vehicleMarkers = {};
let geofenceLayers = [];
let routePolyline = null;

function initFleetMap() {
  const mapElement = document.getElementById('fleet-map');
  if (!mapElement) return;

  // Se já inicializado, apenas invalida o tamanho para renderização perfeita
  if (mapInstance) {
    mapInstance.invalidateSize();
    return;
  }

  // Centro padrão Sul / Sudeste
  mapInstance = L.map('fleet-map', {
    zoomControl: true,
  }).setView([-25.48, -49.12], 10);

  // Tiles limpos e modernos (CartoDB Voyager)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    maxZoom: 19,
    subdomains: 'abcd',
  }).addTo(mapInstance);

  loadGeofencesOnMap();
  updateVehicleMarkersOnMap();
}

async function loadGeofencesOnMap() {
  if (!mapInstance) return;

  try {
    const cercas = await api.getGeofences();
    geofenceLayers.forEach(l => mapInstance.removeLayer(l));
    geofenceLayers = [];

    cercas.forEach(c => {
      const isProibida = c.regras === 'PROIBIDA';
      const color = isProibida ? '#ef4444' : '#10b981';

      if (c.tipo === 'CIRCULO' && c.centro_lat && c.centro_lng) {
        const circle = L.circle([c.centro_lat, c.centro_lng], {
          color: color,
          fillColor: color,
          fillOpacity: 0.12,
          weight: 2,
          radius: c.raio_metros || 1000,
        }).addTo(mapInstance);

        circle.bindPopup(`
          <div style="font-family: Inter, sans-serif; min-width: 180px;">
            <strong style="color: ${color}; font-size: 13px;">${c.nome}</strong><br>
            <span style="font-size: 11px; color: #64748b;">Tipo: Cerca ${c.regras}</span><br>
            <span style="font-size: 11px;">Raio: <b>${c.raio_metros} m</b></span>
          </div>
        `);
        geofenceLayers.push(circle);
      }
    });
  } catch (err) {
    console.error('Erro ao carregar cercas no mapa:', err);
  }
}

async function updateVehicleMarkersOnMap() {
  if (!mapInstance) return;

  try {
    const posicoes = await api.getTelemetryLive();
    const bounds = [];

    posicoes.forEach(p => {
      const lat = p.latitude;
      const lng = p.longitude;
      if (!lat || !lng) return;

      bounds.push([lat, lng]);

      // Ícone e cores conforme status
      let iconColor = '#3b82f6'; // Azul = Estacionado
      let statusTexto = 'Estacionado';
      if (p.ignicao && p.velocidade_kmh > 5) {
        iconColor = '#10b981'; // Verde = Em Movimento
        statusTexto = `${p.velocidade_kmh} km/h`;
      } else if (p.ignicao) {
        iconColor = '#f59e0b'; // Amarelo = Ligado Parado
        statusTexto = 'Motor Ligado (0 km/h)';
      }

      const customIcon = L.divIcon({
        className: 'custom-fleet-pin',
        html: `
          <div style="
            background-color: ${iconColor};
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
          ">
            🚚
          </div>
          <div style="
            background: rgba(15,23,42,0.9);
            color: white;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            white-space: nowrap;
            margin-top: 2px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
          ">${p.veiculo_placa}</div>
        `,
        iconSize: [36, 50],
        iconAnchor: [18, 25],
      });

      if (vehicleMarkers[p.veiculo_placa]) {
        vehicleMarkers[p.veiculo_placa].setLatLng([lat, lng]);
        vehicleMarkers[p.veiculo_placa].setIcon(customIcon);
      } else {
        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(mapInstance);
        vehicleMarkers[p.veiculo_placa] = marker;

        marker.on('click', () => {
          showVehicleDetailsPopup(p);
        });
      }

      vehicleMarkers[p.veiculo_placa].bindPopup(`
        <div style="font-family: Inter, sans-serif; font-size: 12px; min-width: 200px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
            <b style="font-size: 14px; color: #1e293b;">${p.veiculo_placa}</b>
            <span style="background: ${iconColor}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">${statusTexto}</span>
          </div>
          <div style="color: #475569; font-size: 11px; margin-bottom: 4px;">Modelo: <b>${p.modelo}</b></div>
          <div style="color: #475569; font-size: 11px; margin-bottom: 4px;">Condutor: <b>${p.motorista_identificador || 'Não Identificado'}</b></div>
          <div style="color: #475569; font-size: 11px; margin-bottom: 8px;">RPM: <b>${p.rpm}</b> | Odômetro: <b>${p.odometro_km} km</b></div>
          <button onclick="drawVehicleRoute('${p.veiculo_placa}')" style="
            width: 100%;
            background: #2563eb;
            color: white;
            border: none;
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
          ">Traçar Histórico de Rota</button>
        </div>
      `);
    });

    if (bounds.length > 0 && !routePolyline) {
      mapInstance.fitBounds(bounds, { padding: [50, 50], maxZoom: 12 });
    }
  } catch (err) {
    console.error('Erro ao atualizar posições no mapa:', err);
  }
}

async function drawVehicleRoute(placa) {
  try {
    const pontos = await api.getTelemetryHistory(placa);
    if (!pontos || pontos.length === 0) {
      alert(`Nenhum histórico de rota recente encontrado para o veículo ${placa}.`);
      return;
    }

    if (routePolyline) {
      mapInstance.removeLayer(routePolyline);
    }

    const latlngs = pontos.map(pt => [pt.latitude, pt.longitude]);
    routePolyline = L.polyline(latlngs, {
      color: '#3b82f6',
      weight: 4,
      opacity: 0.85,
      dashArray: '8, 8',
    }).addTo(mapInstance);

    mapInstance.fitBounds(routePolyline.getBounds(), { padding: [40, 40] });
  } catch (err) {
    console.error('Erro ao traçar rota:', err);
  }
}

function showVehicleDetailsPopup(pos) {
  // Dispara evento ou preenche card lateral se desejado
  console.log('Veículo selecionado:', pos);
}
