import { AlertCircle } from 'lucide-react'

interface DashboardErrorStateProps {
  message: string
}

export function DashboardErrorState({ message }: DashboardErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-5">
      <div className="flex gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="font-semibold text-red-900">Dashboard data unavailable</h3>
          <p className="text-sm text-red-800 mt-1">{message}</p>
          <p className="text-xs text-red-700 mt-2">
            Run the Python pipeline or{' '}
            <code className="bg-red-100/50 px-1.5 py-0.5 rounded text-red-900 font-mono">
              python frontend_export.py
            </code>{' '}
            to refresh the frontend assets.
          </p>
        </div>
      </div>
    </div>
  )
}
