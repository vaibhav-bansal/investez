import axios from 'axios'
import type {
  ApiResponse,
  Portfolio,
  Holding,
  MFHolding,
  QuotesEnrichment,
  MarketCapEnrichment,
  MFDayChangeEnrichment
} from '../types/portfolio'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
})

export async function sendAuthCallback(requestToken: string): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/callback', { request_token: requestToken })
  return data
}

export async function fetchAuthStatus(): Promise<ApiResponse<{ user_authenticated: boolean; broker_authenticated: boolean }>> {
  const { data } = await api.get('/auth/status')
  return data
}

export async function fetchLoginUrl(): Promise<ApiResponse<{ login_url: string }>> {
  const { data } = await api.get('/auth/login-url')
  return data
}

// ============================================================================
// CORE DATA API FUNCTIONS (Fast, broker data only)
// ============================================================================

export async function fetchHoldings(): Promise<ApiResponse<Holding[]>> {
  try {
    const { data } = await api.get('/portfolio/holdings')
    return data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

export async function fetchMFHoldings(): Promise<ApiResponse<MFHolding[]>> {
  try {
    const { data } = await api.get('/portfolio/mf/holdings')
    return data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

// ============================================================================
// ENRICHMENT API FUNCTIONS (Slow, external APIs)
// ============================================================================

export async function fetchHoldingsQuotes(): Promise<ApiResponse<QuotesEnrichment>> {
  try {
    const { data } = await api.get('/portfolio/enriched/holdings/quotes')
    return data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

export async function fetchMarketCapEnrichment(): Promise<ApiResponse<MarketCapEnrichment>> {
  try {
    const { data } = await api.get('/portfolio/enriched/holdings/market-cap')
    return data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

export async function fetchMFDayChangeEnrichment(): Promise<ApiResponse<MFDayChangeEnrichment>> {
  try {
    const { data } = await api.get('/portfolio/enriched/mf/holdings/day-change')
    return data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

// ============================================================================
// LEGACY - Kept for backward compatibility, will be removed
// ============================================================================

export async function fetchPortfolio(): Promise<ApiResponse<Portfolio>> {
  try {
    const { data } = await api.get('/portfolio/')
    return data
  } catch (error: any) {
    // Return error response for token expiry detection
    if (error.response?.data) {
      return error.response.data
    }
    throw error
  }
}

export async function fetchProfile(): Promise<ApiResponse<{
  user_id: string
  user_name: string
  user_shortname: string
  email: string
  user_type: string
  broker: string
  connected_brokers: Array<{
    name: string
    broker_id: string
    user_id: string
    connected: boolean
  }>
}>> {
  const { data } = await api.get('/auth/profile')
  return data
}

export async function logout(): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/logout')
  return data
}

export async function logoutAllBrokers(): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/logout-all')
  return data
}

export async function fetchGoogleAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
  const { data } = await api.get('/auth/google/login')
  return data
}

export async function fetchCurrentUser(): Promise<ApiResponse<{
  id: number
  email: string
  name: string
  profile_picture: string
  created_at: string
}>> {
  const { data } = await api.get('/auth/google/me')
  return data
}

export async function googleLogout(): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/google/logout')
  return data
}

export interface Broker {
  id: number
  name: string
  broker_id: string
  oauth_enabled: boolean
  status: 'unconfigured' | 'configured' | 'authenticated'
  has_credentials: boolean
  user_id?: string
}

export async function fetchBrokers(): Promise<ApiResponse<{ brokers: Broker[] }>> {
  const { data } = await api.get('/brokers')
  return data
}

export async function saveBrokerCredentials(
  brokerId: string,
  apiKey: string,
  apiSecret: string
): Promise<ApiResponse<{ message: string; status: string }>> {
  const { data } = await api.post(`/brokers/${brokerId}/credentials`, {
    api_key: apiKey,
    api_secret: apiSecret,
  })
  return data
}

export async function deleteBrokerCredentials(
  brokerId: string
): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.delete(`/brokers/${brokerId}/credentials`)
  return data
}

export async function authenticateGroww(): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/groww/authenticate')
  return data
}

export async function logoutGroww(): Promise<ApiResponse<{ message: string }>> {
  const { data } = await api.post('/auth/groww/logout')
  return data
}
