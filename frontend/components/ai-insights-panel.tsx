'use client';

import { useState, useEffect } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import type { SalesMetric } from '@/lib/mock-data';

interface AIInsightsPanelProps {
  data: SalesMetric[];
  dataset: string;
}

export function AIInsightsPanel({ data, dataset }: AIInsightsPanelProps) {
  const [insights, setInsights] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    // Simulate AI analysis delay
    const timer = setTimeout(() => {
      const newInsights = generateInsights(data, dataset);
      setInsights(newInsights);
      setIsLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, [data, dataset]);

  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-primary" />
        <h2 className="text-lg font-bold text-foreground">AI Insights</h2>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-5 h-5 text-primary animate-spin" />
        </div>
      ) : (
        <ul className="space-y-3">
          {insights.map((insight, index) => (
            <li key={index} className="flex gap-3 text-sm text-foreground/80">
              <span className="text-primary font-bold mt-0.5">•</span>
              <span>{insight}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function generateInsights(data: SalesMetric[], dataset: string): string[] {
  const latestData = data[data.length - 1];
  const previousData = data[data.length - 2];
  
  const insights: string[] = [];

  // Sales trend insight
  const salesGrowth = latestData.sales - previousData.sales;
  if (salesGrowth > 0) {
    insights.push(`Sales increased by ${salesGrowth.toLocaleString()} from yesterday, showing positive momentum.`);
  } else {
    insights.push(`Sales decreased by ${Math.abs(salesGrowth).toLocaleString()}, consider promotional strategies.`);
  }

  // Conversion rate insight
  const conversionTrend = latestData.conversionRate - previousData.conversionRate;
  if (conversionTrend > 0) {
    insights.push(`Conversion rate improved to ${latestData.conversionRate}%, indicating better customer engagement.`);
  } else {
    insights.push(`Conversion rate dipped to ${latestData.conversionRate}%, investigate checkout friction.`);
  }

  // AOV insight
  insights.push(`Average order value is ${latestData.avgOrderValue.toFixed(2)}, up from ${previousData.avgOrderValue.toFixed(2)}.`);

  // Peak transactions
  const avgTransactions = data.reduce((sum, d) => sum + d.transactions, 0) / data.length;
  insights.push(`Peak performance detected with ${latestData.transactions} transactions, ${Math.round(((latestData.transactions / avgTransactions - 1) * 100))}% above average.`);

  return insights;
}
