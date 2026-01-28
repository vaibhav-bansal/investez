import { Check } from 'lucide-react'
import { Section } from '../ui/Section'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'

export const Pricing = () => {
  const plans = [
    {
      name: 'Free',
      price: 0,
      interval: 'forever',
      popular: false,
      features: [
        'Connect up to 2 broker accounts',
        'Basic portfolio consolidation',
        'Basic stock research',
        '5 AI queries per day',
        'Community support'
      ]
    },
    {
      name: 'Premium',
      price: 499,
      interval: 'month',
      popular: true,
      features: [
        'Connect unlimited broker accounts',
        'Full portfolio consolidation',
        'Unified performance tracking',
        'Unlimited AI queries',
        'Advanced portfolio analytics',
        'Real-time sync across brokers',
        'Priority support',
        'Early access to features'
      ]
    }
  ]

  const faqs = [
    {
      question: 'Can I cancel anytime?',
      answer: 'Yes, no commitment required. Cancel anytime with one click.'
    },
    {
      question: 'Which brokers do you support?',
      answer: 'We support Zerodha, Groww, Upstox, and more. New brokers are added regularly.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes, 14 days free trial for Premium. No credit card required.'
    }
  ]

  return (
    <Section id="pricing" background="gray">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Simple, Transparent Pricing
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Choose the plan that's right for you
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-16">
        {plans.map((plan, index) => (
          <Card
            key={index}
            className={`relative ${
              plan.popular ? 'ring-2 ring-primary shadow-xl' : ''
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-primary text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {plan.name}
              </h3>
              <div className="flex items-baseline justify-center mb-2">
                <span className="text-5xl font-bold text-gray-900">
                  ₹{plan.price}
                </span>
                <span className="text-gray-600 ml-2">
                  /{plan.interval}
                </span>
              </div>
              {plan.popular && (
                <p className="text-sm text-gray-600">
                  14-day free trial, no credit card required
                </p>
              )}
            </div>

            <ul className="space-y-3 mb-8">
              {plan.features.map((feature, featureIndex) => (
                <li key={featureIndex} className="flex items-start">
                  <Check size={20} className="text-secondary mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>

            <Button
              variant={plan.popular ? 'primary' : 'outline'}
              className="w-full"
            >
              {plan.name === 'Free' ? 'Get Started' : 'Start Free Trial'}
            </Button>
          </Card>
        ))}
      </div>

      <div className="max-w-3xl mx-auto">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Frequently Asked Questions
        </h3>
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <Card key={index}>
              <h4 className="font-semibold text-gray-900 mb-2">
                {faq.question}
              </h4>
              <p className="text-gray-600">{faq.answer}</p>
            </Card>
          ))}
        </div>
      </div>
    </Section>
  )
}
