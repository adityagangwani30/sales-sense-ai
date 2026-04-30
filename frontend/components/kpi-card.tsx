'use client';

import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Percent, BarChart3 } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string;
  change?: string;
  isPositive?: boolean;
  icon?: 'revenue' | 'transactions' | 'aov' | 'conversion' | 'satisfaction' | 'growth';
  showChangeIcon?: boolean;
}

const iconMap = {
  revenue: DollarSign,
  transactions: ShoppingCart,
  aov: BarChart3,
  conversion: Percent,
  satisfaction: TrendingUp,
  growth: TrendingUp,
};

export function KPICard({
  title,
  value,
  change,
  isPositive = true,
  icon = 'revenue',
  showChangeIcon = true,
}: KPICardProps) {
  const IconComponent = iconMap[icon];
  const ChangeIcon = isPositive ? TrendingUp : TrendingDown;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:border-white/20 transition-all duration-200 shadow-lg">
      <div className="flex items-start justify-between mb-4">
        <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
          <IconComponent className="w-5 h-5 text-purple-300" />
        </div>
        {change && (
          <div className={`flex items-center gap-1 text-sm font-semibold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
            {showChangeIcon ? <ChangeIcon className="w-4 h-4" /> : null}
            {change}
          </div>
        )}
      </div>
      <h3 className="text-sm font-medium text-gray-400 mb-2">{title}</h3>
      <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
    </div>
  );
}
