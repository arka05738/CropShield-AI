import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Filter, Layers, TrendingUp, ShieldAlert } from 'lucide-react';
import type { HotspotGeoJSON, HotspotFeature } from '../../types';
import { EmptyState } from '../ui/States';

interface AdminGisMapProps {
  hotspots: HotspotGeoJSON | null;
  onFilterChange: (filters: {
    crop?: string;
    disease?: string;
    state?: string;
    min_risk?: string;
  }) => void;
  dataSource?: string | null;
}

const MapFlyTo: React.FC<{ coords: [number, number] }> = ({ coords }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(coords, 7, { duration: 1.2 });
  }, [coords, map]);
  return null;
};

export const AdminGisMap: React.FC<AdminGisMapProps> = ({
  hotspots,
  onFilterChange,
  dataSource,
}) => {
  const [selectedHotspot, setSelectedHotspot] = useState<HotspotFeature | null>(null);
  const [cropFilter, setCropFilter] = useState('all');
  const [stateFilter, setStateFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');
  const [activeLayers, setActiveLayers] = useState({
    heatmaps: true,
    clusters: true,
  });

  const features = hotspots?.features || [];

  useEffect(() => {
    if (features.length > 0 && !selectedHotspot) {
      setSelectedHotspot(features[0]);
    }
    if (features.length === 0) {
      setSelectedHotspot(null);
    }
  }, [features, selectedHotspot]);

  const handleFilterUpdate = (key: string, value: string) => {
    if (key === 'crop') setCropFilter(value);
    if (key === 'state') setStateFilter(value);
    if (key === 'risk') setRiskFilter(value);

    onFilterChange({
      crop: key === 'crop' ? value : cropFilter,
      state: key === 'state' ? value : stateFilter,
      min_risk: key === 'risk' ? value : riskFilter,
    });
  };

  const getMarkerColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical':
        return '#b91c1c';
      case 'high risk':
      case 'high':
        return '#c2410c';
      case 'moderate risk':
      case 'moderate':
        return '#a16207';
      default:
        return '#166534';
    }
  };

  const cropOptions = Array.from(new Set(features.map((f) => f.properties.crop).filter(Boolean))).sort();
  const stateOptions = Array.from(new Set(features.map((f) => f.properties.state).filter(Boolean))).sort();

  return (
    <div className="relative flex h-[calc(100vh-120px)] min-h-[520px] w-full flex-col overflow-hidden rounded-xl border border-stone-200 bg-white lg:flex-row">
      <div className="z-20 w-full shrink-0 space-y-4 overflow-y-auto border-r border-stone-200 bg-stone-50 p-4 lg:w-72">
        <div className="flex items-center gap-2 border-b border-stone-200 pb-3">
          <Filter className="h-4 w-4 text-green-800" />
          <h3 className="text-sm font-semibold text-stone-900">Spatial filters</h3>
        </div>

        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-stone-500">Crop</label>
          <select
            value={cropFilter}
            onChange={(e) => handleFilterUpdate('crop', e.target.value)}
            className="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs text-stone-800"
          >
            <option value="all">All crops</option>
            {cropOptions.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-stone-500">State</label>
          <select
            value={stateFilter}
            onChange={(e) => handleFilterUpdate('state', e.target.value)}
            className="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs text-stone-800"
          >
            <option value="all">All states</option>
            {stateOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-stone-500">Severity</label>
          <select
            value={riskFilter}
            onChange={(e) => handleFilterUpdate('risk', e.target.value)}
            className="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs text-stone-800"
          >
            <option value="all">All severities</option>
            <option value="Critical">Critical</option>
            <option value="High Risk">High Risk</option>
            <option value="Moderate Risk">Moderate Risk</option>
          </select>
        </div>

        <div className="space-y-2 border-t border-stone-200 pt-3">
          <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-stone-600">
            <Layers className="h-3.5 w-3.5 text-green-800" />
            Map layers
          </div>
          <label className="flex cursor-pointer items-center justify-between rounded p-1.5 text-xs text-stone-700 hover:bg-white">
            <span>Intensity rings</span>
            <input
              type="checkbox"
              checked={activeLayers.heatmaps}
              onChange={() => setActiveLayers((p) => ({ ...p, heatmaps: !p.heatmaps }))}
              className="accent-green-800"
            />
          </label>
          <label className="flex cursor-pointer items-center justify-between rounded p-1.5 text-xs text-stone-700 hover:bg-white">
            <span>Outbreak points</span>
            <input
              type="checkbox"
              checked={activeLayers.clusters}
              onChange={() => setActiveLayers((p) => ({ ...p, clusters: !p.clusters }))}
              className="accent-green-800"
            />
          </label>
        </div>

        <div className="space-y-2 border-t border-stone-200 pt-3">
          <span className="text-[11px] font-semibold uppercase text-stone-500">
            Epicenters ({features.length})
          </span>
          {features.length === 0 ? (
            <p className="text-xs text-stone-400">No hotspot features from API.</p>
          ) : (
            <div className="max-h-48 space-y-1.5 overflow-y-auto">
              {features.map((f) => (
                <button
                  key={f.properties.id}
                  type="button"
                  onClick={() => setSelectedHotspot(f)}
                  className={`w-full rounded-lg border p-2 text-left text-xs transition-all ${
                    selectedHotspot?.properties.id === f.properties.id
                      ? 'border-green-700 bg-green-50 text-stone-900'
                      : 'border-stone-200 bg-white text-stone-600 hover:border-stone-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-stone-800">{f.properties.district}</span>
                    <span className="text-[10px] font-bold text-amber-800">
                      {f.properties.case_count} cases
                    </span>
                  </div>
                  <p className="mt-0.5 truncate text-[11px] text-stone-500">
                    {f.properties.crop} • {f.properties.disease}
                  </p>
                </button>
              ))}
            </div>
          )}
          {dataSource ? (
            <p className="text-[10px] uppercase tracking-wide text-stone-400">data_source: {dataSource}</p>
          ) : null}
        </div>
      </div>

      <div className="relative h-full min-h-[400px] flex-1">
        {features.length === 0 ? (
          <div className="absolute inset-0 z-[400] flex items-center justify-center bg-stone-100/80">
            <EmptyState
              title="No hotspot geometry"
              detail="Hotspots appear when analyses with locations are available from the API."
            />
          </div>
        ) : null}

        <MapContainer
          center={[22.5, 78.5]}
          zoom={5}
          scrollWheelZoom
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {selectedHotspot ? (
            <MapFlyTo
              coords={[
                selectedHotspot.geometry.coordinates[1],
                selectedHotspot.geometry.coordinates[0],
              ]}
            />
          ) : null}

          {features.map((feature) => {
            const [lng, lat] = feature.geometry.coordinates;
            const props = feature.properties;
            const color = getMarkerColor(props.risk_level);
            const isSelected = selectedHotspot?.properties.id === props.id;

            return (
              <React.Fragment key={props.id}>
                {activeLayers.heatmaps ? (
                  <CircleMarker
                    center={[lat, lng]}
                    radius={20 + props.intensity * 25}
                    pathOptions={{
                      color,
                      fillColor: color,
                      fillOpacity: 0.15,
                      weight: 1,
                      dashArray: '4, 4',
                    }}
                  />
                ) : null}
                {activeLayers.clusters ? (
                  <CircleMarker
                    center={[lat, lng]}
                    radius={isSelected ? 10 : 7}
                    eventHandlers={{ click: () => setSelectedHotspot(feature) }}
                    pathOptions={{
                      color: '#ffffff',
                      fillColor: color,
                      fillOpacity: 0.95,
                      weight: isSelected ? 3 : 1.5,
                    }}
                  >
                    <Popup>
                      <div className="space-y-1 p-1 text-xs text-stone-800">
                        <p className="text-sm font-bold text-green-900">
                          {props.district}, {props.state}
                        </p>
                        <p><strong>Crop:</strong> {props.crop}</p>
                        <p><strong>Disease:</strong> {props.disease}</p>
                        <p>
                          <strong>Cases:</strong> {props.case_count} in {props.farm_count} farms
                        </p>
                        <p>
                          <strong>Trend:</strong>{' '}
                          {props.trend_pct > 0 ? `+${props.trend_pct}%` : `${props.trend_pct}%`}
                        </p>
                      </div>
                    </Popup>
                  </CircleMarker>
                ) : null}
              </React.Fragment>
            );
          })}
        </MapContainer>
      </div>

      {selectedHotspot ? (
        <div className="z-20 w-full shrink-0 space-y-5 overflow-y-auto border-l border-stone-200 bg-white p-5 lg:w-80">
          <div className="border-b border-stone-200 pb-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-green-800">
              District dossier
            </span>
            <h2 className="mt-0.5 text-xl font-semibold text-stone-900">
              {selectedHotspot.properties.district}
            </h2>
            <p className="text-xs text-stone-500">{selectedHotspot.properties.state}</p>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3">
              <span className="text-[10px] text-stone-500">Risk</span>
              <p className="mt-1 text-xs font-bold text-amber-800">
                {selectedHotspot.properties.risk_level}
              </p>
            </div>
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3">
              <span className="text-[10px] text-stone-500">Trend %</span>
              <p className="mt-1 flex items-center gap-1 text-xs font-bold text-orange-800">
                <TrendingUp className="h-3.5 w-3.5" />
                {selectedHotspot.properties.trend_pct > 0
                  ? `+${selectedHotspot.properties.trend_pct}%`
                  : `${selectedHotspot.properties.trend_pct}%`}
              </p>
            </div>
          </div>

          <div className="space-y-2 rounded-xl border border-stone-200 bg-stone-50 p-4">
            <span className="text-[10px] font-semibold uppercase text-stone-500">Profile</span>
            <div>
              <p className="text-xs text-stone-500">Crop</p>
              <p className="text-sm font-bold text-green-900">{selectedHotspot.properties.crop}</p>
            </div>
            <div>
              <p className="text-xs text-stone-500">Disease</p>
              <p className="text-sm font-bold text-stone-900">{selectedHotspot.properties.disease}</p>
            </div>
            {selectedHotspot.properties.pest ? (
              <div>
                <p className="text-xs text-stone-500">Pest</p>
                <p className="text-sm font-bold text-stone-800">{selectedHotspot.properties.pest}</p>
              </div>
            ) : null}
          </div>

          <div className="grid grid-cols-2 gap-2.5 text-xs">
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3">
              <span className="block text-[10px] text-stone-500">Cases</span>
              <span className="text-lg font-bold text-stone-900">
                {selectedHotspot.properties.case_count}
              </span>
            </div>
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3">
              <span className="block text-[10px] text-stone-500">Farms</span>
              <span className="text-lg font-bold text-stone-900">
                {selectedHotspot.properties.farm_count}
              </span>
            </div>
          </div>

          <div className="space-y-1.5 rounded-xl border border-green-200 bg-green-50 p-3.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-green-900">
              <ShieldAlert className="h-3.5 w-3.5" />
              Extension note
            </div>
            <p className="text-[11px] leading-relaxed text-stone-700">
              Coordinate with block agriculture officers in {selectedHotspot.properties.district} for
              field verification and prophylactic measures based on confirmed cases.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};
