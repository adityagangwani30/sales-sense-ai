import type { DashboardDataset, DashboardManifest } from '@/lib/dashboard-types'

const MANIFEST_PATH = '/data/dataset-manifest.json'

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`)
  }
  return (await response.json()) as T
}

export function fetchDashboardManifest() {
  return fetchJson<DashboardManifest>(MANIFEST_PATH)
}

export function fetchDashboardDataset(path: string) {
  return fetchJson<DashboardDataset>(path)
}
