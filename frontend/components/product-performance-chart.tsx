'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { ProductData } from '@/lib/mock-data';

interface ProductPerformanceProps {
  data: ProductData[];
}

const COLORS = ['oklch(0.56 0.165 259)', 'oklch(0.52 0.18 142)', 'oklch(0.48 0.15 179)', 'oklch(0.65 0.12 70)', 'oklch(0.45 0.14 24)'];

export function ProductPerformanceChart({ data }: ProductPerformanceProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <h2 className="text-lg font-bold text-foreground mb-6">Revenue by Product</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="revenue"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: 'oklch(0.18 0.01 284)', border: '1px solid oklch(0.25 0.02 284)' }}
            labelStyle={{ color: 'oklch(0.95 0 0)' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
