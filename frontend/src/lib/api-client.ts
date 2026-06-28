const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

/** Ошибка HTTP-запроса с кодом и сообщением из тела (FastAPI `detail`). */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError(0, 'Не удалось связаться с сервером. Проверь соединение.')
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(response.status, body?.detail ?? `Ошибка ${response.status}`)
  }
  return (await response.json()) as T
}

export const apiClient = {
  post: <T>(path: string, body: unknown): Promise<T> =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}
