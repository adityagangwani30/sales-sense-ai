'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { HourlyData } from '@/lib/mock-data';

interface HourlyTrafficProps {
  data: HourlyData[];
}

export function HourlyTrafficChart({ data }: HourlyTrafficProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <h2 className="text-lg font-bold text-foreground mb-6">Hourly Traffic & Sales</h2>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0.02 284)" />
          <XAxis dataKey="time" stroke="oklch(0.65 0 0)" />
          <YAxis stroke="oklch(0.65 0 0)" />
          <Tooltip 
            contentStyle={{ backgroundColor: 'oklch(0.18 0.01 284)', border: '1px solid oklch(0.25 0.02 284)' }}
            labelStyle={{ color: 'oklch(0.95 0 0)' }}
          />
          <Area type="monotone" dataKey="sales" stroke="oklch(0.52 0.18 142)" fill="oklch(0.52 0.18 142)" fillOpacity={0.3} />
          <Area type="monotone" dataKey="customers" stroke="oklch(0.56 0.165 259)" fill="oklch(0.56 0.165 259)" fillOpacity={0.3} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
