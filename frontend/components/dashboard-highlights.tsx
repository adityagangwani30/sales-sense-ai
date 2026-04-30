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
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Key Highlights</h2>
        <p className="text-sm text-gray-400 mt-1">
          Quick business signals from this dataset.
        </p>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.title}
              className="flex items-center gap-3 rounded-lg bg-white/[3%] hover:bg-white/[5%] px-3 py-3 transition-colors border border-white/5"
            >
              <div className="rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 p-2 flex-shrink-0">
                <Icon className="h-4 w-4 text-purple-300" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{item.title}</p>
                <p className="truncate text-sm font-semibold text-white mt-0.5">{item.value}</p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
