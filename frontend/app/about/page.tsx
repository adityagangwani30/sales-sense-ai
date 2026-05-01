"use client";

import { useEffect, useState } from 'react';
import { CheckCircle2, Cpu, Database, Shield } from 'lucide-react';

import { Navbar } from '@/components/navbar';
import { DEFAULT_DATASET_ID, getDashboardData } from '@/lib/getDashboardData';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/format';

export default function AboutPage() {
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

  const featureCount =
    ds?.metricsDetailed?.feature_columns?.length ??
    ds?.modelMetrics?.feature_columns?.length ??
    null;
  const sampleCount =
    ds?.modelMetrics?.sample_count ??
    ds?.metricsDetailed?.sample_count ??
    ds?.metrics?.total_orders ??
    null;
  const dataPointsProcessed =
    sampleCount != null && featureCount != null
      ? Number(sampleCount) * Number(featureCount)
      : null;

  const techStack = [
    { icon: Cpu, title: 'Real-time Processing', description: 'Sub-second data processing with edge computing.' },
    { icon: Database, title: 'Multi-Source Integration', description: 'Seamless data ingestion across transactional and analytical sources.' },
    { icon: Shield, title: 'Enterprise Security', description: 'Secure deployment patterns with controlled access to exported assets.' },
    { icon: Cpu, title: 'AI & Machine Learning', description: 'Predictive analytics, performance scoring, and model comparison in one workspace.' },
  ];

  const capabilities = [
    '8+ interactive chart types',
    'Static dataset snapshots for fast loading',
    'AI-powered insights',
    'Custom report generation',
    'Multi-user collaboration',
    'Mobile-responsive design',
    'Advanced filtering and drill-down',
    'Data export workflows',
    'Business insight summaries',
    'Role-based access control ready',
    'API-driven dataset refresh pipeline',
    'Deployment-ready frontend exports',
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h1 className="mb-4 text-5xl font-bold text-foreground">About SalesSense AI</h1>
          <p className="mx-auto max-w-3xl text-xl text-foreground/60">
            Retail analytics built to turn exported data, SQL analysis, and ML outputs into decisions.
          </p>
        </div>

        <section className="mb-20 rounded-2xl border border-border bg-card p-8 md:p-12">
          <h2 className="mb-4 text-2xl font-bold text-foreground">Our Mission</h2>
          <p className="mb-4 leading-relaxed text-foreground/70">
            SalesSense AI is focused on making retail intelligence easier to access, validate, and act on. The platform brings together transactional metrics, model evaluation, and business context in a single experience.
          </p>
          <p className="leading-relaxed text-foreground/70">
            Teams can compare datasets, review predictive quality, and surface high-signal insights without digging through raw exports by hand.
          </p>
        </section>

        <section className="mb-20">
          <h2 className="mb-12 text-3xl font-bold text-foreground">Platform Capabilities</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((capability, index) => (
              <div key={index} className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-primary" />
                <span className="text-foreground">{capability}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-20 border-t border-border pt-20">
          <h2 className="mb-12 text-3xl font-bold text-foreground">Technology &amp; Architecture</h2>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            {techStack.map((tech, index) => {
              const Icon = tech.icon;

              return (
                <div key={index} className="rounded-xl border border-border bg-card p-6 transition-colors hover:border-primary/50">
                  <div className="mb-4 w-fit rounded-lg bg-primary/10 p-3">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="mb-2 text-lg font-bold text-foreground">{tech.title}</h3>
                  <p className="text-foreground/60">{tech.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        <section className="mb-20 rounded-2xl border border-border bg-card p-8 md:p-12">
          <h2 className="mb-6 text-2xl font-bold text-foreground">Architecture Overview</h2>
          <div className="space-y-4 text-foreground/70">
            <p>
              <strong className="text-foreground">Frontend:</strong> Next.js 16, React 19, and Tailwind CSS power the analytics UI.
            </p>
            <p>
              <strong className="text-foreground">Visualization:</strong> Recharts renders revenue, product, category, and predictive performance views.
            </p>
            <p>
              <strong className="text-foreground">Data Layer:</strong> Static JSON exports provide fast dataset switching without a live API dependency.
            </p>
            <p>
              <strong className="text-foreground">AI/ML Engine:</strong> Model metrics, confidence ranges, and error analysis are surfaced directly from pipeline outputs.
            </p>
            <p>
              <strong className="text-foreground">Operational Workflow:</strong> Python export scripts refresh the public assets consumed by the website.
            </p>
          </div>
        </section>

        <section className="mb-20 border-t border-border pt-20">
          <h2 className="mb-8 text-3xl font-bold text-foreground">Results Achieved</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="mb-2 text-lg font-bold text-foreground">Data Processing</h3>
              <p className="text-foreground/70">
                {ds?.metrics?.total_orders != null ? `${formatNumber(ds.metrics.total_orders)} orders processed` : 'Data not available'}
              </p>
              <p className="text-foreground/70">
                {ds?.metrics?.total_revenue != null ? `${formatCurrency(ds.metrics.total_revenue)} total revenue analyzed` : ''}
              </p>
              <p className="text-foreground/70">Features engineered: {featureCount ?? 'Data not available'}</p>
            </div>

            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="mb-2 text-lg font-bold text-foreground">Model Development</h3>
              <p className="text-foreground/70">
                Models trained: {ds?.modelMetrics?.models ? ds.modelMetrics.models.length : 'Data not available'}
              </p>
              <p className="text-foreground/70">
                Best model: {ds?.modelMetrics?.best_model?.display_name ?? 'Data not available'}
              </p>
              <p className="text-foreground/70">
                Best model R-squared: {ds?.modelMetrics?.best_model?.r2 != null ? formatPercent(ds.modelMetrics.best_model.r2) : 'Data not available'}
              </p>
            </div>

            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="mb-2 text-lg font-bold text-foreground">Model Performance</h3>
              <p className="text-foreground/70">
                MAE: {ds?.modelMetrics?.best_model?.mae != null ? formatCurrency(ds.modelMetrics.best_model.mae) : 'Data not available'}
              </p>
              <p className="text-foreground/70">
                MAPE: {ds?.modelMetrics?.best_model?.mape != null ? formatPercent(ds.modelMetrics.best_model.mape) : 'Data not available'}
              </p>
              <p className="text-foreground/70">Sample count: {sampleCount ?? 'Data not available'}</p>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-8 border-t border-border py-20 md:grid-cols-4">
          <div className="text-center">
            <p className="mb-2 text-4xl font-bold text-primary">
              {ds?.metrics?.total_customers != null ? formatNumber(ds.metrics.total_customers) : 'Data not available'}
            </p>
            <p className="text-foreground/60">Customers Profiled</p>
          </div>
          <div className="text-center">
            <p className="mb-2 text-4xl font-bold text-secondary">
              {dataPointsProcessed != null ? formatNumber(dataPointsProcessed) : 'Data not available'}
            </p>
            <p className="text-foreground/60">Data Points Processed</p>
          </div>
          <div className="text-center">
            <p className="mb-2 text-4xl font-bold text-accent">
              {ds?.metrics?.repeat_purchase_rate != null ? formatPercent(ds.metrics.repeat_purchase_rate) : 'Data not available'}
            </p>
            <p className="text-foreground/60">Repeat Purchase Rate</p>
          </div>
          <div className="text-center">
            <p className="mb-2 text-4xl font-bold text-primary">
              {ds?.modelMetrics?.best_model?.r2 != null ? formatPercent(ds.modelMetrics.best_model.r2) : 'Data not available'}
            </p>
            <p className="text-foreground/60">Top Model R-squared</p>
          </div>
        </section>

        <section className="rounded-2xl border border-border bg-card/30 p-8 md:p-12">
          <h2 className="mb-4 text-2xl font-bold text-foreground">Support &amp; Resources</h2>
          <p className="mb-6 text-foreground/70">
            The platform is designed to be refreshed from pipeline outputs quickly, so teams can re-export assets, validate model results, and publish updated dashboards with minimal friction.
          </p>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <button className="rounded-lg border border-border px-4 py-2 text-foreground transition-colors hover:bg-card">
              Documentation
            </button>
            <button className="rounded-lg border border-border px-4 py-2 text-foreground transition-colors hover:bg-card">
              Contact Support
            </button>
            <button className="rounded-lg border border-border px-4 py-2 text-foreground transition-colors hover:bg-card">
              Schedule Demo
            </button>
          </div>
        </section>
      </main>

      <footer className="mt-20 border-t border-border bg-card/30 py-12">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-foreground/60 sm:px-6 lg:px-8">
          <p>&copy; 2024 SalesSense AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
