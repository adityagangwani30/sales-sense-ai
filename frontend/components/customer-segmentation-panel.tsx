import type { CustomerSegmentItem } from '@/lib/dashboard-types'
import { formatCurrency, formatNumber } from '@/lib/formatters'

interface CustomerSegmentationPanelProps {
  segments: CustomerSegmentItem[]
}

export function CustomerSegmentationPanel({
  segments,
}: CustomerSegmentationPanelProps) {
  return (
    <section className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-foreground">Customer Segmentation</h2>
        <p className="text-sm text-foreground/60">
          Segment-level customer counts and average order values from the exported data.
        </p>
      </div>

      <div className="space-y-3">
        {segments.map((segment) => (
          <div
            key={segment.segment}
            className="rounded-xl border border-border/60 bg-background/80 px-4 py-3"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="font-medium text-foreground">{segment.segment}</h3>
                <p className="text-sm text-foreground/60">
                  {formatNumber(segment.customer_count)} customers
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-foreground/60">Avg order value</p>
                <p className="font-semibold text-foreground">
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
