import { ArrowRight } from 'lucide-react'

export const CTA = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section className="relative py-20 bg-gradient-to-r from-blue-600 to-purple-700 text-white overflow-hidden">
      <div className="absolute inset-0 bg-black opacity-10"></div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl md:text-5xl font-bold mb-6">
          Ready to see all your investments in one place?
        </h2>

        <p className="text-xl md:text-2xl mb-8 text-blue-100">
          Stop switching between apps. Consolidate portfolios from all your brokers and get AI-powered insights.
        </p>

        <button
          onClick={() => scrollToSection('pricing')}
          className="px-8 py-4 text-lg font-medium rounded-lg transition-all duration-200 cursor-pointer inline-flex items-center bg-white text-blue-600 hover:bg-gray-100 shadow-md hover:shadow-lg"
        >
          Get Started Free
          <ArrowRight className="inline-block ml-2" size={20} />
        </button>
      </div>
    </section>
  )
}
