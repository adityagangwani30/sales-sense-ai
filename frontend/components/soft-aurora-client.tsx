'use client'

import dynamic from 'next/dynamic'
import React from 'react'

const SoftAurora = dynamic(
  () => import('./soft-aurora').then((mod) => mod.SoftAurora),
  { ssr: false }
)

export default function SoftAuroraClient() {
  return <SoftAurora />
}
