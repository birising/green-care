import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchBins, fetchBinTelemetry, fetchGreens, fetchLamps } from './api/client'
import { Bin, Green, Lamp, TelemetryRecord } from './api/types'
import { LayerToggles } from './components/LayerToggles'
import { DetailPanel } from './components/DetailPanel'
import { MapView, SelectedFeature } from './map/MapView'

function App() {
  const [layers, setLayers] = useState({ greens: true, lamps: true, bins: true })
  const [selection, setSelection] = useState<SelectedFeature>(null)

  const { data: greens = [] } = useQuery({ queryKey: ['greens'], queryFn: fetchGreens })
  const { data: lamps = [] } = useQuery({ queryKey: ['lamps'], queryFn: fetchLamps })
  const { data: bins = [] } = useQuery({ queryKey: ['bins'], queryFn: fetchBins })

  const selectedBinId = selection?.type === 'bin' ? selection.feature.id : null
  const { data: telemetry } = useQuery<TelemetryRecord[]>({
    queryKey: ['bin-telemetry', selectedBinId],
    queryFn: () => fetchBinTelemetry(selectedBinId!),
    enabled: selectedBinId !== null,
  })

  const layerStates = useMemo(() => layers, [layers])

  const handleToggle = (layer: string) => {
    setLayers((prev) => ({ ...prev, [layer]: !prev[layer as keyof typeof prev] }))
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Green Care Map</h1>
        <LayerToggles states={layerStates} onToggle={handleToggle} />
        <div className="section">
          <h3>Legend</h3>
          <div className="legend">
            <span className="swatch" style={{ background: '#16a34a' }}></span>
            <span>Greens</span>
          </div>
          <div className="legend">
            <span className="swatch" style={{ background: '#2563eb' }}></span>
            <span>Lamps</span>
          </div>
          <div className="legend">
            <span className="swatch" style={{ background: '#22c55e' }}></span>
            <span>Bins (by fill level)</span>
          </div>
        </div>
        <DetailPanel selection={selection} telemetry={telemetry} />
      </aside>
      <div className="map-wrapper">
        <MapView
          greens={greens as Green[]}
          lamps={lamps as Lamp[]}
          bins={bins as Bin[]}
          showGreens={layers.greens}
          showLamps={layers.lamps}
          showBins={layers.bins}
          onSelect={(sel) => setSelection(sel)}
        />
      </div>
    </div>
  )
}

export default App
