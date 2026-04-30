import Image from 'next/image'

import type { VisualizationAsset } from '@/lib/dashboard-types'

interface VisualizationGalleryProps {
  visualizations: VisualizationAsset[]
}

export function VisualizationGallery({
  visualizations,
}: VisualizationGalleryProps) {
  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">Generated Visualizations</h2>
        <p className="text-sm text-foreground/60 mt-1">
          Pre-rendered analytics charts from the Python pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {visualizations.map((visualization) => (
          <article
            key={visualization.filename}
            className="overflow-hidden rounded-lg border border-border/60 bg-background/40 hover:border-border hover:bg-background/60 transition-all duration-200"
          >
            <div className="border-b border-border/40 px-4 py-3 bg-background/20">
              <h3 className="font-medium text-foreground text-sm">{visualization.title}</h3>
              <p className="text-xs text-foreground/50 mt-1">{visualization.filename}</p>
            </div>
            <div className="p-3">
              <Image
                src={visualization.src}
                alt={visualization.title}
                width={1600}
                height={900}
                className="h-auto w-full rounded-md border border-border/30 bg-background"
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
