'use client'

import { memo, useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  AlertTriangle,
  BrainCircuit,
  CircleDollarSign,
  Lightbulb,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react'

import type {
  CategoryDistributionItem,
  CustomerSegmentItem,
  DashboardDataset,
  TopProduct,
} from '@/lib/dashboard-types'
import { formatCompactCurrency, formatCurrency, formatNumber, formatPercent } from '@/lib/formatters'

interface ModelMetric {
  name: string
  display_name?: string
  mae: number
  rmse: number
  r2: number
  train_r2?: number
  test_r2?: number
  generalization_gap?: number
  fit_assessment?: string
}

interface ModelMetricsPayload {
  models?: ModelMetric[]
  best_model?: {
    name?: string
    display_name?: string
    mae?: number
    rmse?: number
    r2?: number
    mape?: number
  }
}

interface FeatureImportanceItem {
  feature: string
  importance: number
}

interface FeatureImportancePayload {
  model_based_importance?: FeatureImportanceItem[]
  permutation_importance?: FeatureImportanceItem[]
}

interface ErrorAnalysisPayload {
  mean_error?: number
  median_error?: number
  std_error?: number
  min_error?: number
  max_error?: number
  percentiles?: Record<string, number>
}

interface ConfidencePayload {
  summary?: {
    high_confidence_count?: number
    medium_confidence_count?: number
    low_confidence_count?: number
    mean_interval_width?: number
    median_interval_width?: number
  }
  samples?: Array<{
    prediction?: number
    lower_bound?: number
    upper_bound?: number
    interval_width?: number
    confidence_level?: string
  }>
}

interface RoiPayload {
  text?: string
  savings?: number
  cost?: number
  roi?: number
  annual_savings?: number
  implementation_cost?: number
  roi_pct?: number
}

interface PercentageErrorPayload {
  mean_mape?: number
  median_mape?: number
  within_5_percent?: number
  within_10_percent?: number
  within_20_percent?: number
}

interface SupplementalState {
  isLoading: boolean
  modelMetrics: ModelMetricsPayload | null
  featureImportance: FeatureImportancePayload | null
  errorAnalysis: ErrorAnalysisPayload | null
  confidenceScores: ConfidencePayload | null
  roiAnalysis: RoiPayload | null
  percentageError: PercentageErrorPayload | null
  businessInsights: string[]
  sqlRevenueTrend: Array<{ month?: string; revenue?: number; monthly_revenue?: number; month_start?: string }> | null
  sqlTopProducts: TopProduct[] | null
  sqlCategoryPerformance: CategoryDistributionItem[] | null
  sqlCustomerSegmentation: CustomerSegmentItem[] | null
}

interface DashboardDeepAnalyticsProps {
  datasetId: string
  dataset: DashboardDataset
}

const glassCardClass =
  'rounded-xl bg-white/5 backdrop-blur border border-white/10 p-4 shadow-lg'

function parseJsonLoosely(text: string): unknown {
  const normalized = text
    .replace(/\bNaN\b/g, 'null')
    .replace(/\bInfinity\b/g, 'null')
    .replace(/\b-Infinity\b/g, 'null')
  return JSON.parse(normalized)
}

async function fetchOptionalJson(paths: string[]): Promise<any | null> {
  for (const path of paths) {
    try {
      const response = await fetch(path)
      if (!response.ok) {
        continue
      }

      const text = await response.text()
      if (!text.trim()) {
        continue
      }

      const parsed = parseJsonLoosely(text)
      if (parsed !== null && parsed !== undefined) {
        return parsed
      }
    } catch {
      continue
    }
  }

  return null
}

async function fetchOptionalText(paths: string[]): Promise<string | null> {
  for (const path of paths) {
    try {
      const response = await fetch(path)
      if (!response.ok) {
        continue
      }

      const text = (await response.text()).trim()
      if (text) {
        return text
      }
    } catch {
      continue
    }
  }

  return null
}

function normalizeInsightLines(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) =>
      line.length > 0 &&
      !line.endsWith(':') &&
      line.toLowerCase() !== 'dataset: global_ecommerce_sales' &&
      line.toLowerCase() !== 'dataset: retail_supply_chain_sales' &&
      line.toLowerCase() !== 'revenue drivers' &&
      line.toLowerCase() !== 'seasonal insights' &&
      line.toLowerCase() !== 'product insights' &&
      line.toLowerCase() !== 'customer insights' &&
      !/^\d+\./.test(line),
    )
    .map((line) => line.replace(/^[-*]\s*/, ''))
}

