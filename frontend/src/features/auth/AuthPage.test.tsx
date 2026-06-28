import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import * as authApi from './auth-api'
import { AuthPage } from './AuthPage'

function renderWithToken(token?: string) {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: 0 } } })
  const path = token ? `/auth?token=${token}` : '/auth'
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <AuthPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AuthPage', () => {
  it('показывает форму входа', () => {
    renderWithToken('valid-token')
    expect(screen.getByRole('heading', { name: /вход через сниу/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/логин сниу/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/пароль/i)).toBeInTheDocument()
  })

  it('предупреждает, если ссылка без токена', () => {
    renderWithToken()
    expect(screen.getByRole('alert')).toHaveTextContent(/ссылка недействительна/i)
    expect(screen.getByRole('button', { name: /войти/i })).toBeDisabled()
  })

  it('валидирует пустые поля и не дёргает API', async () => {
    const spy = vi.spyOn(authApi, 'authenticate')
    const user = userEvent.setup()
    renderWithToken('valid-token')

    await user.click(screen.getByRole('button', { name: /войти/i }))

    expect(await screen.findByText(/введите логин сниу/i)).toBeInTheDocument()
    expect(screen.getByText(/введите пароль/i)).toBeInTheDocument()
    expect(spy).not.toHaveBeenCalled()
  })

  it('отправляет креды с токеном в API', async () => {
    const spy = vi
      .spyOn(authApi, 'authenticate')
      .mockResolvedValue({ status: 'success', group_name: '6132-020402D' })
    const user = userEvent.setup()
    renderWithToken('valid-token')

    await user.type(screen.getByLabelText(/логин сниу/i), 'student01')
    await user.type(screen.getByLabelText(/пароль/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /войти/i }))

    expect(await screen.findByText(/готово/i)).toBeInTheDocument()
    expect(spy.mock.calls[0]?.[0]).toEqual({
      token: 'valid-token',
      login: 'student01',
      password: 'secret123',
    })
  })
})
