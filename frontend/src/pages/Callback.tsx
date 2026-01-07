import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Callback() {
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const [message, setMessage] = useState('Processing login...')

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search)
      const requestToken = params.get('request_token')
      const loginStatus = params.get('status')

      if (loginStatus !== 'success' || !requestToken) {
        setStatus('error')
        setMessage('Login failed or cancelled.')
        return
      }

      try {
        const response = await axios.post('/api/auth/callback', {
          request_token: requestToken,
        })

        if (response.data.success) {
          setStatus('success')
          setMessage('Login successful! Redirecting...')
          setTimeout(() => {
            window.location.href = '/'
          }, 1000)
        } else {
          setStatus('error')
          setMessage(response.data.error || 'Authentication failed.')
        }
      } catch (err) {
        setStatus('error')
        setMessage('Failed to complete authentication.')
        console.error(err)
      }
    }

    handleCallback()
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center max-w-md">
        {status === 'processing' && (
          <div className="text-gray-600">{message}</div>
        )}
        {status === 'success' && (
          <div className="text-green-600">{message}</div>
        )}
        {status === 'error' && (
          <div>
            <p className="text-red-600 mb-4">{message}</p>
            <a href="/" className="text-blue-600 hover:underline">
              Go back to home
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
