export function formatCurrency(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === '') return 'Data not available'
  const num = Number(value)
  if (Number.isNaN(num)) return 'Data not available'
  return num.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
}

export function formatNumber(value: number | string | null | undefined, digits = 0) {
  if (value === null || value === undefined || value === '') return 'Data not available'
  const num = Number(value)
  if (Number.isNaN(num)) return 'Data not available'
  return num.toLocaleString(undefined, { maximumFractionDigits: digits })
}

export function formatPercent(value: number | string | null | undefined, digits = 2) {
  if (value === null || value === undefined || value === '') return 'Data not available'
  const num = Number(value)
  if (Number.isNaN(num)) return 'Data not available'
  // if value <= 1 treat as fraction (0.9387 -> 93.87%), else assume already percent (93.87)
  const pct = num <= 1 ? num * 100 : num
  return `${pct.toFixed(digits)}%`.replace(/\.0+%$/, '%')
}
