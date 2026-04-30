import Image from 'next/image'

import type { VisualizationAsset } from '@/lib/dashboard-types'

interface VisualizationGalleryProps {
  visualizations: VisualizationAsset[]
}

export function VisualizationGallery({
  visualizations,
}: VisualizationGalleryProps) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Generated Visualizations</h2>
        <p className="text-sm text-gray-400 mt-1">
          Pre-rendered analytics charts from the Python pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {visualizations.map((visualization) => (
          <article
            key={visualization.filename}
            className="overflow-hidden rounded-lg border border-white/10 bg-white/[3%] hover:border-white/20 hover:bg-white/[5%] transition-all duration-200"
          >
            <div className="border-b border-white/10 px-4 py-3 bg-white/[2%]">
              <h3 className="font-medium text-white text-sm">{visualization.title}</h3>
              <p className="text-xs text-gray-500 mt-1">{visualization.filename}</p>
            </div>
            <div className="p-3">
              <Image
                src={visualization.src}
                alt={visualization.title}
                width={1600}
                height={900}
                className="h-auto w-full rounded-md border border-white/5 bg-black/40"
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
