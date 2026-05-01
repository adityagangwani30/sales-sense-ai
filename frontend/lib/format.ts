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
  return `${(num * (num > 1 ? 1 : 1)).toFixed(digits)}%`.replace(/\.0+%$/, '%')
}