function createDatasetAliases(datasetId: string): string[] {
  const aliases = [datasetId]

  if (datasetId === 'global_ecommerce_sales') {
    aliases.push('dataset_1')
  }
  if (datasetId === 'retail_supply_chain_sales') {
    aliases.push('dataset_2')
  }

  return aliases
}

function buildPathVariants(datasetAliases: string[], relativePath: string): string[] {
  return datasetAliases.flatMap((datasetAlias) => [
    `/data/${datasetAlias}/${relativePath}`,
    `/data/ml/${datasetAlias}/${relativePath}`,
  ])
}

function DashboardDeepAnalytics({ datasetId, dataset }: DashboardDeepAnalyticsProps) {
  const [supplemental, setSupplemental] = useState<SupplementalState>({
    isLoading: true,
    modelMetrics: null,
    featureImportance: null,
    errorAnalysis: null,
    confidenceScores: null,
    roiAnalysis: null,
    percentageError: null,
    businessInsights: [],
    sqlRevenueTrend: null,
    sqlTopProducts: null,
    sqlCategoryPerformance: null,
    sqlCustomerSegmentation: null,
  })

  useEffect(() => {
    let isMounted = true

    async function loadSupplementalAssets() {
      setSupplemental((previous) => ({ ...previous, isLoading: true }))

      const aliases = createDatasetAliases(datasetId)

      const [
        sqlRevenueTrend,
        sqlTopProducts,
        sqlCategoryPerformance,
        sqlCustomerSegmentation,
        modelMetrics,
        featureImportance,
        errorAnalysis,
        confidenceScores,
        roiAnalysis,
        percentageError,
        businessInsightsText,
      ] = await Promise.all([
        fetchOptionalJson([
          `/data/${datasetId}/sql/revenue_trend.json`,
          `/data/sql-analysis/${datasetId}/monthly_revenue_trend.json`,
          `/data/${datasetId}/revenue_trend.json`,
        ]),
        fetchOptionalJson([
          `/data/${datasetId}/sql/top_products.json`,
          `/data/sql-analysis/${datasetId}/top_products.json`,
          `/data/${datasetId}/top_products.json`,
        ]),
        fetchOptionalJson([
          `/data/${datasetId}/sql/category_performance.json`,
          `/data/sql-analysis/${datasetId}/category_performance.json`,
          `/data/${datasetId}/category_performance.json`,
        ]),
        fetchOptionalJson([
          `/data/${datasetId}/sql/customer_segmentation.json`,
          `/data/sql-analysis/${datasetId}/customer_segmentation.json`,
          `/data/${datasetId}/customer_segmentation.json`,
        ]),
        fetchOptionalJson(buildPathVariants(aliases, 'model_metrics.json')),
        fetchOptionalJson(buildPathVariants(aliases, 'feature_importance.json')),
        fetchOptionalJson(buildPathVariants(aliases, 'error_analysis.json')),
        fetchOptionalJson(buildPathVariants(aliases, 'confidence_scores.json')),
        fetchOptionalJson(buildPathVariants(aliases, 'roi_analysis.json')),
        fetchOptionalJson(buildPathVariants(aliases, 'percentage_error.json')),
        fetchOptionalText(buildPathVariants(aliases, 'business_insights.txt')),
      ])

      if (!isMounted) {
        return
      }

      setSupplemental({
        isLoading: false,
        modelMetrics: modelMetrics as ModelMetricsPayload | null,
        featureImportance: featureImportance as FeatureImportancePayload | null,
        errorAnalysis: errorAnalysis as ErrorAnalysisPayload | null,
        confidenceScores: confidenceScores as ConfidencePayload | null,
        roiAnalysis: roiAnalysis as RoiPayload | null,
        percentageError: percentageError as PercentageErrorPayload | null,
        businessInsights: businessInsightsText ? normalizeInsightLines(businessInsightsText) : [],
        sqlRevenueTrend: Array.isArray(sqlRevenueTrend)
          ? (sqlRevenueTrend as Array<{ month?: string; revenue?: number }>)
          : null,
        sqlTopProducts: Array.isArray(sqlTopProducts) ? (sqlTopProducts as TopProduct[]) : null,
        sqlCategoryPerformance: Array.isArray(sqlCategoryPerformance)
          ? (sqlCategoryPerformance as CategoryDistributionItem[])
          : null,
        sqlCustomerSegmentation: Array.isArray(sqlCustomerSegmentation)
          ? (sqlCustomerSegmentation as CustomerSegmentItem[])
          : null,
      })
    }

    loadSupplementalAssets()

    return () => {
      isMounted = false
    }
  }, [datasetId])

  const sqlRevenueData = useMemo(() => {
    if (supplemental.sqlRevenueTrend && supplemental.sqlRevenueTrend.length > 0) {
      return supplemental.sqlRevenueTrend
        .slice(-12)
        .map((item) => {
          const revenue = Number(item.revenue ?? item.monthly_revenue ?? 0)
          const month = String(item.month ?? item.month_start ?? 'N/A')
          return { month, revenue }
        })
    }

    return dataset.revenueTrend.slice(-12).map((item) => ({ month: item.month, revenue: item.revenue }))
  }, [supplemental.sqlRevenueTrend, dataset.revenueTrend])

  const sqlTopProducts = useMemo(() => {
    if (supplemental.sqlTopProducts && supplemental.sqlTopProducts.length > 0) {
      return supplemental.sqlTopProducts.slice(0, 8)
    }
    return dataset.topProducts.slice(0, 8)
  }, [supplemental.sqlTopProducts, dataset.topProducts])

  const sqlCategoryData = useMemo(() => {
    let data = supplemental.sqlCategoryPerformance && supplemental.sqlCategoryPerformance.length > 0
      ? supplemental.sqlCategoryPerformance
      : dataset.categoryDistribution

    if (data.length > 0 && !('share_pct' in data[0])) {
      const totalRev = data.reduce((sum, item) => sum + Number(item.total_revenue ?? 0), 0)
      data = data.map((item) => ({
        ...item,
        share_pct: totalRev > 0 ? (Number(item.total_revenue ?? 0) / totalRev) * 100 : 0,
      }))
    }

    return data
  }, [supplemental.sqlCategoryPerformance, dataset.categoryDistribution])

  const sqlSegments = useMemo(() => {
    if (supplemental.sqlCustomerSegmentation && supplemental.sqlCustomerSegmentation.length > 0) {
      const sample = supplemental.sqlCustomerSegmentation[0]
      const hasSegmentAggregation = 'customer_count' in sample && 'segment' in sample

      if (hasSegmentAggregation) {
        return supplemental.sqlCustomerSegmentation
          .filter((item) => Number(item.customer_count ?? 0) > 0)
          .slice(0, 6)
      }

      const aggregated: Record<string, { segment: string; customer_count: number; total_spent: number; avg_order_value: number }> = {}
      for (const row of supplemental.sqlCustomerSegmentation) {
        const seg = String(row.segment ?? 'Unknown')
        if (!aggregated[seg]) {
          aggregated[seg] = { segment: seg, customer_count: 0, total_spent: 0, avg_order_value: 0 }
        }
        aggregated[seg].customer_count += 1
        aggregated[seg].total_spent += Number(row.total_spent ?? 0)
      }
      return Object.values(aggregated)
        .map((s) => ({ ...s, avg_order_value: s.customer_count > 0 ? s.total_spent / s.customer_count : 0 }))
        .sort((a, b) => b.customer_count - a.customer_count)
        .slice(0, 6)
    }
    return dataset.customerSegmentation.slice(0, 6)
  }, [supplemental.sqlCustomerSegmentation, dataset.customerSegmentation])

  const modelRows = supplemental.modelMetrics?.models ?? []
  const bestModel = supplemental.modelMetrics?.best_model

  const modelComparisonChart = useMemo(
    () =>
      modelRows.map((model) => ({
        name: model.display_name ?? model.name,
        r2: Number(model.r2 ?? 0),
        mae: Number(model.mae ?? 0),
        rmse: Number(model.rmse ?? 0),
      })),
    [modelRows],
  )

  const predictionIntervalData = useMemo(() => {
    const samples = supplemental.confidenceScores?.samples ?? []
    return samples.slice(0, 20).map((sample, index) => ({
      index: index + 1,
      predicted: Number(sample.prediction ?? 0),
      lower: Number(sample.lower_bound ?? 0),
      upper: Number(sample.upper_bound ?? 0),
    }))
  }, [supplemental.confidenceScores?.samples])

  const errorDistributionData = useMemo(() => {
    const error = supplemental.errorAnalysis
    if (!error?.percentiles) {
      return []
    }

    return [
      { bucket: 'P5', value: Number(error.percentiles['5'] ?? 0) },
      { bucket: 'P25', value: Number(error.percentiles['25'] ?? 0) },
      { bucket: 'P50', value: Number(error.percentiles['50'] ?? 0) },
      { bucket: 'P75', value: Number(error.percentiles['75'] ?? 0) },
      { bucket: 'P95', value: Number(error.percentiles['95'] ?? 0) },
    ]
  }, [supplemental.errorAnalysis])

  const featureImportanceData = useMemo(() => {
    const modelBased = supplemental.featureImportance?.model_based_importance ?? []
    return modelBased
      .slice()
      .sort((a, b) => Number(b.importance) - Number(a.importance))
      .slice(0, 8)
      .map((item) => ({
        feature: item.feature,
        importance: Number(item.importance),
      }))
  }, [supplemental.featureImportance?.model_based_importance])

  const roiValues = useMemo(() => {
    const raw = supplemental.roiAnalysis
    if (!raw) {
      return null
    }

    const safeNumber = (value: unknown): number => {
      const parsed = Number(value)
      return Number.isFinite(parsed) ? parsed : 0
    }

    const lines = (raw.text ?? '').split('\n')
    const readFromText = (label: string): number | null => {
      const line = lines.find((item) => item.toLowerCase().includes(label.toLowerCase()))
      if (!line) {
        return null
      }
      const value = Number(line.replace(/[^0-9.-]/g, ''))
      return Number.isFinite(value) ? value : null
    }

    const annualSavings = safeNumber(
      raw.savings ?? raw.annual_savings ?? readFromText('annual savings') ?? 0,
    )
    const implementationCost = safeNumber(
      raw.cost ?? raw.implementation_cost ?? readFromText('implementation cost') ?? 0,
    )
    const roiPct = implementationCost > 0 ? ((annualSavings - implementationCost) / implementationCost) * 100 : 0

    return {
      annualSavings,
      implementationCost,
      roiPct,
      impactStatement:
        roiPct >= 250
          ? 'High-value optimization opportunity identified.'
          : roiPct >= 100
            ? 'Positive return expected from model-guided planning.'
            : 'Moderate return profile; monitor rollout assumptions.',
    }
  }, [supplemental.roiAnalysis])

  return (
    <div className="space-y-10 border-t border-white/10 pt-10">
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full" />
          SQL Analytics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={`${glassCardClass} md:col-span-2`}>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">Revenue Trend</h3>
              <p className="text-xs text-gray-400 mt-1">Monthly trend from SQL exports.</p>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={sqlRevenueData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value: number) => formatCompactCurrency(value)}
                />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), 'Revenue']}
                  contentStyle={{
                    borderRadius: '12px',
                    border: '1px solid rgba(255,255,255,0.14)',
                    background: 'rgba(15, 23, 42, 0.95)',
                  }}
                />
                <Line type="monotone" dataKey="revenue" stroke="#22D3EE" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className={glassCardClass}>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">Top Products</h3>
              <p className="text-xs text-gray-400 mt-1">Highest revenue contributors.</p>
            </div>
            <div className="space-y-2 max-h-[240px] overflow-auto pr-1">
              {sqlTopProducts.length > 0 ? (
                sqlTopProducts.map((item) => (
                  <div
                    key={item.product_name}
                    className="rounded-lg border border-white/10 bg-white/[3%] px-3 py-2"
                  >
                    <p className="text-sm font-medium text-white truncate">{item.product_name}</p>
                    <p className="text-xs text-cyan-300 mt-1">
                      {formatCurrency(item.total_revenue)} · {formatNumber(item.order_count)} orders
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-400">No top product data found.</p>
              )}
            </div>
          </div>

          <div className={glassCardClass}>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">Category Performance</h3>
              <p className="text-xs text-gray-400 mt-1">Revenue share by category.</p>
            </div>
            <div className="space-y-2">
              {sqlCategoryData.slice(0, 6).map((item) => (
                <div key={item.category} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-300 truncate mr-2">{item.category}</span>
                    <span className="text-cyan-300">{Number(item.share_pct).toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-white/10 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
                      style={{ width: `${Math.max(2, Number(item.share_pct))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={`${glassCardClass} lg:col-span-2`}>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">Customer Segmentation</h3>
              <p className="text-xs text-gray-400 mt-1">Segment mix and average value.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {sqlSegments.length > 0 ? (
                sqlSegments.map((segment) => (
                  <div key={segment.segment} className="rounded-lg border border-white/10 bg-white/[3%] p-3">
                    <p className="text-sm font-semibold text-white">{segment.segment}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatNumber(Number(segment.customer_count))} customers
                    </p>
                    <p className="text-xs text-cyan-300 mt-1">
                      Avg Order: {formatCurrency(Number(segment.avg_order_value))}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-400">No customer segmentation data found.</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-emerald-400 to-cyan-500 rounded-full" />
          ML Model Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={`${glassCardClass} lg:col-span-2`}>
            <div className="mb-4">
              <h3 className="text-base font-semibold text-white">Model Comparison (LR vs RF vs XGB)</h3>
              <p className="text-xs text-gray-400 mt-1">R² score and core error metrics.</p>
            </div>
            {modelComparisonChart.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={modelComparisonChart}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid rgba(255,255,255,0.14)',
                      background: 'rgba(15, 23, 42, 0.95)',
                    }}
                  />
                  <Legend />
                  <Bar dataKey="r2" fill="#34D399" name="R²" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="mae" fill="#22D3EE" name="MAE" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="rmse" fill="#0EA5E9" name="RMSE" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-sm text-gray-400">No model metrics found for this dataset in public data.</div>
            )}
          </div>

          <div className={glassCardClass}>
            <h3 className="text-base font-semibold text-white">Best Model Snapshot</h3>
            {bestModel ? (
              <div className="mt-4 space-y-3 text-sm">
                <div className="rounded-lg border border-emerald-400/30 bg-emerald-400/10 p-3">
                  <p className="text-emerald-300 font-semibold">{bestModel.display_name ?? bestModel.name}</p>
                </div>
                <p className="text-gray-300">MAE: <span className="text-white font-medium">{Number(bestModel.mae ?? 0).toFixed(3)}</span></p>
                <p className="text-gray-300">RMSE: <span className="text-white font-medium">{Number(bestModel.rmse ?? 0).toFixed(3)}</span></p>
                <p className="text-gray-300">R²: <span className="text-white font-medium">{Number(bestModel.r2 ?? 0).toFixed(4)}</span></p>
              </div>
            ) : (
              <p className="text-sm text-gray-400 mt-4">No best-model summary available.</p>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-sky-400 to-indigo-500 rounded-full" />
          Predictions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={`${glassCardClass} lg:col-span-2`}>
            <h3 className="text-base font-semibold text-white">Actual vs Predicted (interval view)</h3>
            <p className="text-xs text-gray-400 mt-1">Predicted values with confidence bounds from model outputs.</p>
            {predictionIntervalData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={predictionIntervalData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="index" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid rgba(255,255,255,0.14)',
                      background: 'rgba(15, 23, 42, 0.95)',
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="predicted" stroke="#22D3EE" dot={false} name="Predicted" />
                  <Line type="monotone" dataKey="lower" stroke="#94A3B8" dot={false} name="Lower bound" />
                  <Line type="monotone" dataKey="upper" stroke="#A78BFA" dot={false} name="Upper bound" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 mt-4">No prediction sample data found.</p>
            )}
          </div>

          <div className={glassCardClass}>
            <h3 className="text-base font-semibold text-white">Error Distribution</h3>
            <p className="text-xs text-gray-400 mt-1">Error percentiles and MAPE ranges.</p>
            {errorDistributionData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={errorDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="bucket" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid rgba(255,255,255,0.14)',
                      background: 'rgba(15, 23, 42, 0.95)',
                    }}
                  />
                  <Bar dataKey="value" fill="#0EA5E9" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 mt-4">No error distribution found.</p>
            )}

            {supplemental.percentageError ? (
              <div className="mt-3 space-y-1 text-xs text-gray-300">
                <p>MAPE: {Number(supplemental.percentageError.mean_mape ?? 0).toFixed(2)}%</p>
                <p>Within 5%: {Number(supplemental.percentageError.within_5_percent ?? 0).toFixed(1)}%</p>
                <p>Within 10%: {Number(supplemental.percentageError.within_10_percent ?? 0).toFixed(1)}%</p>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-amber-400 to-orange-500 rounded-full" />
          Feature Importance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={`${glassCardClass} lg:col-span-2`}>
            <h3 className="text-base font-semibold text-white">Top Features (sorted importance)</h3>
            {featureImportanceData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={featureImportanceData} layout="vertical" margin={{ left: 20, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.2} />
                  <XAxis type="number" tickLine={false} axisLine={false} />
                  <YAxis
                    dataKey="feature"
                    type="category"
                    tickLine={false}
                    axisLine={false}
                    width={130}
                  />
                  <Tooltip
                    formatter={(value: number) => [`${value.toFixed(2)}%`, 'Importance']}
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid rgba(255,255,255,0.14)',
                      background: 'rgba(15, 23, 42, 0.95)',
                    }}
                  />
                  <Bar dataKey="importance" fill="#F59E0B" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 mt-4">No feature importance file available.</p>
            )}
          </div>

          <div className={glassCardClass}>
            <h3 className="text-base font-semibold text-white">Top Drivers</h3>
            <div className="mt-3 space-y-2">
              {featureImportanceData.slice(0, 5).map((item) => (
                <div key={item.feature} className="rounded-md border border-white/10 bg-white/[3%] px-3 py-2">
                  <p className="text-sm text-white">{item.feature}</p>
                  <p className="text-xs text-amber-300 mt-0.5">{item.importance.toFixed(2)}%</p>
                </div>
              ))}
              {featureImportanceData.length === 0 ? (
                <p className="text-sm text-gray-400">No feature importance data found.</p>
              ) : null}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-fuchsia-400 to-pink-500 rounded-full" />
          Business Insights
        </h2>
        <div className={glassCardClass}>
          {supplemental.businessInsights.length > 0 ? (
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {supplemental.businessInsights.map((insight) => (
                <li key={insight} className="rounded-lg border border-fuchsia-400/20 bg-fuchsia-500/10 px-4 py-3">
                  <p className="text-sm text-fuchsia-100 leading-relaxed">• {insight}</p>
                </li>
              ))}
            </ul>
          ) : (
            <div className="rounded-lg border border-dashed border-white/20 bg-white/[2%] p-5 text-sm text-gray-400">
              Business insights file not found for this dataset. Expected path: /data/{datasetId}/ml/business_insights.txt
            </div>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-rose-400 to-red-500 rounded-full" />
          Error / Model Analysis
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-rose-300">
              <BrainCircuit className="h-4 w-4" />
              <p className="text-sm font-semibold">Overfitting Status</p>
            </div>
            <p className="text-sm text-white mt-3">
              {modelRows[0]?.fit_assessment ?? 'Not available'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Gap: {Number(modelRows[0]?.generalization_gap ?? 0).toFixed(4)}
            </p>
          </div>

          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-cyan-300">
              <Target className="h-4 w-4" />
              <p className="text-sm font-semibold">Confidence Level</p>
            </div>
            <div className="mt-3 space-y-1 text-sm text-gray-200">
              <p>High: {formatNumber(Number(supplemental.confidenceScores?.summary?.high_confidence_count ?? 0))}</p>
              <p>Medium: {formatNumber(Number(supplemental.confidenceScores?.summary?.medium_confidence_count ?? 0))}</p>
              <p>Low: {formatNumber(Number(supplemental.confidenceScores?.summary?.low_confidence_count ?? 0))}</p>
            </div>
          </div>

          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-amber-300">
              <AlertTriangle className="h-4 w-4" />
              <p className="text-sm font-semibold">Error Stats</p>
            </div>
            <div className="mt-3 space-y-1 text-sm text-gray-200">
              <p>Mean error: {Number(supplemental.errorAnalysis?.mean_error ?? 0).toFixed(3)}</p>
              <p>Std error: {Number(supplemental.errorAnalysis?.std_error ?? 0).toFixed(3)}</p>
              <p>Min/Max: {Number(supplemental.errorAnalysis?.min_error ?? 0).toFixed(2)} / {Number(supplemental.errorAnalysis?.max_error ?? 0).toFixed(2)}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-1 h-6 bg-gradient-to-b from-lime-400 to-emerald-500 rounded-full" />
          ROI / Impact
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-lime-300">
              <CircleDollarSign className="h-4 w-4" />
              <p className="text-sm font-semibold">Estimated Savings</p>
            </div>
            <p className="text-2xl font-bold text-white mt-4">
              {roiValues ? formatCurrency(roiValues.annualSavings) : 'N/A'}
            </p>
          </div>

          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-emerald-300">
              <TrendingUp className="h-4 w-4" />
              <p className="text-sm font-semibold">ROI</p>
            </div>
            <p className="text-2xl font-bold text-white mt-4">
              {roiValues ? `${roiValues.roiPct.toFixed(2)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Impl. Cost: {roiValues ? formatCurrency(roiValues.implementationCost) : 'N/A'}
            </p>
          </div>

          <div className={glassCardClass}>
            <div className="flex items-center gap-2 text-cyan-300">
              <Lightbulb className="h-4 w-4" />
              <p className="text-sm font-semibold">Business Impact</p>
            </div>
            <p className="text-sm text-gray-200 mt-4">
              {roiValues?.impactStatement ?? 'ROI analysis not available for this dataset.'}
            </p>
          </div>
        </div>
      </section>

      {supplemental.isLoading ? (
        <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 text-sm text-gray-300 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan-300 animate-pulse" />
          Loading SQL and ML analytics assets for this dataset...
        </div>
      ) : null}

      {!supplemental.isLoading && modelRows.length === 0 && supplemental.businessInsights.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/15 bg-white/[3%] backdrop-blur p-4 text-sm text-gray-400">
          ML export files were not found in /public/data for this dataset. SQL and KPI sections still use available dataset outputs.
        </div>
      ) : null}

    </div>
  )
}

export default memo(DashboardDeepAnalytics)
