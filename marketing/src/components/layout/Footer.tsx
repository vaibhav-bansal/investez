import { Twitter, Linkedin, Github } from 'lucide-react'

export const Footer = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const quickLinks = [
    { label: 'Features', sectionId: 'features' },
    { label: 'How It Works', sectionId: 'how-it-works' },
    { label: 'Pricing', sectionId: 'pricing' },
    { label: 'About', sectionId: 'about' }
  ]

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-2xl font-bold text-primary mb-4">InvestEz</h3>
            <p className="text-gray-400 mb-4">
              AI-powered investment research for Indian retail investors.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">
                <Twitter size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">
                <Linkedin size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">
                <Github size={20} />
              </a>
            </div>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.sectionId}>
                  <a
                    onClick={(e) => {
                      e.preventDefault()
                      scrollToSection(link.sectionId)
                    }}
                    href={`#${link.sectionId}`}
                    className="text-gray-400 hover:text-primary cursor-pointer transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Contact</h4>
            <p className="text-gray-400">
              Email: support@investez.vercel.app
            </p>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2026 InvestEz. AI-powered investment research.</p>
        </div>
      </div>
    </footer>
  )
}
