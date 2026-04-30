import { AlertCircle } from 'lucide-react'

interface DashboardErrorStateProps {
  message: string
}

export function DashboardErrorState({ message }: DashboardErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-500/20 bg-red-500/10 backdrop-blur p-5">
      <div className="flex gap-3">
        <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="font-semibold text-red-300">Dashboard data unavailable</h3>
          <p className="text-sm text-red-400/90 mt-1">{message}</p>
          <p className="text-xs text-red-400/70 mt-2">
            Run the Python pipeline or{' '}
            <code className="bg-red-500/20 px-1.5 py-0.5 rounded text-red-200 font-mono">
              python frontend_export.py
            </code>{' '}
            to refresh the frontend assets.
          </p>
        </div>
      </div>
    </div>
  )
}
