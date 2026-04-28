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
    <section className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-foreground">Key Highlights</h2>
        <p className="text-sm text-foreground/60">
          Quick business signals extracted from the selected dataset snapshot.
        </p>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.title}
              className="flex items-start gap-3 rounded-xl bg-background/80 px-4 py-3"
            >
              <div className="rounded-lg bg-primary/10 p-2">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0">
                <p className="text-sm text-foreground/60">{item.title}</p>
                <p className="truncate text-sm font-semibold text-foreground">{item.value}</p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
