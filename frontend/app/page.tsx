"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ArrowRight, BarChart3, Lightbulb, Shield, TrendingUp, Users, Zap } from 'lucide-react';

import { Navbar } from '@/components/navbar';
import { DEFAULT_DATASET_ID, getDashboardData } from '@/lib/getDashboardData';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/format';

export default function LandingPage() {
  const [ds, setDs] = useState<any>(null);

  useEffect(() => {
    let mounted = true;

    getDashboardData(DEFAULT_DATASET_ID).then((res) => {
      if (!mounted) return;
      setDs(res);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const sampleCount = ds?.modelMetrics?.sample_count ?? ds?.metrics?.total_orders ?? null;
  const bestModelR2 = ds?.modelMetrics?.best_model?.r2 ?? null;
  const bestModelMae = ds?.modelMetrics?.best_model?.mae ?? null;
  const businessInsightText = typeof ds?.businessInsights === 'string' ? ds.businessInsights.trim() : '';

  const features = [
    { icon: BarChart3, title: 'Revenue Trend Analysis', description: 'Visualize monthly revenue patterns, identify seasonal peaks and troughs, and spot growth trends.' },
    { icon: Zap, title: 'Feature Importance', description: 'Understand which factors matter most, from quantity and price to product and calendar effects.' },
    { icon: Shield, title: 'Model Comparison', description: 'Compare Linear Regression, Random Forest, and XGBoost with current exported metrics.' },
    { icon: TrendingUp, title: 'Customer Segmentation', description: 'Segment customers by value and behavior to tailor retention and marketing strategies.' },
    { icon: Users, title: 'Product Performance', description: 'Rank products by revenue, identify underperformers, and uncover cross-sell opportunities.' },
    { icon: Lightbulb, title: 'Prediction Confidence', description: 'Review confidence intervals and error ranges alongside each predictive output.' },
  ];

  const useCases = [
    {
      title: 'Retail Networks',
      description: 'Monitor multi-store performance, inventory levels, and sales trends across locations.',
      metrics: ['5+ locations', '45% faster insights', '2.5x ROI in 6 months'],
    },
    {
      title: 'E-Commerce Platforms',
      description: 'Track conversion funnels, customer behavior, and revenue optimization opportunities.',
      metrics: ['87% faster decisions', '15% uplift in AOV', 'Real-time alerts'],
    },
    {
      title: 'Enterprise Retailers',
      description: 'Consolidate data from multiple channels for unified business intelligence.',
      metrics: ['500+ SKUs tracked', 'Multi-channel insights', 'Automated reporting'],
    },
  ];

  return (
    <>
      <Navbar />

      <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8 md:py-32">
        <div className="mb-12 text-center">
          <div className="mb-6 inline-block animate-fade-in-up">
            <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-300 backdrop-blur">
              Enterprise-Grade Analytics Platform
            </span>
          </div>
          <h1 className="mb-6 animate-fade-in-up text-5xl font-bold text-balance text-white md:text-6xl" style={{ animationDelay: '0.1s' }}>
            SalesSense: Retail Analytics &amp; Sales Prediction System
          </h1>
          <p className="mx-auto mb-8 max-w-3xl animate-fade-in-up text-balance text-xl text-gray-400" style={{ animationDelay: '0.2s' }}>
            Transform raw transactional data into actionable insights.
          </p>
          <div className="flex animate-fade-in-up flex-col justify-center gap-4 sm:flex-row" style={{ animationDelay: '0.3s' }}>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-3 font-semibold text-white shadow-lg shadow-purple-500/50 transition-all hover:from-purple-500 hover:to-pink-500"
            >
              Launch Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
            <button className="rounded-lg border border-white/20 px-8 py-3 font-semibold text-white backdrop-blur transition-colors hover:bg-white/10">
              Schedule Demo
            </button>
          </div>
        </div>

        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-6 text-center sm:grid-cols-3">
          <div className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <p className="text-3xl font-bold text-purple-300">
              {sampleCount != null ? formatNumber(sampleCount) : 'Data not available'}
            </p>
            <p className="text-sm text-gray-400">Sales Records Analyzed</p>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <p className="text-3xl font-bold text-pink-300">
              {bestModelR2 != null ? formatPercent(bestModelR2) : 'Data not available'}
            </p>
            <p className="text-sm text-gray-400">Best Model R-squared</p>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.6s' }}>
            <p className="text-3xl font-bold text-blue-300">
              {bestModelMae != null ? formatCurrency(bestModelMae) : 'Data not available'}
            </p>
            <p className="text-sm text-gray-400">Mean Absolute Error</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-white">Powerful Features</h2>
          <p className="mx-auto max-w-2xl text-lg text-gray-400">
            Everything you need to monitor, analyze, and optimize sales performance.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;

            return (
              <div key={index} className="rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg backdrop-blur-xl transition-all duration-200 hover:border-white/20 hover:bg-white/10">
                <div className="mb-4 w-fit rounded-lg border border-purple-500/30 bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-3">
                  <Icon className="h-6 w-6 text-purple-300" />
                </div>
                <h3 className="mb-2 text-lg font-bold text-white">{feature.title}</h3>
                <p className="text-sm text-gray-400">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mx-auto max-w-6xl border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-white">Built for Your Industry</h2>
          <p className="mx-auto max-w-2xl text-lg text-gray-400">
            Trusted by leading retailers and e-commerce companies worldwide.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {useCases.map((useCase, index) => (
            <div key={index} className="rounded-xl border border-white/10 bg-white/5 p-8 shadow-lg backdrop-blur-xl transition-all duration-200 hover:border-white/20 hover:bg-white/10">
              <h3 className="mb-3 text-xl font-bold text-white">{useCase.title}</h3>
              <p className="mb-6 text-gray-400">{useCase.description}</p>
              <div className="space-y-2">
                {useCase.metrics.map((metric, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm text-gray-400">
                    <span className="h-1.5 w-1.5 rounded-full bg-gradient-to-r from-purple-400 to-pink-400" />
                    {metric}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-white">How It Works</h2>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {['Connect Data', 'Visualize Metrics', 'Take Action'].map((step, index) => (
            <div key={index} className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-purple-500/30 bg-gradient-to-br from-purple-500/20 to-pink-500/20 text-lg font-bold text-purple-300">
                {index + 1}
              </div>
              <h3 className="mb-2 text-xl font-bold text-white">{step}</h3>
              <p className="text-gray-400">
                {index === 0 && 'Connect your sales data sources in minutes with zero friction.'}
                {index === 1 && 'Explore pre-built dashboards or compare model outputs across datasets.'}
                {index === 2 && 'Export reports, set alerts, and share insights with your team.'}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-4xl font-bold text-white">Model Comparison</h2>
          <p className="mx-auto max-w-2xl text-lg text-gray-400">
            Performance metrics loaded from model outputs for the selected dataset.
          </p>
        </div>

        <div className="overflow-x-auto rounded-xl border border-white/10 bg-white/5 p-6">
          <table className="w-full text-left">
            <thead>
              <tr className="text-sm text-gray-400">
                <th className="pb-4">Model</th>
                <th className="pb-4">R-squared</th>
                <th className="pb-4">MAE</th>
                <th className="pb-4">RMSE</th>
                <th className="pb-4">MAPE</th>
              </tr>
            </thead>
            <tbody>
              {ds?.modelMetrics?.models?.length ? (
                ds.modelMetrics.models.map((model: any) => (
                  <tr key={model.name} className="border-t border-white/5">
                    <td className="py-4 font-medium text-white">{model.display_name || model.name}</td>
                    <td className="py-4 text-gray-200">{model.r2 != null ? formatPercent(model.r2) : 'Data not available'}</td>
                    <td className="py-4 text-gray-200">{model.mae != null ? formatCurrency(model.mae) : 'Data not available'}</td>
                    <td className="py-4 text-gray-200">{model.rmse != null ? formatCurrency(model.rmse) : 'Data not available'}</td>
                    <td className="py-4 text-gray-200">{model.mape != null ? formatPercent(model.mape) : 'Data not available'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="py-4 text-gray-400">Model data not available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="rounded-xl bg-white/5 p-6">
            <h3 className="mb-2 text-lg font-bold text-white">Best Model</h3>
            <p className="mb-2 text-gray-400">{ds?.modelMetrics?.best_model?.display_name ?? 'Data not available'}</p>
            <p className="text-gray-400">
              R-squared: {ds?.modelMetrics?.best_model?.r2 != null ? formatPercent(ds.modelMetrics.best_model.r2) : 'Data not available'}
            </p>
            <p className="text-gray-400">
              MAE: {ds?.modelMetrics?.best_model?.mae != null ? formatCurrency(ds.modelMetrics.best_model.mae) : 'Data not available'}
            </p>
          </div>

          <div className="rounded-xl bg-white/5 p-6">
            <h3 className="mb-2 text-lg font-bold text-white">Dataset</h3>
            <p className="text-gray-400">Records: {sampleCount != null ? formatNumber(sampleCount) : 'Data not available'}</p>
            <p className="text-gray-400">
              Revenue: {ds?.metrics?.total_revenue != null ? formatCurrency(ds.metrics.total_revenue) : 'Data not available'}
            </p>
          </div>

          <div className="rounded-xl bg-white/5 p-6">
            <h3 className="mb-2 text-lg font-bold text-white">Notes</h3>
            <p className="whitespace-pre-line text-sm text-gray-400">
              {businessInsightText || 'Business insights not available'}
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-4xl border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="rounded-2xl border border-purple-500/30 bg-gradient-to-r from-purple-500/10 to-pink-500/10 p-12 text-center backdrop-blur">
          <h2 className="mb-4 text-3xl font-bold text-white">Ready to Transform Your Sales Analytics?</h2>
          <p className="mb-8 text-lg text-gray-400">
            Start with a free demo or explore the interactive dashboard today.
          </p>
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <Link
              href="/dashboard"
              className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-3 font-semibold text-white shadow-lg shadow-purple-500/50 transition-all hover:from-purple-500 hover:to-pink-500"
            >
              Explore Dashboard
            </Link>
            <Link
              href="/about"
              className="rounded-lg border border-purple-500/30 px-8 py-3 font-semibold text-white backdrop-blur transition-colors hover:bg-purple-500/10"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>

      <footer className="mt-20 border-t border-white/10 bg-black/40 py-12 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-gray-500 sm:px-6 lg:px-8">
          <p>&copy; 2024 SalesSense AI. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}
