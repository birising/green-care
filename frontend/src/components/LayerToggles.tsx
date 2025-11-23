import React from 'react'

type LayerTogglesProps = {
  states: Record<string, boolean>
  onToggle: (layer: string) => void
}

const LABELS: Record<string, string> = {
  greens: 'Greens',
  lamps: 'Lamps',
  bins: 'Bins',
}

export const LayerToggles: React.FC<LayerTogglesProps> = ({ states, onToggle }) => {
  return (
    <div className="section">
      <h2>Layers</h2>
      {Object.entries(states).map(([key, value]) => (
        <label key={key} className="layer-checkbox">
          <input type="checkbox" checked={value} onChange={() => onToggle(key)} />
          <span>{LABELS[key] ?? key}</span>
        </label>
      ))}
    </div>
  )
}
