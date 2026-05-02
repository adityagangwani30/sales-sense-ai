export interface DatasetOption {
  id: string
  label: string
  description: string
  dataPath: string
  visualizations?: VisualizationAsset[]
}

export interface VisualizationAsset {
  title: string
  src: string
  filename: string
}

export type SqlAnalysisMap = Record<string, Record<string, string>>

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
  monthly_revenue?: number
  year?: number
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
  product_count?: number
  order_count?: number
  avg_revenue_per_order?: number
  revenue_per_product?: number
}

export interface CustomerSegmentItem {
  segment: string
  customer_count?: number
  avg_order_value: number
  customer_name?: string
  customer_id?: number
  region?: string
  city?: string
  order_count?: number
  total_spent?: number
  last_purchase_date?: string
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
