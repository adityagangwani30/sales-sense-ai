 'use client'

import React, { memo } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { RevenueTrendPoint } from '@/lib/dashboard-types'
import { formatCompactCurrency, formatCurrency } from '@/lib/formatters'

interface RevenueTrendChartProps {
  data: RevenueTrendPoint[]
}

function RevenueTrendChart({ data }: RevenueTrendChartProps) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Revenue Trend</h2>
        <p className="text-sm text-gray-400 mt-1">
          Monthly revenue movement from your dataset.
        </p>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} minTickGap={20} />
          <YAxis
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => formatCompactCurrency(value)}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Revenue']}
            labelFormatter={(label) => `Month: ${label}`}
            contentStyle={{
              borderRadius: '16px',
              border: '1px solid rgba(46, 134, 171, 0.15)',
              background: 'rgba(255,255,255,0.98)',
            }}
          />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#2E86AB"
            strokeWidth={3}
            dot={{ r: 4, strokeWidth: 2, fill: '#ffffff' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}

export default memo(RevenueTrendChart)
