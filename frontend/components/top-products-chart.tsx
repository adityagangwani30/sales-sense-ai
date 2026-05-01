 'use client'

import React, { memo } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { TopProduct } from '@/lib/dashboard-types'
import { formatCompactCurrency, formatCurrency } from '@/lib/formatters'

interface TopProductsChartProps {
  data: TopProduct[]
}

function TopProductsChart({ data }: TopProductsChartProps) {
  const chartData = [...data]
    .slice(0, 7)
    .reverse()
    .map((item, index, items) => ({
      ...item,
      fill: index === items.length - 1 ? '#A23B72' : '#2E86AB',
    }))

  return (
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Top Products</h2>
        <p className="text-sm text-gray-400 mt-1">
          Best-selling products by revenue.
        </p>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.2} />
          <XAxis
            type="number"
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => formatCompactCurrency(value)}
          />
          <YAxis
            dataKey="product_name"
            type="category"
            tickLine={false}
            axisLine={false}
            width={120}
            tickFormatter={(value: string) =>
              value.length > 18 ? `${value.slice(0, 18)}...` : value
            }
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Revenue']}
            labelFormatter={(label) => `Product: ${label}`}
            contentStyle={{
              borderRadius: '16px',
              border: '1px solid rgba(46, 134, 171, 0.15)',
              background: 'rgba(255,255,255,0.98)',
            }}
          />
          <Bar dataKey="total_revenue" radius={[0, 10, 10, 0]}>
            {chartData.map((item) => (
              <Cell key={item.product_name} fill={item.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </section>
  )
}

export default memo(TopProductsChart)
