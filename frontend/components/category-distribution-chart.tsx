'use client'

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import type { CategoryDistributionItem } from '@/lib/dashboard-types'
import { formatCurrency } from '@/lib/formatters'

const COLORS = ['#2E86AB', '#A23B72', '#06A77D', '#F4B942', '#5C80BC', '#6C757D']

interface CategoryDistributionChartProps {
  data: CategoryDistributionItem[]
}

export function CategoryDistributionChart({
  data,
}: CategoryDistributionChartProps) {
  return (
    <section className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-foreground">Category Distribution</h2>
        <p className="text-sm text-foreground/60">
          Revenue share by category, grouped for quick executive reading.
        </p>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey="total_revenue"
            nameKey="category"
            cx="50%"
            cy="50%"
            outerRadius={110}
            innerRadius={52}
            paddingAngle={3}
          >
            {data.map((entry, index) => (
              <Cell key={entry.category} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number, _name, item) => [
              `${formatCurrency(value)} · ${Number(item.payload.share_pct).toFixed(1)}%`,
              item.payload.category,
            ]}
            contentStyle={{
              borderRadius: '16px',
              border: '1px solid rgba(46, 134, 171, 0.15)',
              background: 'rgba(255,255,255,0.98)',
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {data.map((item, index) => (
          <div
            key={item.category}
            className="flex items-center justify-between rounded-xl bg-background/80 px-3 py-2 text-sm"
          >
            <div className="flex items-center gap-2">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="font-medium text-foreground">{item.category}</span>
            </div>
            <span className="text-foreground/60">{item.share_pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </section>
  )
}
