interface DashboardErrorStateProps {
  message: string
}

export function DashboardErrorState({ message }: DashboardErrorStateProps) {
  return (
    <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-8 shadow-sm">
      <h2 className="text-lg font-semibold text-foreground">Dashboard data unavailable</h2>
      <p className="mt-2 text-sm text-foreground/70">{message}</p>
      <p className="mt-2 text-sm text-foreground/60">
        Run the Python pipeline or `python frontend_export.py` to refresh the frontend assets.
      </p>
    </div>
  )
}
