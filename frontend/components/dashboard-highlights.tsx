import { ArrowUpRight, Boxes, CalendarRange, RotateCcw } from 'lucide-react'

import type { DashboardDataset } from '@/lib/dashboard-types'
import { formatPercent } from '@/lib/formatters'

interface DashboardHighlightsProps {
  dataset: DashboardDataset
}

export function DashboardHighlights({ dataset }: DashboardHighlightsProps) {
  const items = [
    {
      title: 'Peak month',
      value: dataset.highlights.peakMonth ?? 'Not available',
      icon: CalendarRange,
    },
    {
      title: 'Top product',
      value: dataset.highlights.topProduct ?? 'Not available',
      icon: ArrowUpRight,
    },
    {
      title: 'Largest category',
      value: dataset.highlights.largestCategory ?? 'Not available',
      icon: Boxes,
    },
    {
      title: 'Repeat purchase rate',
      value: formatPercent(dataset.kpis.repeatPurchaseRate).replace('+', ''),
      icon: RotateCcw,
    },
  ]

  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">Key Highlights</h2>
        <p className="text-sm text-foreground/60 mt-1">
          Quick business signals from this dataset.
        </p>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.title}
              className="flex items-center gap-3 rounded-lg bg-background/40 hover:bg-background/60 px-3 py-3 transition-colors"
            >
              <div className="rounded-lg bg-primary/10 p-2 flex-shrink-0">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-foreground/50 font-medium uppercase tracking-wide">{item.title}</p>
                <p className="truncate text-sm font-semibold text-foreground mt-0.5">{item.value}</p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
