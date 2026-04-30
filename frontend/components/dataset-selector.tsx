'use client'

import { Database } from 'lucide-react'

import type { DatasetOption } from '@/lib/dashboard-types'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Spinner } from '@/components/ui/spinner'

interface DatasetSelectorProps {
  datasets: DatasetOption[]
  selectedDatasetId: string
  onDatasetChange: (datasetId: string) => void
  isLoading?: boolean
}

export function DatasetSelector({
  datasets,
  selectedDatasetId,
  onDatasetChange,
  isLoading = false,
}: DatasetSelectorProps) {
  const activeDataset = datasets.find((dataset) => dataset.id === selectedDatasetId)

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <Database className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground">Active Dataset</h3>
            </div>
            <p className="text-sm text-foreground/60">
              Switch between exported dataset snapshots for different analytics views.
            </p>
          </div>
        </div>

        {/* Selector Row */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Select value={selectedDatasetId} onValueChange={onDatasetChange}>
            <SelectTrigger className="w-full sm:w-[280px] bg-background hover:bg-background/80">
              <SelectValue placeholder="Select a dataset" />
            </SelectTrigger>
            <SelectContent>
              {datasets.map((dataset) => (
                <SelectItem key={dataset.id} value={dataset.id}>
                  <div className="flex flex-col">
                    <span className="font-medium text-foreground">{dataset.label}</span>
                    <span className="text-xs text-foreground/50">{dataset.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-foreground/60 px-1">
              <Spinner className="h-4 w-4 text-primary" />
              <span>Loading dataset...</span>
            </div>
          ) : null}
        </div>

        {/* Active Dataset Info */}
        {activeDataset ? (
          <div className="rounded-lg border border-primary/20 bg-primary/5 px-4 py-3">
            <p className="text-sm text-foreground/70">
              <span className="font-semibold text-primary">{activeDataset.label}</span>
              <span className="text-foreground/60"> · {activeDataset.description}</span>
            </p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
