import type { Metadata, Viewport } from 'next'
import SoftAuroraClient from '@/components/soft-aurora-client'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });


export const metadata: Metadata = {
  title: 'SalesSense AI - Retail Analytics Platform',
  description: 'Advanced AI-powered retail analytics and sales intelligence platform with real-time insights and predictive analytics.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="bg-background">
      <body className="font-sans antialiased">
        <div className="relative min-h-screen overflow-hidden bg-black">

          <div className="absolute inset-0 z-0">
            <SoftAuroraClient />
          </div>

          <div className="absolute inset-0 bg-black/60 z-10" />

          <div className="relative z-20">
            {children}
            {process.env.NODE_ENV === 'production' && <Analytics />}
          </div>

        </div>
      </body>
    </html>
  )
}
