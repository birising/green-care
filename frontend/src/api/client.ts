import axios from 'axios'
import { Bin, Green, Lamp, TelemetryRecord } from './types'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

const client = axios.create({
  baseURL: apiBase,
})

export const fetchGreens = async (): Promise<Green[]> => {
  const res = await client.get<Green[]>('/greens')
  return res.data
}

export const fetchLamps = async (): Promise<Lamp[]> => {
  const res = await client.get<Lamp[]>('/lamps')
  return res.data
}

export const fetchBins = async (): Promise<Bin[]> => {
  const res = await client.get<Bin[]>('/bins')
  return res.data
}

export const fetchBinTelemetry = async (binId: number, limit = 20): Promise<TelemetryRecord[]> => {
  const res = await client.get<TelemetryRecord[]>(`/bins/${binId}/telemetry`, {
    params: { limit },
  })
  return res.data
}
