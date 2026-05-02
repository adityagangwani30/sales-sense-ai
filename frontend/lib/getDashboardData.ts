export const DEFAULT_DATASET_ID = 'dataset_1'

const DATASET_ALIASES: Record<string, string> = {
  global_ecommerce_sales: 'dataset_1',
  retail_supply_chain_sales: 'dataset_2',
}

function resolveDatasetId(dataset?: string) {
  if (!dataset) {
    return DEFAULT_DATASET_ID
  }

  return DATASET_ALIASES[dataset] ?? dataset
}

function toSafeNumber(value: unknown, fallback = 0): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function readRoiValueFromText(text: string | null | undefined, label: string): number | null {
  if (!text) {
    return null
  }

  const line = text
    .split('\n')
    .find((item) => item.toLowerCase().includes(label.toLowerCase()))

  if (!line) {
    return null
  }

  const parsed = Number(line.replace(/[^0-9.-]/g, ''))
  return Number.isFinite(parsed) ? parsed : null
}

function normalizeRoiPayload(raw: any) {
  const savings = toSafeNumber(
    raw?.savings ?? raw?.annual_savings ?? readRoiValueFromText(raw?.text, 'annual savings'),
  )
  const cost = toSafeNumber(
    raw?.cost ?? raw?.implementation_cost ?? readRoiValueFromText(raw?.text, 'implementation cost'),
  )
  const roi = cost > 0 ? ((savings - cost) / cost) * 100 : 0

  return {
    savings,
    cost,
    roi,
  }
}

async function fetchAggregateFallback(fetchJson: (path: string) => Promise<any>) {
  const [m1, m2, r1, r2] = await Promise.all([
    fetchJson('/data/dataset_1/ml/model_metrics.json'),
    fetchJson('/data/dataset_2/ml/model_metrics.json'),
    fetchJson('/data/ml/dataset_1/roi_analysis.json'),
    fetchJson('/data/ml/dataset_2/roi_analysis.json'),
  ])

  const totalRecords =
    toSafeNumber(m1?.sample_count, 0) +
    toSafeNumber(m2?.sample_count, 0)

  const roiOne = normalizeRoiPayload(r1)
  const roiTwo = normalizeRoiPayload(r2)
  const savings = roiOne.savings + roiTwo.savings
  const cost = roiOne.cost + roiTwo.cost
  const roi = cost > 0 ? ((savings - cost) / cost) * 100 : 0

  return {
    total_records: totalRecords,
    savings,
    cost,
    roi,
  }
}

export async function getDashboardData(dataset?: string) {
  const resolvedDatasetId = resolveDatasetId(dataset)
  const base = `/data/${resolvedDatasetId}`

  async function fetchJson(path: string) {
    try {
      const res = await fetch(path)
      if (!res.ok) return null
      return await res.json()
    } catch (e) {
      return null
    }
  }

  async function fetchText(path: string) {
    try {
      const res = await fetch(path)
      if (!res.ok) return null
      return await res.text()
    } catch (e) {
      return null
    }
  }

  const [metrics, metricsDetailed, modelMetrics, businessInsights] = await Promise.all([
    fetchJson(`${base}/metrics.json`),
    fetchJson(`${base}/ml/metrics_detailed.json`),
    fetchJson(`${base}/ml/model_metrics.json`),
    fetchText(`${base}/ml/business_insights.txt`),
  ])

  const [roiAnalysis, overviewPayload] = await Promise.all([
    fetchJson(`${base}/ml/roi_analysis.json`),
    fetchJson('/data/overview.json'),
  ])

  const normalizedRoi = normalizeRoiPayload(roiAnalysis)

  const summary = overviewPayload
    ? {
        total_records: toSafeNumber(
          overviewPayload?.total_records ?? overviewPayload?.totalRecords,
          toSafeNumber(modelMetrics?.sample_count ?? metrics?.total_orders, 0),
        ),
        savings: toSafeNumber(overviewPayload?.savings, normalizedRoi.savings),
        cost: toSafeNumber(overviewPayload?.cost, normalizedRoi.cost),
        roi: (() => {
          const savings = toSafeNumber(overviewPayload?.savings, normalizedRoi.savings)
          const cost = toSafeNumber(overviewPayload?.cost, normalizedRoi.cost)
          return cost > 0 ? ((savings - cost) / cost) * 100 : 0
        })(),
      }
    : await fetchAggregateFallback(fetchJson)

  return {
    metrics: metrics || {},
    metricsDetailed: metricsDetailed || {},
    modelMetrics: modelMetrics || {},
    roi: normalizedRoi,
    summary,
    total_records: summary.total_records,
    savings: summary.savings,
    cost: summary.cost,
    roi_pct: summary.roi,
    businessInsights: businessInsights || null,
    isLoading: false,
  }
}
