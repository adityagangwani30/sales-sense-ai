import type { DashboardDataset, DashboardManifest, RevenueTrendPoint, TopProduct, CustomerSegmentItem, CategoryDistributionItem, TopCustomer, VisualizationAsset, KPISet, DashboardHighlights } from '@/lib/dashboard-types'

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

export async function fetchDashboardDataset(datasetId: string, manifest: DashboardManifest): Promise<DashboardDataset> {
  const datasetConfig = manifest.datasets.find((item) => item.id === datasetId)
  const datasetPrefix = `/data/${datasetId}`

  const [metrics, revenueTrend, topProducts, customerSegmentation, categoryPerformance, repeatRate, insights] = await Promise.all([
    fetchJson<any>(`${datasetPrefix}/metrics.json`),
    fetchJson<RevenueTrendPoint[]>(`${datasetPrefix}/revenue_trend.json`),
    fetchJson<TopProduct[]>(`${datasetPrefix}/top_products.json`),
    fetchJson<CustomerSegmentItem[]>(`${datasetPrefix}/customer_segmentation.json`),
    fetchJson<CategoryDistributionItem[]>(`${datasetPrefix}/category_performance.json`),
    fetchJson<any>(`${datasetPrefix}/repeat_rate.json`),
    fetchJson<DashboardHighlights>(`${datasetPrefix}/insights.json`),
  ])

  const totalRevenue = Number(categoryPerformance?.reduce((s: number, it: any) => s + Number(it.total_revenue || 0), 0) || 0)

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
    visualizations: datasetConfig?.visualizations || (Array.isArray(insights) ? insights as unknown as VisualizationAsset[] : []),
    highlights: insights || { peakMonth: null, topProduct: null, largestCategory: null },
    priceSalesCorrelationAvailable: false,
  }

  return dataset
}
