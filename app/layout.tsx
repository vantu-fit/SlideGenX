import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SlideGen',
  description: 'Project ML Course - Slide Generation',
  generator: 'DoVanTu',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
