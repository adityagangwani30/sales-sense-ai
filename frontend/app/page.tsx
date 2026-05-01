"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Navbar } from '@/components/navbar';
import { ArrowRight, BarChart3, Zap, Shield, TrendingUp, Users, Lightbulb } from 'lucide-react';
import { getDashboardData } from '@/lib/getDashboardData';
import { formatCurrency, formatNumber } from '@/lib/format';

export default function LandingPage() {
  const [dataset, setDataset] = useState('dataset_1')
  const [ds, setDs] = useState<any>(null)

  useEffect(() => {
    let mounted = true
    getDashboardData(dataset).then((res) => {
      if (!mounted) return
      setDs(res)
    })
    return () => {
      mounted = false
    }
  }, [dataset])

  const features = [
    { icon: BarChart3, title: 'Revenue Trend Analysis', description: 'Visualize monthly revenue patterns, identify seasonal peaks and troughs, spot growth trends' },
    { icon: Zap, title: 'Feature Importance', description: 'Understand which factors matter most: quantity, price, product and time features' },
    { icon: Shield, title: 'Model Comparison', description: 'Compare Linear Regression, Random Forest and XGBoost to choose the best model' },
    { icon: TrendingUp, title: 'Customer Segmentation', description: 'Segment customers by value and behavior to tailor retention and marketing strategies' },
    { icon: Users, title: 'Product Performance', description: 'Rank products by revenue, identify underperformers and cross-sell opportunities' },
    { icon: Lightbulb, title: 'Prediction Confidence', description: 'Provide confidence intervals and error estimates for every prediction' },
  ];

  const useCases = [
    {
      title: 'Retail Networks',
      description: 'Monitor multi-store performance, inventory levels, and sales trends across locations',
      metrics: ['5+ locations', '45% faster insights', '2.5x ROI in 6 months'],
    },
    {
      title: 'E-Commerce Platforms',
      description: 'Track conversion funnels, customer behavior, and revenue optimization opportunities',
      metrics: ['87% faster decisions', '15% uplift in AOV', 'Real-time alerts'],
    },
    {
      title: 'Enterprise Retailers',
      description: 'Consolidate data from multiple channels for unified business intelligence',
      metrics: ['500+ SKUs tracked', 'Multi-channel insights', 'Automated reporting'],
    },
  ];

  return (
    <>
      <Navbar />

        {/* Hero Section */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 md:py-32">
          <div className="text-center mb-12">
            <div className="inline-block mb-6 animate-fade-in-up">
              <span className="px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-sm font-medium backdrop-blur">
                Enterprise-Grade Analytics Platform
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 text-balance animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              SalesSense: Retail Analytics & Sales Prediction System
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto text-balance animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              Transform Raw Transactional Data Into Actionable Insights
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <Link
                href="/dashboard"
                className="px-8 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:from-purple-500 hover:to-pink-500 transition-all inline-flex items-center justify-center gap-2 shadow-lg shadow-purple-500/50"
              >
                Launch Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button className="px-8 py-3 rounded-lg border border-white/20 text-white font-semibold hover:bg-white/10 backdrop-blur transition-colors">
                Schedule Demo
              </button>
            </div>
          </div>

          {/* Quick Stats (dynamic) */}
          <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto text-center mt-16">
            <div className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
              <p className="text-3xl font-bold text-purple-300">{ds?.metrics?.total_records ? formatNumber(ds.metrics.total_records) : 'Data not available'}</p>
              <p className="text-sm text-gray-400">Sales Records Analyzed</p>
            </div>
            <div className="animate-fade-in" style={{ animationDelay: '0.5s' }}>
              <p className="text-3xl font-bold text-pink-300">{ds?.modelMetrics?.best_model?.r2 ?? ds?.metrics?.r2_score ?? 'Data not available'}</p>
              <p className="text-sm text-gray-400">Model R² (best)</p>
            </div>
            <div className="animate-fade-in" style={{ animationDelay: '0.6s' }}>
              <p className="text-3xl font-bold text-blue-300">{ds?.modelMetrics?.best_model?.mae ?? ds?.metrics?.mae ?? 'Data not available'}</p>
              <p className="text-sm text-gray-400">Mean Absolute Error</p>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-white/10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">Everything you need to monitor, analyze, and optimize your sales performance</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:border-white/20 transition-all duration-200 shadow-lg">
                  <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 w-fit mb-4">
                    <Icon className="w-6 h-6 text-purple-300" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Use Cases Section */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-white/10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Built for Your Industry</h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">Trusted by leading retailers and e-commerce companies worldwide</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {useCases.map((useCase, index) => (
              <div key={index} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-8 hover:bg-white/10 hover:border-white/20 transition-all duration-200 shadow-lg">
                <h3 className="text-xl font-bold text-white mb-3">{useCase.title}</h3>
                <p className="text-gray-400 mb-6">{useCase.description}</p>
                <div className="space-y-2">
                  {useCase.metrics.map((metric, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm text-gray-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-purple-400 to-pink-400" />
                      {metric}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How It Works */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-white/10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">How It Works</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {['Connect Data', 'Visualize Metrics', 'Take Action'].map((step, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-300 font-bold text-lg flex items-center justify-center mx-auto mb-4">
                  {index + 1}
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{step}</h3>
                <p className="text-gray-400">
                  {index === 0 && 'Connect your sales data sources in minutes with zero friction'}
                  {index === 1 && 'Choose from 20+ pre-built dashboards or create your own'}
                  {index === 2 && 'Export reports, set alerts, and share insights with your team'}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Model Comparison & Results */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-white/10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Model Comparison</h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">Performance metrics loaded from model outputs for the selected dataset</p>
          </div>

          <div className="overflow-x-auto bg-white/5 border border-white/10 rounded-xl p-6">
            <table className="w-full text-left">
              <thead>
                <tr className="text-sm text-gray-400">
                  <th className="pb-4">Model</th>
                  <th className="pb-4">R²</th>
                  <th className="pb-4">MAE</th>
                  <th className="pb-4">RMSE</th>
                  <th className="pb-4">MAPE</th>
                </tr>
              </thead>
              <tbody>
                {ds?.modelMetrics?.models?.length ? (
                  ds.modelMetrics.models.map((m: any) => (
                    <tr key={m.name} className="border-t border-white/5">
                      <td className="py-4 text-white font-medium">{m.display_name || m.name}</td>
                      <td className="py-4 text-gray-200">{m.r2 != null ? `${(m.r2 * 100).toFixed(2)}%` : 'Data not available'}</td>
                      <td className="py-4 text-gray-200">{m.mae != null ? formatCurrency(m.mae) : 'Data not available'}</td>
                      <td className="py-4 text-gray-200">{m.rmse != null ? formatCurrency(m.rmse) : 'Data not available'}</td>
                      <td className="py-4 text-gray-200">{m.mape != null ? formatPercent(m.mape) : 'Data not available'}</td>
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

          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/5 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-2">Best Model</h3>
              <p className="text-gray-400 mb-2">{ds?.modelMetrics?.best_model?.display_name ?? 'Data not available'}</p>
              <p className="text-gray-400">R²: {ds?.modelMetrics?.best_model?.r2 != null ? `${(ds.modelMetrics.best_model.r2 * 100).toFixed(2)}%` : 'Data not available'}</p>
              <p className="text-gray-400">MAE: {ds?.modelMetrics?.best_model?.mae != null ? formatCurrency(ds.modelMetrics.best_model.mae) : 'Data not available'}</p>
            </div>

            <div className="bg-white/5 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-2">Dataset</h3>
              <p className="text-gray-400">Records: {ds?.metrics?.total_orders != null ? formatNumber(ds.metrics.total_orders) : 'Data not available'}</p>
              <p className="text-gray-400">Revenue: {ds?.metrics?.total_revenue != null ? formatCurrency(ds.metrics.total_revenue) : 'Data not available'}</p>
            </div>

            <div className="bg-white/5 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-2">Notes</h3>
              <p className="text-gray-400 text-sm">{ds?.businessInsights ?? 'Business insights not available'}</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-20 border-t border-white/10">
          <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-2xl p-12 text-center backdrop-blur">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Sales Analytics?</h2>
            <p className="text-lg text-gray-400 mb-8">Start with a free demo or explore our interactive dashboard today.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard"
                className="px-8 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:from-purple-500 hover:to-pink-500 transition-all shadow-lg shadow-purple-500/50"
              >
                Explore Dashboard
              </Link>
              <Link
                href="/about"
                className="px-8 py-3 rounded-lg border border-purple-500/30 text-white font-semibold hover:bg-purple-500/10 backdrop-blur transition-colors"
              >
                Learn More
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 mt-20 py-12 bg-black/40 backdrop-blur">
          <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
            <div className="text-center text-gray-500 text-sm">
              <p>&copy; 2024 SalesSense AI. All rights reserved.</p>
            </div>
          </div>
        </footer>
    </>
  );
}
