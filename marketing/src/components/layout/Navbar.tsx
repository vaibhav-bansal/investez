import { useState, useEffect } from 'react'
import { Menu, X } from 'lucide-react'
import { Button } from '../ui/Button'

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setIsMobileMenuOpen(false)
    }
  }

  const navLinks = [
    { label: 'Features', sectionId: 'features' },
    { label: 'How It Works', sectionId: 'how-it-works' },
    { label: 'Pricing', sectionId: 'pricing' },
    { label: 'About', sectionId: 'about' }
  ]

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-md' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div
            onClick={() => scrollToSection('home')}
            className="flex items-center cursor-pointer"
          >
            <span className={`text-2xl font-bold transition-colors ${
              isScrolled ? 'text-primary' : 'text-white'
            }`}>
              InvestEz
            </span>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <a
                key={link.sectionId}
                onClick={(e) => {
                  e.preventDefault()
                  scrollToSection(link.sectionId)
                }}
                href={`#${link.sectionId}`}
                className={`font-medium cursor-pointer transition-colors hover:text-primary ${
                  isScrolled ? 'text-gray-700' : 'text-white'
                }`}
              >
                {link.label}
              </a>
            ))}
            <Button
              size="md"
              onClick={() => scrollToSection('pricing')}
            >
              Get Started
            </Button>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className={`p-2 ${isScrolled ? 'text-gray-700' : 'text-white'}`}
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 py-4 space-y-3">
            {navLinks.map((link) => (
              <a
                key={link.sectionId}
                onClick={(e) => {
                  e.preventDefault()
                  scrollToSection(link.sectionId)
                }}
                href={`#${link.sectionId}`}
                className="block py-2 text-gray-700 font-medium cursor-pointer hover:text-primary"
              >
                {link.label}
              </a>
            ))}
            <Button
              size="md"
              onClick={() => scrollToSection('pricing')}
              className="w-full"
            >
              Get Started
            </Button>
          </div>
        </div>
      )}
    </nav>
  )
}
