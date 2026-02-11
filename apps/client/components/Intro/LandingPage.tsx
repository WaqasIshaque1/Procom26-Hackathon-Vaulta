'use client'

import Header from './ui/Header'
import HeroHome from './HeroHome'
import Workflows from './Workflows'
import Features from './Features'
import Testimonials from './Testimonials'
import Footer from './ui/Footer'

export default function LandingPage({ onAccessGranted }: { onAccessGranted: () => void }) {
    return (
        <div className="flex min-h-screen flex-col overflow-hidden supports-[overflow:clip]:overflow-clip">
            <Header />
            <main className="grow">
                <HeroHome onAccessGranted={onAccessGranted} />
                <Workflows />
                <Features />
                <Testimonials />
            </main>
            <Footer />
        </div>
    )
}
