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
    <div className="rounded-2xl border border-border/70 bg-card/80 p-4 shadow-sm backdrop-blur-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm font-medium text-foreground/70">
            <Database className="h-4 w-4 text-primary" />
            Active dataset
          </div>
          <p className="text-sm text-foreground/60">
            Switch between exported dataset snapshots without needing a backend API.
          </p>
        </div>

        <div className="flex flex-col items-start gap-2 sm:flex-row sm:items-center">
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-foreground/60">
              <Spinner className="h-4 w-4 text-primary" />
              Loading dataset...
            </div>
          ) : null}

          <Select value={selectedDatasetId} onValueChange={onDatasetChange}>
            <SelectTrigger className="w-full min-w-[250px] bg-background/70 sm:w-[300px]">
              <SelectValue placeholder="Select a dataset" />
            </SelectTrigger>
            <SelectContent>
              {datasets.map((dataset) => (
                <SelectItem key={dataset.id} value={dataset.id}>
                  <div className="flex flex-col">
                    <span className="font-medium">{dataset.label}</span>
                    <span className="text-xs text-foreground/60">{dataset.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {activeDataset ? (
        <div className="mt-4 rounded-xl border border-dashed border-primary/20 bg-primary/5 px-4 py-3 text-sm text-foreground/70">
          <span className="font-semibold text-foreground">{activeDataset.label}</span>
          {' · '}
          {activeDataset.description}
        </div>
      ) : null}
    </div>
  )
}
