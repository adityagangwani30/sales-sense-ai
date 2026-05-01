'use client'

import { useEffect } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function DashboardError({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error('[Dashboard] Unhandled error:', error)
  }, [error])

  return (
    <div className="mx-auto max-w-7xl px-6 py-20 flex items-center justify-center min-h-[60vh]">
      <div className="text-center space-y-6 max-w-md">
        <div className="mx-auto w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
          <AlertCircle className="h-8 w-8 text-red-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard failed to load</h1>
          <p className="mt-2 text-sm text-gray-400">
            An unexpected error occurred while rendering the dashboard.
          </p>
          {error?.message && (
            <p className="mt-3 text-xs font-mono bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2 text-red-300 break-all">
              {error.message}
            </p>
          )}
        </div>
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      </div>
    </div>
  )
}
