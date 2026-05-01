'use client'

import dynamic from 'next/dynamic'
import { Navbar } from '@/components/navbar'
import { DashboardErrorState } from '@/components/dashboard-error-state'
import { DashboardHighlights } from '@/components/dashboard-highlights'
import { DashboardLoadingState } from '@/components/dashboard-loading-state'
import { DatasetSelector } from '@/components/dataset-selector'
import { KPICard } from '@/components/kpi-card'
import { useDashboardData } from '@/hooks/use-dashboard-data'

const CategoryDistributionChart = dynamic(
  () => import('@/components/category-distribution-chart').then((m) => m.default),
  { ssr: false }
)
const CustomerSegmentationPanel = dynamic(
  () => import('@/components/customer-segmentation-panel').then((m) => m.CustomerSegmentationPanel),
  { ssr: false }
)
const RevenueTrendChart = dynamic(
  () => import('@/components/revenue-trend-chart').then((m) => m.default),
  { ssr: false }
)
const TopProductsChart = dynamic(
  () => import('@/components/top-products-chart').then((m) => m.default),
  { ssr: false }
)
const TopProductsTable = dynamic(
  () => import('@/components/top-products-table').then((m) => m.TopProductsTable),
  { ssr: false }
)
const VisualizationGallery = dynamic(
  () => import('@/components/visualization-gallery').then((m) => m.VisualizationGallery),
  { ssr: false }
)
import {
  formatCompactCurrency,
  formatCurrency,
  formatNumber,
  formatPercent,
} from '@/lib/formatters'
import { Database, AlertCircle } from 'lucide-react'

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
          {/* Header Section */}
          <div className="mb-10 border-b border-white/10 pb-10">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="space-y-3">
                <span className="inline-flex rounded-full border border-purple-500/30 bg-purple-500/10 backdrop-blur px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-purple-300">
                  SalesSense AI
                </span>
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                    Retail Analytics Dashboard
                  </h1>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-400 sm:text-base">
                    Frontend-connected analytics experience powered by exported Python pipeline
                    outputs. Select a dataset to view detailed insights and metrics.
                  </p>
                </div>
              </div>

              {manifest && !error ? (
                <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur px-4 py-3 text-sm shadow-lg">
                  <p className="text-gray-300">
                    <span className="font-semibold text-white">{manifest.datasets.length}</span>{' '}
                    <span>dataset{manifest.datasets.length !== 1 ? 's' : ''}</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">loaded from exports</p>
                </div>
              ) : null}
            </div>
          </div>

          {/* Dataset Selector */}
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

          {/* Error State */}
          {error ? (
            <div className="mb-10 rounded-lg border border-red-500/20 bg-red-500/10 backdrop-blur p-5">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-red-300">Dashboard data unavailable</h3>
                  <p className="text-sm text-red-400/90 mt-1">{error}</p>
                  <p className="text-xs text-red-400/70 mt-2">
                    Run the Python pipeline or <code className="bg-red-500/20 px-1.5 py-0.5 rounded text-red-200 font-mono">python frontend_export.py</code> to refresh the frontend assets.
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {/* Loading State */}
          {!dataset && isLoading ? <DashboardLoadingState /> : null}

          {/* Empty State */}
          {!dataset && !error && !isLoading ? (
            <div className="mb-12 rounded-xl border border-white/10 bg-white/5 backdrop-blur py-16 text-center">
              <Database className="mx-auto h-12 w-12 text-purple-400/60 mb-4" />
              <h3 className="text-lg font-semibold text-white">No dataset selected</h3>
              <p className="mt-2 text-sm text-gray-400 max-w-sm mx-auto">
                Select a dataset from the dropdown above to view analytics, insights, and detailed performance metrics.
              </p>
            </div>
          ) : null}

          {/* Dashboard Content */}
          {dataset ? (
            <div className="space-y-10 transition-opacity duration-300 animate-in fade-in">
              {/* Overview Section */}
              <section>
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full" />
                    Overview
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

              {/* Analytics Section */}
              <section className="space-y-6 border-t border-white/10 pt-10">
                <div>
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span className="w-1 h-6 bg-gradient-to-b from-pink-500 to-blue-500 rounded-full" />
                    Analytics
                  </h2>
                </div>
                
                <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.6fr_1fr]">
                  <RevenueTrendChart data={dataset.revenueTrend} />
                  <DashboardHighlights dataset={dataset} />
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
                  <TopProductsChart data={dataset.topProducts} />
                  <CategoryDistributionChart data={dataset.categoryDistribution} />
                </div>
              </section>

              {/* Details Section */}
              <section className="space-y-6 border-t border-white/10 pt-10">
                <div>
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full" />
                    Details
                  </h2>
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.3fr_0.9fr]">
                  <TopProductsTable products={dataset.topProducts} />
                  <CustomerSegmentationPanel segments={dataset.customerSegmentation} />
                </div>
              </section>

              {/* Visualizations Gallery */}
              <section className="border-t border-white/10 pt-10">
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-blue-500 rounded-full" />
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
