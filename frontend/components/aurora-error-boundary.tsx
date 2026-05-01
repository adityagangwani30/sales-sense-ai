'use client'

import React from 'react'

interface Props {
  children: React.ReactNode
}

interface State {
  hasError: boolean
}

export class AuroraErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    // Silently swallow WebGL/aurora errors — background is non-critical
    console.warn('[AuroraErrorBoundary] Aurora background failed to render:', error?.message)
  }

  render() {
    if (this.state.hasError) {
      // Render nothing — the page background is just missing the aurora effect
      return null
    }
    return this.props.children
  }
}
