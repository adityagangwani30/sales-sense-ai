export const DEFAULT_DATASET_ID = 'global_ecommerce_sales'

const DATASET_ALIASES: Record<string, string> = {
  dataset_1: 'global_ecommerce_sales',
  dataset_2: 'retail_supply_chain_sales',
}

function resolveDatasetId(dataset?: string) {
  if (!dataset) {
    return DEFAULT_DATASET_ID
  }

  return DATASET_ALIASES[dataset] ?? dataset
}

export async function getDashboardData(dataset?: string) {
  const base = `/data/${resolveDatasetId(dataset)}`

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

  return {
    metrics: metrics || {},
    metricsDetailed: metricsDetailed || {},
    modelMetrics: modelMetrics || {},
    businessInsights: businessInsights || null,
  }
}
