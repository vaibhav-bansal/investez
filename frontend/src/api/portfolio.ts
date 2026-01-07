import axios from 'axios'
import type { ApiResponse, Portfolio } from '../types/portfolio'

const api = axios.create({
  baseURL: '/api',
})

export async function fetchAuthStatus(): Promise<ApiResponse<{ authenticated: boolean }>> {
  const { data } = await api.get('/auth/status')
  return data
}

export async function fetchLoginUrl(): Promise<ApiResponse<{ login_url: string }>> {
  const { data } = await api.get('/auth/login-url')
  return data
}

export async function fetchPortfolio(): Promise<ApiResponse<Portfolio>> {
  const { data } = await api.get('/portfolio/')
  return data
}

export async function fetchSummary(): Promise<ApiResponse<Portfolio['summary']>> {
  const { data } = await api.get('/portfolio/summary')
  return data
}

export async function fetchHoldings(): Promise<ApiResponse<Portfolio['holdings']>> {
  const { data } = await api.get('/portfolio/holdings')
  return data
}

export async function fetchMFHoldings(): Promise<ApiResponse<Portfolio['mf_holdings']>> {
  const { data } = await api.get('/portfolio/mf')
  return data
}

export async function fetchAllocation(): Promise<ApiResponse<Portfolio['allocation']>> {
  const { data } = await api.get('/portfolio/allocation')
  return data
}
