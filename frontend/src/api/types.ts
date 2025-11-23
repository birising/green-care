export type Geometry = {
  type: string
  coordinates: any
}

export interface Green {
  id: number
  name: string
  polygon: Geometry | null
  frequency_days?: number | null
  last_mowed_at?: string | null
}

export interface Lamp {
  id: number
  name: string
  point: Geometry | null
}

export interface Bin {
  id: number
  name: string
  point: Geometry | null
  last_fill_level?: number | null
  last_battery_level?: number | null
  last_temperature?: number | null
  updated_at?: string | null
}

export interface TelemetryRecord {
  id: number
  bin_id: number
  fill_level: number | null
  battery_level: number | null
  temperature: number | null
  at_time: string
}
