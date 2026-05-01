"use client";

import { useEffect, useState } from 'react';
import { Navbar } from '@/components/navbar';
import { CheckCircle2, Cpu, Database, Shield } from 'lucide-react';
import { getDashboardData } from '@/lib/getDashboardData';
import { formatCurrency, formatNumber } from '@/lib/format';

export default function AboutPage() {
  const [dataset] = useState('dataset_1')
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

  const techStack = [
    { icon: Cpu, title: 'Real-time Processing', description: 'Sub-second data processing with edge computing' },
    { icon: Database, title: 'Multi-Source Integration', description: 'Seamless data from 50+ platforms and APIs' },
    { icon: Shield, title: 'Enterprise Security', description: 'ISO 27001, SOC 2 Type II compliance certified' },
    { icon: Cpu, title: 'AI & Machine Learning', description: 'Predictive analytics and anomaly detection' },
  ];

  const capabilities = [
    '8+ Interactive Chart Types',
    'Real-time Data Updates',
    'AI-Powered Insights',
    'Custom Report Generation',
    'Multi-User Collaboration',
    'Mobile-Responsive Design',
    'Advanced Filtering & Drill-down',
    'Data Export (CSV, PDF, Excel)',
    'Custom Alerts & Notifications',
    'Role-Based Access Control',
    'API Access & Webhooks',
    'White-Label Options',
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-foreground mb-4">About SalesSense AI</h1>
          <p className="text-xl text-foreground/60 max-w-3xl mx-auto">
            Revolutionizing retail analytics with enterprise-grade intelligence and real-time insights
          </p>
        </div>

        {/* Mission Statement */}
        <section className="bg-card border border-border rounded-2xl p-8 md:p-12 mb-20">
          <h2 className="text-2xl font-bold text-foreground mb-4">Our Mission</h2>
          <p className="text-foreground/70 leading-relaxed mb-4">
            At SalesSense AI, we believe every retailer deserves access to enterprise-grade analytics. We&apos;re on a mission to democratize data intelligence by providing powerful, intuitive tools that transform raw sales data into actionable insights.
          </p>
          <p className="text-foreground/70 leading-relaxed">
            Our platform empowers retail leaders to make smarter decisions faster, optimize operations in real-time, and unlock hidden revenue opportunities. We&apos;re committed to innovation, security, and customer success.
          </p>
        </section>

        {/* Core Features */}
        <section className="mb-20">
          <h2 className="text-3xl font-bold text-foreground mb-12">Platform Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((capability, index) => (
              <div key={index} className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-foreground">{capability}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Technology Stack */}
        <section className="mb-20 border-t border-border pt-20">
          <h2 className="text-3xl font-bold text-foreground mb-12">Technology & Architecture</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {techStack.map((tech, index) => {
              const Icon = tech.icon;
              return (
                <div key={index} className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-colors">
                  <div className="p-3 rounded-lg bg-primary/10 w-fit mb-4">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-2">{tech.title}</h3>
                  <p className="text-foreground/60">{tech.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Architecture Highlights */}
        <section className="bg-card border border-border rounded-2xl p-8 md:p-12 mb-20">
          <h2 className="text-2xl font-bold text-foreground mb-6">Architecture Overview</h2>
          <div className="space-y-4 text-foreground/70">
            <p>
              <strong className="text-foreground">Frontend:</strong> Built with Next.js 16, React 19, and Tailwind CSS for lightning-fast performance and responsive design
            </p>
            <p>
              <strong className="text-foreground">Data Visualization:</strong> Recharts for beautiful, interactive charts with smooth animations
            </p>
            <p>
              <strong className="text-foreground">Real-time Updates:</strong> Server-sent events and WebSocket support for live data streaming
            </p>
            <p>
              <strong className="text-foreground">AI/ML Engine:</strong> Advanced algorithms for predictive analytics, trend forecasting, and anomaly detection
            </p>
            <p>
              <strong className="text-foreground">Security:</strong> End-to-end encryption, role-based access control, and comprehensive audit logs
            </p>
          </div>
        </section>

        {/* Results Achieved */}
        <section className="mb-20 border-t border-border pt-20">
          <h2 className="text-3xl font-bold text-foreground mb-8">Results Achieved</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-lg font-bold text-foreground mb-2">Data Processing</h3>
              <p className="text-foreground/70">{ds?.metrics?.total_orders != null ? `${formatNumber(ds.metrics.total_orders)} orders processed` : 'Data not available'}</p>
              <p className="text-foreground/70">{ds?.metrics?.total_revenue != null ? `${formatCurrency(ds.metrics.total_revenue)} total revenue analyzed` : ''}</p>
              <p className="text-foreground/70">Features engineered: {ds?.metricsDetailed?.feature_columns ? ds.metricsDetailed.feature_columns.length : (ds?.modelMetrics?.feature_columns ? ds.modelMetrics.feature_columns.length : 'Data not available')}</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-lg font-bold text-foreground mb-2">Model Development</h3>
              <p className="text-foreground/70">Models trained: {ds?.modelMetrics?.models ? ds.modelMetrics.models.length : 'Data not available'}</p>
              <p className="text-foreground/70">Best model: {ds?.modelMetrics?.best_model?.display_name ?? 'Data not available'}</p>
              <p className="text-foreground/70">Best model R²: {ds?.modelMetrics?.best_model?.r2 != null ? `${(ds.modelMetrics.best_model.r2 * 100).toFixed(2)}%` : 'Data not available'}</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-lg font-bold text-foreground mb-2">Model Performance</h3>
              <p className="text-foreground/70">MAE: {ds?.modelMetrics?.best_model?.mae != null ? formatCurrency(ds.modelMetrics.best_model.mae) : 'Data not available'}</p>
              <p className="text-foreground/70">MAPE: {ds?.modelMetrics?.best_model?.mape != null ? formatPercent(ds.modelMetrics.best_model.mape) : 'Data not available'}</p>
              <p className="text-foreground/70">Sample count: {ds?.modelMetrics?.sample_count ?? 'Data not available'}</p>
            </div>
          </div>
        </section>

        {/* Stats (dynamic) */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-8 py-20 border-t border-border">
          <div className="text-center">
            <p className="text-4xl font-bold text-primary mb-2">{ds?.metrics?.enterprise_clients ?? 'Data not available'}</p>
            <p className="text-foreground/60">Enterprise Clients</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-secondary mb-2">{ds?.metrics?.total_data_points ? formatNumber(ds.metrics.total_data_points) : (ds?.metrics?.total_records ? formatNumber(Number(ds.metrics.total_records) * (ds.metrics.feature_count || 9)) : 'Data not available')}</p>
            <p className="text-foreground/60">Data Points Processed</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-accent mb-2">{ds?.metrics?.platform_uptime ?? 'Data not available'}</p>
            <p className="text-foreground/60">Platform Uptime</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-primary mb-2">{ds?.metrics?.data_integrations ?? 'Data not available'}</p>
            <p className="text-foreground/60">Data Integrations</p>
          </div>
        </section>

        {/* Support */}
        <section className="bg-card/30 border border-border rounded-2xl p-8 md:p-12">
          <h2 className="text-2xl font-bold text-foreground mb-4">Support & Resources</h2>
          <p className="text-foreground/70 mb-6">
            Our dedicated support team is available 24/7 to help you maximize your analytics ROI. We provide comprehensive documentation, video tutorials, and personalized onboarding for enterprise clients.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="px-4 py-2 rounded-lg border border-border text-foreground hover:bg-card transition-colors">
              Documentation
            </button>
            <button className="px-4 py-2 rounded-lg border border-border text-foreground hover:bg-card transition-colors">
              Contact Support
            </button>
            <button className="px-4 py-2 rounded-lg border border-border text-foreground hover:bg-card transition-colors">
              Schedule Demo
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-20 py-12 bg-card/30">
        <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
          <div className="text-center text-foreground/60 text-sm">
            <p>&copy; 2024 SalesSense AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
