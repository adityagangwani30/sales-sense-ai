'use client'

import dynamic from 'next/dynamic'
import { AlertCircle, Database } from 'lucide-react'

import { Navbar } from '@/components/navbar'
import { DashboardLoadingState } from '@/components/dashboard-loading-state'
import { DatasetSelector } from '@/components/dataset-selector'
import { KPICard } from '@/components/kpi-card'
import { VisualizationGallery } from '@/components/visualization-gallery'
import { useDashboardData } from '@/hooks/use-dashboard-data'
import { formatCompactCurrency, formatCurrency, formatNumber, formatPercent } from '@/lib/formatters'

const DashboardDeepAnalytics = dynamic(
  () => import('@/components/dashboard-deep-analytics').then((m) => m.default),
  { ssr: false },
)

export default function DashboardPage() {
  const {
    manifest,
    dataset,
    selectedDatasetId,
    setSelectedDatasetId,
    isLoading,
    error,
  } = useDashboardData()

  return (
    <>
      <Navbar />

      <main className="mx-auto max-w-7xl px-6 py-8 sm:px-6 lg:px-8">
        <div className="mb-10 border-b border-white/10 pb-10">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-3">
              <span className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-500/10 backdrop-blur px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">
                SalesSense AI
              </span>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                  Complete Analytics Dashboard
                </h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-400 sm:text-base">
                  Unified view across dataset overview, SQL analytics, ML performance,
                  predictions, feature importance, business insights, error analysis, and ROI impact.
                </p>
              </div>
            </div>

            {manifest && !error ? (
              <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur px-4 py-3 text-sm shadow-lg">
                <p className="text-gray-300">
                  <span className="font-semibold text-white">{manifest.datasets.length}</span>{' '}
                  <span>dataset{manifest.datasets.length !== 1 ? 's' : ''}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">loaded from static exports</p>
              </div>
            ) : null}
          </div>
        </div>

        {manifest ? (
          <div className="mb-10">
            <DatasetSelector
              datasets={manifest.datasets}
              selectedDatasetId={selectedDatasetId}
              onDatasetChange={setSelectedDatasetId}
              isLoading={isLoading}
            />
          </div>
        ) : null}

        {error ? (
          <div className="mb-10 rounded-lg border border-red-500/20 bg-red-500/10 backdrop-blur p-5">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-red-300">Dashboard data unavailable</h3>
                <p className="text-sm text-red-400/90 mt-1">{error}</p>
                <p className="text-xs text-red-400/70 mt-2">
                  Run the Python pipeline or{' '}
                  <code className="bg-red-500/20 px-1.5 py-0.5 rounded text-red-200 font-mono">
                    python frontend_export.py
                  </code>{' '}
                  to refresh the frontend assets.
                </p>
              </div>
            </div>
          </div>
        ) : null}

        {!dataset && isLoading ? <DashboardLoadingState /> : null}

        {!dataset && !error && !isLoading ? (
          <div className="mb-12 rounded-xl border border-white/10 bg-white/5 backdrop-blur py-16 text-center">
            <Database className="mx-auto h-12 w-12 text-cyan-300/70 mb-4" />
            <h3 className="text-lg font-semibold text-white">No dataset selected</h3>
            <p className="mt-2 text-sm text-gray-400 max-w-sm mx-auto">
              Select a dataset to view analytics
            </p>
          </div>
        ) : null}

        {dataset ? (
          <div className="space-y-10 transition-opacity duration-300 animate-in fade-in">
            <section>
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <span className="w-1 h-6 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full" />
                  Dataset Overview
                </h2>
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                <KPICard
                  title="Total Revenue"
                  value={formatCompactCurrency(dataset.kpis.totalRevenue)}
                  change={formatPercent(dataset.kpis.trendChangePct)}
                  isPositive={dataset.kpis.trendChangePct >= 0}
                  icon="revenue"
                />
                <KPICard
                  title="Total Orders"
                  value={formatNumber(dataset.kpis.totalOrders)}
                  change="Dataset snapshot"
                  isPositive
                  icon="transactions"
                  showChangeIcon={false}
                />
                <KPICard
                  title="Total Customers"
                  value={formatNumber(dataset.kpis.totalCustomers)}
                  change={dataset.label}
                  isPositive
                  icon="growth"
                  showChangeIcon={false}
                />
                <KPICard
                  title="Avg Order Value"
                  value={formatCurrency(dataset.kpis.averageOrderValue)}
                  change={`${dataset.kpis.repeatPurchaseRate.toFixed(1)}% repeat`}
                  isPositive={dataset.kpis.repeatPurchaseRate >= 0}
                  icon="aov"
                  showChangeIcon={false}
                />
              </div>
            </section>

            <DashboardDeepAnalytics datasetId={selectedDatasetId} dataset={dataset} />

            <section className="border-t border-white/10 pt-10">
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <span className="w-1 h-6 bg-gradient-to-b from-blue-500 to-indigo-500 rounded-full" />
                  Visualizations
                </h2>
              </div>
              <VisualizationGallery visualizations={dataset.visualizations} />
            </section>
          </div>
        ) : null}
      </main>
    </>
  )
}
