import { apiClient } from '@/lib/api-client'

export type AuthStatus = 'success' | 'profile_fetch_error' | 'profile_not_found'

export interface AuthenticateRequest {
  /** Одноразовый подписанный токен из ссылки бота (привязка к Telegram-аккаунту). */
  token: string
  login: string
  password: string
}

export interface AuthenticateResponse {
  status: AuthStatus
  group_name: string | null
}

export function authenticate(body: AuthenticateRequest): Promise<AuthenticateResponse> {
  return apiClient.post<AuthenticateResponse>('/internal/v1/auth/ssau', body)
}
