import { Section } from '../ui/Section'
import { Target, AlertCircle, Lightbulb, Eye } from 'lucide-react'

export const About = () => {
  return (
    <Section id="about" background="white">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            About InvestEz
          </h2>
          <p className="text-xl text-gray-600">
            Solving two critical problems for Indian retail investors
          </p>
        </div>

        <div className="space-y-12">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                <Target size={32} className="text-primary" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                Our Mission
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We're on a mission to bring clarity and intelligence to investing. By consolidating your portfolios
                from multiple brokers and adding AI-powered insights, we help you see the complete picture and make
                better decisions.
              </p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertCircle size={32} className="text-red-600" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                Problem #1: Scattered Investments
              </h3>
              <p className="text-gray-600 leading-relaxed mb-3">
                Most investors have accounts with multiple brokers - Zerodha, Groww, Upstox, and more.
                Your investments are scattered across different platforms, making it impossible to see the complete picture.
              </p>
              <p className="text-gray-600 leading-relaxed">
                <strong>You can't manage what you can't see.</strong> Without a unified view, you're flying blind -
                unable to track overall performance, allocation, or make informed decisions about your entire portfolio.
              </p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-orange-100 rounded-lg flex items-center justify-center">
                <Lightbulb size={32} className="text-orange-600" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                Problem #2: Complex Research
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Investment research is complex, jargon-heavy, and time-consuming. Most retail investors
                don't have access to the tools and insights that institutional investors use daily.
              </p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center">
                <Eye size={32} className="text-secondary" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                Our Solution
              </h3>
              <p className="text-gray-600 leading-relaxed mb-3">
                <strong>First, visibility.</strong> InvestEz consolidates all your investments from multiple brokers
                into one unified dashboard. See everything in one place - your complete portfolio, performance,
                allocation, and trends.
              </p>
              <p className="text-gray-600 leading-relaxed">
                <strong>Second, intelligence.</strong> We add AI-powered research and insights. Ask questions in
                plain language and get clear, actionable answers. No jargon, no complexity - just the information
                you need to make smarter decisions.
              </p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center">
                <Target size={32} className="text-purple-600" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                Our Vision
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We envision a future where every Indian investor has complete visibility of their investments
                and access to institutional-grade research tools - regardless of which brokers they use or
                how much they invest.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Section>
  )
}
