import { HelmetProvider } from 'react-helmet-async'
import { Navbar } from './components/layout/Navbar'
import { Footer } from './components/layout/Footer'
import { Hero } from './components/sections/Hero'
import { Features } from './components/sections/Features'
import { HowItWorks } from './components/sections/HowItWorks'
import { Pricing } from './components/sections/Pricing'
import { About } from './components/sections/About'
import { CTA } from './components/sections/CTA'

function App() {
  return (
    <HelmetProvider>
      <div className="min-h-screen">
        <Navbar />
        <main>
          <Hero />
          <Features />
          <HowItWorks />
          <Pricing />
          <About />
          <CTA />
        </main>
        <Footer />
      </div>
    </HelmetProvider>
  )
}

export default App
