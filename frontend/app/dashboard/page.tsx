'use client'

import { Navbar } from '@/components/navbar'
import { CategoryDistributionChart } from '@/components/category-distribution-chart'
import { CustomerSegmentationPanel } from '@/components/customer-segmentation-panel'
import { DashboardErrorState } from '@/components/dashboard-error-state'
import { DashboardHighlights } from '@/components/dashboard-highlights'
import { DashboardLoadingState } from '@/components/dashboard-loading-state'
import { DatasetSelector } from '@/components/dataset-selector'
import { KPICard } from '@/components/kpi-card'
import { RevenueTrendChart } from '@/components/revenue-trend-chart'
import { TopProductsChart } from '@/components/top-products-chart'
import { TopProductsTable } from '@/components/top-products-table'
import { VisualizationGallery } from '@/components/visualization-gallery'
import { useDashboardData } from '@/hooks/use-dashboard-data'
import {
  formatCompactCurrency,
  formatCurrency,
  formatNumber,
  formatPercent,
} from '@/lib/formatters'

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
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(46,134,171,0.14),_transparent_35%),linear-gradient(180deg,_rgba(255,255,255,1)_0%,_rgba(247,250,252,1)_100%)]">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <span className="inline-flex rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              SalesSense AI
            </span>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Retail Analytics Dashboard
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-foreground/65 sm:text-base">
                Frontend-connected analytics experience powered by exported Python pipeline
                outputs. No backend yet, but the structure is ready for one.
              </p>
            </div>
          </div>

          {manifest ? (
            <div className="rounded-2xl border border-border/70 bg-card/90 px-4 py-3 text-sm text-foreground/65 shadow-sm">
              <span className="font-semibold text-foreground">{manifest.datasets.length}</span>{' '}
              dataset snapshots loaded from <code>/public/data</code>
            </div>
          ) : null}
        </div>

        {manifest ? (
          <div className="mb-8">
            <DatasetSelector
              datasets={manifest.datasets}
              selectedDatasetId={selectedDatasetId}
              onDatasetChange={setSelectedDatasetId}
              isLoading={isLoading}
            />
          </div>
        ) : null}

        {error ? <DashboardErrorState message={error} /> : null}

        {!dataset && isLoading ? <DashboardLoadingState /> : null}

        {dataset ? (
          <div className="space-y-8 transition-opacity duration-300">
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

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.6fr_1fr]">
              <RevenueTrendChart data={dataset.revenueTrend} />
              <DashboardHighlights dataset={dataset} />
            </div>

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              <TopProductsChart data={dataset.topProducts} />
              <CategoryDistributionChart data={dataset.categoryDistribution} />
            </div>

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.3fr_0.9fr]">
              <TopProductsTable products={dataset.topProducts} />
              <CustomerSegmentationPanel segments={dataset.customerSegmentation} />
            </div>

            <VisualizationGallery visualizations={dataset.visualizations} />
          </div>
        ) : null}
      </main>
    </div>
  )
}
