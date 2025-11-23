import React, { useMemo } from 'react'
import { MapContainer, TileLayer, Polygon, CircleMarker, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import { Bin, Green, Lamp } from '../api/types'

export type SelectedFeature =
  | { type: 'green'; feature: Green }
  | { type: 'lamp'; feature: Lamp }
  | { type: 'bin'; feature: Bin }
  | null

type MapViewProps = {
  greens: Green[]
  lamps: Lamp[]
  bins: Bin[]
  showGreens: boolean
  showLamps: boolean
  showBins: boolean
  onSelect: (sel: SelectedFeature) => void
}

const center: [number, number] = [50.0755, 14.4378]

const binFillColor = (fillLevel?: number | null): string => {
  if (fillLevel == null) return '#6b7280'
  if (fillLevel >= 80) return '#ef4444'
  if (fillLevel >= 50) return '#f59e0b'
  return '#22c55e'
}

const swapLatLng = (coords: any): any => {
  if (typeof coords[0] === 'number' && typeof coords[1] === 'number') {
    return [coords[1], coords[0]]
  }
  if (Array.isArray(coords)) {
    return coords.map((c) => swapLatLng(c))
  }
  return coords
}

export const MapView: React.FC<MapViewProps> = ({
  greens,
  lamps,
  bins,
  showGreens,
  showLamps,
  showBins,
  onSelect,
}) => {
  const greensShapes = useMemo(
    () =>
      greens
        .filter((g) => g.polygon)
        .map((g) => ({
          ...g,
          coords: swapLatLng(g.polygon?.coordinates),
        })),
    [greens]
  )

  const lampPoints = useMemo(
    () =>
      lamps
        .filter((l) => l.point)
        .map((l) => ({
          ...l,
          coords: swapLatLng(l.point?.coordinates) as [number, number],
        })),
    [lamps]
  )

  const binPoints = useMemo(
    () =>
      bins
        .filter((b) => b.point)
        .map((b) => ({
          ...b,
          coords: swapLatLng(b.point?.coordinates) as [number, number],
        })),
    [bins]
  )

  return (
    <MapContainer center={center} zoom={13} className="map-container">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />

      {showGreens &&
        greensShapes.map((g) => (
          <Polygon
            key={g.id}
            positions={g.coords as L.LatLngExpression[][]}
            pathOptions={{ color: '#16a34a', weight: 2, fillOpacity: 0.35 }}
            eventHandlers={{ click: () => onSelect({ type: 'green', feature: g as Green }) }}
          >
            <Tooltip>{g.name}</Tooltip>
          </Polygon>
        ))}

      {showLamps &&
        lampPoints.map((lamp) => (
          <CircleMarker
            key={lamp.id}
            center={lamp.coords}
            pathOptions={{ color: '#2563eb', fillColor: '#1d4ed8', fillOpacity: 0.9 }}
            radius={6}
            eventHandlers={{ click: () => onSelect({ type: 'lamp', feature: lamp }) }}
          >
            <Tooltip>{lamp.name}</Tooltip>
          </CircleMarker>
        ))}

      {showBins &&
        binPoints.map((bin) => (
          <CircleMarker
            key={bin.id}
            center={bin.coords}
            pathOptions={{ color: binFillColor(bin.last_fill_level), fillColor: binFillColor(bin.last_fill_level), fillOpacity: 0.9 }}
            radius={7}
            eventHandlers={{ click: () => onSelect({ type: 'bin', feature: bin }) }}
          >
            <Tooltip>
              {bin.name}
              <br />
              Fill: {bin.last_fill_level ?? 'n/a'}%
            </Tooltip>
          </CircleMarker>
        ))}
    </MapContainer>
  )
}
