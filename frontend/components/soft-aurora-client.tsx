'use client'

import dynamic from 'next/dynamic'
import React from 'react'

const SoftAurora = dynamic(
  () => import('./soft-aurora').then((mod) => mod.SoftAurora),
  { ssr: false }
)

export default function SoftAuroraClient() {
  return (
    <SoftAurora
      brightness={1.8}
      scale={2.0}
      color1="#7c3aed"
      color2="#ec4899"
    />
  )
}
