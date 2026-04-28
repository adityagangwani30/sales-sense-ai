'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { DepartmentData } from '@/lib/mock-data';

interface DepartmentPerformanceProps {
  data: DepartmentData[];
}

export function DepartmentPerformanceChart({ data }: DepartmentPerformanceProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <h2 className="text-lg font-bold text-foreground mb-6">Store Performance vs Target</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0.02 284)" />
          <XAxis dataKey="department" stroke="oklch(0.65 0 0)" />
          <YAxis stroke="oklch(0.65 0 0)" />
          <Tooltip 
            contentStyle={{ backgroundColor: 'oklch(0.18 0.01 284)', border: '1px solid oklch(0.25 0.02 284)' }}
            labelStyle={{ color: 'oklch(0.95 0 0)' }}
          />
          <Legend />
          <Bar dataKey="sales" fill="oklch(0.56 0.165 259)" />
          <Bar dataKey="target" fill="oklch(0.52 0.18 142)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
