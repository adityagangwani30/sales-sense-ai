import { Spinner } from '@/components/ui/spinner'

export function DashboardLoadingState() {
  return (
    <div className="rounded-2xl border border-border/70 bg-card/90 p-8 shadow-sm">
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <div className="rounded-full bg-primary/10 p-4">
          <Spinner className="h-8 w-8 text-primary" />
        </div>
        <div className="space-y-1">
          <h2 className="text-lg font-semibold text-foreground">Loading dashboard data</h2>
          <p className="text-sm text-foreground/60">
            Fetching exported JSON snapshots and visualization assets.
          </p>
        </div>
      </div>
    </div>
  )
}
