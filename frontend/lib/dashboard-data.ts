import type { DashboardDataset, DashboardManifest, RevenueTrendPoint, TopProduct, CustomerSegmentItem, CategoryDistributionItem, TopCustomer, KPISet, DashboardHighlights } from '@/lib/dashboard-types'

const MANIFEST_PATH = '/data/dataset-manifest.json'

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`)
  }
  return (await response.json()) as T
}

async function fetchJsonOrNull<T>(path: string): Promise<T | null> {
  try {
    return await fetchJson<T>(path)
  } catch {
    return null
  }
}

export function fetchDashboardManifest() {
  return fetchJson<DashboardManifest>(MANIFEST_PATH)
}

export async function fetchDashboardDataset(datasetId: string, manifest: DashboardManifest): Promise<DashboardDataset> {
  const datasetConfig = manifest.datasets.find((item) => item.id === datasetId)
  const datasetPrefix = `/data/${datasetId}`
  const datasetVisualizations = manifest.visualizations.filter((asset) =>
    asset.src.includes(`/${datasetId}/`),
  )

  const [metrics, revenueTrend, topProducts, customerSegmentation, categoryPerformance, repeatRate, insights] = await Promise.all([
    fetchJsonOrNull<any>(`${datasetPrefix}/metrics.json`),
    fetchJsonOrNull<RevenueTrendPoint[]>(`${datasetPrefix}/revenue_trend.json`),
    fetchJsonOrNull<TopProduct[]>(`${datasetPrefix}/top_products.json`),
    fetchJsonOrNull<CustomerSegmentItem[]>(`${datasetPrefix}/customer_segmentation.json`),
    fetchJsonOrNull<CategoryDistributionItem[]>(`${datasetPrefix}/category_performance.json`),
    fetchJsonOrNull<any>(`${datasetPrefix}/repeat_rate.json`),
    fetchJsonOrNull<DashboardHighlights>(`${datasetPrefix}/insights.json`),
  ])

  const kpis: KPISet = {
    totalRevenue: Number(metrics?.total_revenue || metrics?.totalRevenue || 0),
    totalOrders: Number(metrics?.total_orders || metrics?.totalOrders || 0),
    totalCustomers: Number(metrics?.total_customers || metrics?.totalCustomers || 0),
    averageOrderValue: Number(metrics?.avg_order_value || metrics?.averageOrderValue || 0),
    repeatPurchaseRate: Number(repeatRate?.repeat_purchase_rate || metrics?.repeat_purchase_rate || 0),
    trendChangePct: Number(metrics?.trend_change_pct || 0),
  }

  const dataset: DashboardDataset = {
    datasetId,
    label: datasetConfig?.label || datasetId,
    description: datasetConfig?.description || '',
    sourceFile: datasetConfig?.dataPath || `${datasetPrefix}/metrics.json`,
    kpis,
    revenueTrend: revenueTrend || [],
    topProducts: topProducts || [],
    categoryDistribution: categoryPerformance || [],
    customerSegmentation: customerSegmentation || [],
    topCustomers: [],
    visualizations: datasetConfig?.visualizations || datasetVisualizations,
    highlights: insights || { peakMonth: null, topProduct: null, largestCategory: null },
    priceSalesCorrelationAvailable: false,
  }

  return dataset
}
