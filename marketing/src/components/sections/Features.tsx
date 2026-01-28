import { Layers, BarChart3, Briefcase, MessageCircle } from 'lucide-react'
import { Section } from '../ui/Section'
import { Card } from '../ui/Card'

export const Features = () => {
  const features = [
    {
      icon: <Layers size={40} className="text-primary" />,
      title: 'Portfolio Consolidation',
      description: 'See all your investments from multiple brokers in one dashboard. Zerodha, Groww, Upstox, or any platform - track everything in one place. No more switching between apps.'
    },
    {
      icon: <Briefcase size={40} className="text-primary" />,
      title: 'Unified Portfolio View',
      description: 'Get a complete picture of your holdings across stocks, mutual funds, ETFs, and bonds. Track performance, allocation, and returns from all your investment accounts together.'
    },
    {
      icon: <BarChart3 size={40} className="text-primary" />,
      title: 'AI-Powered Research',
      description: 'Get plain-language analysis of any Indian stock or mutual fund using advanced AI. No jargon, just clear insights you can understand and act on.'
    },
    {
      icon: <MessageCircle size={40} className="text-primary" />,
      title: 'Conversational Insights',
      description: 'Ask questions about your investments in natural language. "How is my portfolio performing?" or "Should I buy this stock?" - get AI-powered answers instantly.'
    }
  ]

  return (
    <Section id="features" background="gray">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Why InvestEz?
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Consolidate all your investments + get AI-powered insights
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {features.map((feature, index) => (
          <Card key={index} hover>
            <div className="mb-4">{feature.icon}</div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-3">
              {feature.title}
            </h3>
            <p className="text-gray-600 leading-relaxed">
              {feature.description}
            </p>
          </Card>
        ))}
      </div>
    </Section>
  )
}
