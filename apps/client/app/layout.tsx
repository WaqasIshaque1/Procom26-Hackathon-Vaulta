import type { Metadata } from 'next'
import { Space_Grotesk, Syne } from 'next/font/google'
import './globals.css'
import IntroGate from '@/components/Intro/IntroGate'
import VapiWidgetComponent from '@/components/VapiWidgetComponent'

import localFont from 'next/font/local'
import AOSProvider from '@/components/AOSProvider'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-sans',
})

const nacelle = localFont({
  src: [
    {
      path: '../public/fonts/nacelle-regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../public/fonts/nacelle-italic.woff2',
      weight: '400',
      style: 'italic',
    },
    {
      path: '../public/fonts/nacelle-semibold.woff2',
      weight: '600',
      style: 'normal',
    },
    {
      path: '../public/fonts/nacelle-semibolditalic.woff2',
      weight: '600',
      style: 'italic',
    },
  ],
  variable: '--font-nacelle',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Vaulta Voice Agent',
  description: 'Secure voice banking assistant powered by AI',
  keywords: ['banking', 'voice AI', 'customer service', 'Vaulta'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${nacelle.variable} font-sans antialiased text-gray-200 bg-gray-950`}>
        <AOSProvider>
          <IntroGate>{children}</IntroGate>
          <VapiWidgetComponent />
        </AOSProvider>
      </body>
    </html>
  )
}
