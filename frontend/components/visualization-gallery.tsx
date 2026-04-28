import Image from 'next/image'

import type { VisualizationAsset } from '@/lib/dashboard-types'

interface VisualizationGalleryProps {
  visualizations: VisualizationAsset[]
}

export function VisualizationGallery({
  visualizations,
}: VisualizationGalleryProps) {
  return (
    <section className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-foreground">Generated Visualizations</h2>
        <p className="text-sm text-foreground/60">
          Pre-rendered PNG outputs copied directly from the Python analytics pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {visualizations.map((visualization) => (
          <article
            key={visualization.filename}
            className="overflow-hidden rounded-2xl border border-border/70 bg-background/80"
          >
            <div className="border-b border-border/60 px-4 py-3">
              <h3 className="font-medium text-foreground">{visualization.title}</h3>
              <p className="text-xs text-foreground/50">{visualization.filename}</p>
            </div>
            <div className="p-3">
              <Image
                src={visualization.src}
                alt={visualization.title}
                width={1600}
                height={900}
                className="h-auto w-full rounded-xl border border-border/50"
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
