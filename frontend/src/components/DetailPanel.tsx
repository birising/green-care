import React from 'react'
import { Bin, Green, Lamp, TelemetryRecord } from '../api/types'

type SelectedFeature =
  | { type: 'green'; feature: Green }
  | { type: 'lamp'; feature: Lamp }
  | { type: 'bin'; feature: Bin }
  | null

type DetailPanelProps = {
  selection: SelectedFeature
  telemetry?: TelemetryRecord[]
}

export const DetailPanel: React.FC<DetailPanelProps> = ({ selection, telemetry }) => {
  if (!selection) {
    return (
      <div className="section detail">
        <h2>Details</h2>
        <p>Select a feature on the map to see details.</p>
      </div>
    )
  }

  const { type, feature } = selection

  return (
    <div className="section detail">
      <h2>Details</h2>
      <p className="badge">{type.toUpperCase()}</p>
      <h3>{feature.name}</h3>
      {type === 'green' && (
        <ul>
          <li>Frequency (days): {feature.frequency_days ?? 'n/a'}</li>
          <li>Last mowed: {feature.last_mowed_at ?? 'n/a'}</li>
        </ul>
      )}
      {type === 'lamp' && <p>ID: {feature.id}</p>}
      {type === 'bin' && (
        <ul>
          <li>Last fill level: {feature.last_fill_level ?? 'n/a'}</li>
          <li>Last battery: {feature.last_battery_level ?? 'n/a'}</li>
          <li>Last temperature: {feature.last_temperature ?? 'n/a'}</li>
          <li>Updated at: {feature.updated_at ?? 'n/a'}</li>
        </ul>
      )}
      {type === 'bin' && telemetry && telemetry.length > 0 && (
        <div>
          <h4>Recent telemetry</h4>
          <ul>
            {telemetry.slice(0, 5).map((item) => (
              <li key={item.id}>
                {item.at_time}: {item.fill_level ?? 'n/a'}% full, battery {item.battery_level ?? 'n/a'}%, temp
                {item.temperature ?? 'n/a'}°C
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
