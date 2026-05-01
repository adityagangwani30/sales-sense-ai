'use client';

import React, { memo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { SalesMetric } from '@/lib/mock-data';

interface SalesTrendChartProps {
  data: SalesMetric[];
}

function SalesTrendChart({ data }: SalesTrendChartProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <h2 className="text-lg font-bold text-foreground mb-6">Sales Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0.02 284)" />
          <XAxis dataKey="date" stroke="oklch(0.65 0 0)" />
          <YAxis stroke="oklch(0.65 0 0)" />
          <Tooltip 
            contentStyle={{ backgroundColor: 'oklch(0.18 0.01 284)', border: '1px solid oklch(0.25 0.02 284)' }}
            labelStyle={{ color: 'oklch(0.95 0 0)' }}
          />
          <Legend />
          <Line type="monotone" dataKey="sales" stroke="oklch(0.56 0.165 259)" strokeWidth={2} dot={{ r: 4 }} />
          <Line type="monotone" dataKey="transactions" stroke="oklch(0.52 0.18 142)" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default memo(SalesTrendChart)
