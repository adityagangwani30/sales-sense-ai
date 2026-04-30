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
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                <Database className="h-5 w-5 text-purple-300" />
              </div>
              <h3 className="font-semibold text-white">Active Dataset</h3>
            </div>
            <p className="text-sm text-gray-400">
              Switch between exported dataset snapshots for different analytics views.
            </p>
          </div>
        </div>

        {/* Selector Row */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Select value={selectedDatasetId} onValueChange={onDatasetChange}>
            <SelectTrigger className="w-full sm:w-[280px] bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 text-white placeholder-gray-500 focus:border-purple-500/50 focus:ring-purple-500/20">
              <SelectValue placeholder="Select a dataset" />
            </SelectTrigger>
            <SelectContent className="bg-neutral-950 border-white/10">
              {datasets.map((dataset) => (
                <SelectItem key={dataset.id} value={dataset.id}>
                  <div className="flex flex-col">
                    <span className="font-medium text-white">{dataset.label}</span>
                    <span className="text-xs text-gray-400">{dataset.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-gray-400 px-1">
              <Spinner className="h-4 w-4 text-purple-400" />
              <span>Loading dataset...</span>
            </div>
          ) : null}
        </div>

        {/* Active Dataset Info */}
        {activeDataset ? (
          <div className="rounded-lg border border-purple-500/30 bg-purple-500/10 backdrop-blur px-4 py-3">
            <p className="text-sm text-gray-300">
              <span className="font-semibold text-purple-300">{activeDataset.label}</span>
              <span className="text-gray-400"> · {activeDataset.description}</span>
            </p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
