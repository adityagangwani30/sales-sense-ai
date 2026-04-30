import { Spinner } from '@/components/ui/spinner'

export function DashboardLoadingState() {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-8 shadow-lg">
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <div className="rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 p-4">
          <Spinner className="h-8 w-8 text-purple-400" />
        </div>
        <div className="space-y-1">
          <h2 className="text-lg font-semibold text-white">Loading dashboard data</h2>
          <p className="text-sm text-gray-400">
            Fetching your analytics data...
          </p>
        </div>
      </div>
    </div>
  )
}
