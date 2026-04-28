'use client';

import Link from 'next/link';
import { Navbar } from '@/components/navbar';
import { ArrowRight, BarChart3, Zap, Shield, TrendingUp, Users, Lightbulb } from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Real-time dashboards with 8+ visualization types for comprehensive insights',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Sub-second data processing and chart rendering for instant insights',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-grade encryption and compliance with GDPR, SOC 2, and more',
    },
    {
      icon: TrendingUp,
      title: 'AI-Powered Insights',
      description: 'Machine learning algorithms that uncover hidden patterns and trends',
    },
    {
      icon: Users,
      title: 'Multi-User Collaboration',
      description: 'Share dashboards and insights with your entire team in real-time',
    },
    {
      icon: Lightbulb,
      title: 'Predictive Analytics',
      description: 'Forecast future trends and make data-driven decisions with confidence',
    },
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
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 md:py-32">
        <div className="text-center mb-12">
          <div className="inline-block mb-6 animate-fade-in-up">
            <span className="px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium">
              Enterprise-Grade Analytics Platform
            </span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6 text-balance animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            Unlock Sales Intelligence with
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"> SalesSense AI</span>
          </h1>
          <p className="text-xl text-foreground/70 mb-8 max-w-3xl mx-auto text-balance animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            Transform raw sales data into actionable insights. Monitor real-time metrics, predict trends, and make data-driven decisions that drive revenue growth.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <Link
              href="/dashboard"
              className="px-8 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity inline-flex items-center justify-center gap-2"
            >
              Launch Dashboard
              <ArrowRight className="w-4 h-4" />
            </Link>
            <button className="px-8 py-3 rounded-lg border border-border text-foreground font-semibold hover:bg-card transition-colors">
              Schedule Demo
            </button>
          </div>
        </div>

        {/* Hero Stats */}
        <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto text-center mt-16">
          <div className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <p className="text-3xl font-bold text-primary">500+</p>
            <p className="text-sm text-foreground/60">Enterprise Clients</p>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <p className="text-3xl font-bold text-secondary">99.9%</p>
            <p className="text-sm text-foreground/60">Uptime SLA</p>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.6s' }}>
            <p className="text-3xl font-bold text-accent">4.9/5</p>
            <p className="text-sm text-foreground/60">Customer Rating</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-border">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-foreground mb-4">Powerful Features</h2>
          <p className="text-lg text-foreground/60 max-w-2xl mx-auto">Everything you need to monitor, analyze, and optimize your sales performance</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-colors">
                <div className="p-3 rounded-lg bg-primary/10 w-fit mb-4">
                  <Icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">{feature.title}</h3>
                <p className="text-foreground/60 text-sm">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-border">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-foreground mb-4">Built for Your Industry</h2>
          <p className="text-lg text-foreground/60 max-w-2xl mx-auto">Trusted by leading retailers and e-commerce companies worldwide</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {useCases.map((useCase, index) => (
            <div key={index} className="bg-card border border-border rounded-xl p-8 hover:border-primary/50 transition-colors">
              <h3 className="text-xl font-bold text-foreground mb-3">{useCase.title}</h3>
              <p className="text-foreground/60 mb-6">{useCase.description}</p>
              <div className="space-y-2">
                {useCase.metrics.map((metric, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm text-foreground/70">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                    {metric}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-20 border-t border-border">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-foreground mb-4">How It Works</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {['Connect Data', 'Visualize Metrics', 'Take Action'].map((step, index) => (
            <div key={index} className="text-center">
              <div className="w-12 h-12 rounded-full bg-primary/20 text-primary font-bold text-lg flex items-center justify-center mx-auto mb-4">
                {index + 1}
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">{step}</h3>
              <p className="text-foreground/60">
                {index === 0 && 'Connect your sales data sources in minutes with zero friction'}
                {index === 1 && 'Choose from 20+ pre-built dashboards or create your own'}
                {index === 2 && 'Export reports, set alerts, and share insights with your team'}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-20 border-t border-border">
        <div className="bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/30 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Ready to Transform Your Sales Analytics?</h2>
          <p className="text-lg text-foreground/70 mb-8">Start with a free demo or explore our interactive dashboard today.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-8 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
            >
              Explore Dashboard
            </Link>
            <Link
              href="/about"
              className="px-8 py-3 rounded-lg border border-primary text-foreground font-semibold hover:bg-primary/5 transition-colors"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>

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
