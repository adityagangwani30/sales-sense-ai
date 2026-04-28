export interface DatasetOption {
  id: string
  label: string
  description: string
  dataPath: string
}

export interface VisualizationAsset {
  title: string
  src: string
  filename: string
}

export interface SqlAnalysisMap {
  [key: string]: string
}

export interface DashboardManifest {
  defaultDatasetId: string
  datasets: DatasetOption[]
  sqlAnalysis: SqlAnalysisMap
  visualizations: VisualizationAsset[]
}

export interface KPISet {
  totalRevenue: number
  totalOrders: number
  totalCustomers: number
  averageOrderValue: number
  repeatPurchaseRate: number
  trendChangePct: number
}

export interface RevenueTrendPoint {
  month: string
  month_start: string
  revenue: number
}

export interface TopProduct {
  product_name: string
  total_revenue: number
  order_count: number
}

export interface CategoryDistributionItem {
  category: string
  total_revenue: number
  share_pct: number
}

export interface CustomerSegmentItem {
  segment: string
  customer_count: number
  avg_order_value: number
}

export interface TopCustomer {
  customer_name: string
  total_spent: number
}

export interface DashboardHighlights {
  peakMonth: string | null
  topProduct: string | null
  largestCategory: string | null
}

export interface DashboardDataset {
  datasetId: string
  label: string
  description: string
  sourceFile: string
  kpis: KPISet
  revenueTrend: RevenueTrendPoint[]
  topProducts: TopProduct[]
  categoryDistribution: CategoryDistributionItem[]
  customerSegmentation: CustomerSegmentItem[]
  topCustomers: TopCustomer[]
  visualizations: VisualizationAsset[]
  highlights: DashboardHighlights
  priceSalesCorrelationAvailable: boolean
}
