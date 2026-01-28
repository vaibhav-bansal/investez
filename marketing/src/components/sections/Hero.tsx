import { ArrowRight } from 'lucide-react'
import { Helmet } from 'react-helmet-async'

export const Hero = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <>
      <Helmet>
        <title>InvestEz - See All Your Investments in One Place</title>
        <meta
          name="description"
          content="Consolidate investments from multiple brokers in one dashboard. Track stocks, mutual funds, and portfolios across platforms. Plus get AI-powered research and insights."
        />
        <meta property="og:title" content="InvestEz - Portfolio Consolidation & AI Research" />
        <meta
          property="og:description"
          content="See all your investments from multiple brokers in one place. AI-powered research and insights for Indian stocks and mutual funds."
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://investez.vercel.app" />
        <meta property="og:site_name" content="InvestEz" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="canonical" href="https://investez.vercel.app" />
      </Helmet>

      <section
        id="home"
        className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 text-white overflow-hidden"
      >
        <div className="absolute inset-0 bg-black opacity-20"></div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            All Your Investments
            <br />
            In One Place
          </h1>

          <p className="text-xl md:text-2xl mb-12 text-blue-100 max-w-3xl mx-auto">
            Consolidate portfolios from multiple brokers. Track all your stocks and mutual funds in a single dashboard. Get AI-powered research and insights.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => scrollToSection('pricing')}
              className="px-8 py-4 text-lg font-medium rounded-lg transition-all duration-200 cursor-pointer inline-flex items-center bg-white text-blue-600 hover:bg-gray-100 shadow-md hover:shadow-lg"
            >
              Get Started Free
              <ArrowRight className="inline-block ml-2" size={20} />
            </button>

            <button
              onClick={() => scrollToSection('features')}
              className="px-8 py-4 text-lg font-medium rounded-lg transition-all duration-200 cursor-pointer inline-flex items-center border-2 border-white text-white hover:bg-white hover:text-blue-600"
            >
              View Features
            </button>
          </div>

          <div className="mt-16">
            <img
              src="/images/dashboard-preview.png"
              alt="InvestEz Dashboard - All portfolios in one place"
              className="rounded-lg shadow-2xl mx-auto max-w-5xl w-full"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white to-transparent"></div>
      </section>
    </>
  )
}
