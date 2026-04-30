'use client'

import { useEffect, useState } from 'react'

import { fetchDashboardDataset, fetchDashboardManifest } from '@/lib/dashboard-data'
import type { DashboardDataset, DashboardManifest } from '@/lib/dashboard-types'

interface UseDashboardDataResult {
  manifest: DashboardManifest | null
  dataset: DashboardDataset | null
  selectedDatasetId: string
  setSelectedDatasetId: (datasetId: string) => void
  isLoading: boolean
  error: string | null
}

export function useDashboardData(): UseDashboardDataResult {
  const [manifest, setManifest] = useState<DashboardManifest | null>(null)
  const [dataset, setDataset] = useState<DashboardDataset | null>(null)
  const [selectedDatasetId, setSelectedDatasetId] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    async function loadManifest() {
      setIsLoading(true)
      setError(null)

      try {
        const loadedManifest = await fetchDashboardManifest()
        if (!isMounted) {
          return
        }

        setManifest(loadedManifest)
        setSelectedDatasetId(loadedManifest.defaultDatasetId)
      } catch (loadError) {
        if (!isMounted) {
          return
        }
        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Unable to load dashboard assets.',
        )
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadManifest()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    if (!manifest || !selectedDatasetId) {
      return
    }

    const selectedDataset = manifest.datasets.find((item) => item.id === selectedDatasetId)
    if (!selectedDataset) {
      return
    }

    let isMounted = true
    setIsLoading(true)
    setError(null)

    fetchDashboardDataset(selectedDataset.id, manifest)
      .then((loadedDataset) => {
        if (isMounted) {
          setDataset(loadedDataset)
        }
      })
      .catch((loadError) => {
        if (!isMounted) {
          return
        }
        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Unable to switch dashboard datasets.',
        )
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [manifest, selectedDatasetId])

  return {
    manifest,
    dataset,
    selectedDatasetId,
    setSelectedDatasetId,
    isLoading,
    error,
  }
}
