'use client'

import React from 'react'
import { usePathname } from 'next/navigation'

export default function AuroraOverlayClient() {
  const pathname = usePathname()
  const isHome = pathname === '/' || pathname === ''
  const overlayClass = isHome ? 'bg-black/20' : 'bg-black/50'

  return <div className={`absolute inset-0 z-10 ${overlayClass}`} />
}
