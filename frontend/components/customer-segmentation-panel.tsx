import type { CustomerSegmentItem } from '@/lib/dashboard-types'
import { formatCurrency, formatNumber } from '@/lib/formatters'

interface CustomerSegmentationPanelProps {
  segments: CustomerSegmentItem[]
}

export function CustomerSegmentationPanel({
  segments,
}: CustomerSegmentationPanelProps) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Customer Segmentation</h2>
        <p className="text-sm text-gray-400 mt-1">
          Customer distribution and value by segment.
        </p>
      </div>

      <div className="space-y-3">
        {segments.map((segment) => (
          <div
            key={segment.segment}
            className="rounded-lg border border-white/5 bg-white/[3%] hover:bg-white/[5%] px-4 py-3 transition-colors"
          >
            <div className="flex items-center justify-between gap-4">
              <div className="flex-1">
                <h3 className="font-semibold text-white">{segment.segment}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  {formatNumber(segment.customer_count)} customers
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">AOV</p>
                <p className="font-semibold text-white text-sm">
                  {formatCurrency(segment.avg_order_value)}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
