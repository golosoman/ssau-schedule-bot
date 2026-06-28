import type { ReactNode } from 'react'

import { useForm } from 'react-hook-form'

import { zodResolver } from '@hookform/resolvers/zod'
import {
  CalendarClock,
  CircleCheckBig,
  KeyRound,
  Loader2,
  ShieldCheck,
  TriangleAlert,
  User,
} from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { authSchema, type AuthFormValues } from './auth-schema'
import { SsauWordmark } from './components/SsauBrand'
import { useAuthenticate } from './use-authenticate'

export function AuthPage() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const mutation = useAuthenticate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AuthFormValues>({ resolver: zodResolver(authSchema) })

  const onSubmit = (values: AuthFormValues) => mutation.mutate({ token, ...values })
  const isAuthenticated = mutation.isSuccess && mutation.data.status === 'success'
  const authProblemStatus =
    mutation.isSuccess && mutation.data.status !== 'success' ? mutation.data.status : undefined
  const authErrorMessage =
    mutation.isError || authProblemStatus
      ? describeError(mutation.isError ? mutation.error : undefined, authProblemStatus)
      : null

  return (
    <main className="grid min-h-dvh lg:grid-cols-2">
      <BrandPanel />

      <section className="flex items-center justify-center px-4 py-10 sm:px-8">
        <div className="w-full max-w-md">
          <SsauWordmark className="mb-6 lg:hidden" />

          {isAuthenticated ? (
            <SuccessCard groupName={mutation.data.group_name} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Вход через СНИУ</CardTitle>
                <CardDescription>
                  Введи логин и пароль от личного кабинета — мы подтянем твоё расписание.
                </CardDescription>
              </CardHeader>

              <CardContent>
                {!token && (
                  <Alert variant="warning" className="mb-5">
                    <TriangleAlert className="mt-0.5 size-5 shrink-0" />
                    <span>
                      Ссылка недействительна или устарела. Открой её заново из бота командой{' '}
                      <b>/auth</b>.
                    </span>
                  </Alert>
                )}

                {authErrorMessage && (
                  <Alert className="mb-5">
                    <TriangleAlert className="mt-0.5 size-5 shrink-0" />
                    <span>{authErrorMessage}</span>
                  </Alert>
                )}

                <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
                  <Field
                    id="login"
                    label="Логин СНИУ"
                    icon={<User className="size-4" />}
                    error={errors.login?.message}
                  >
                    <Input
                      id="login"
                      autoComplete="username"
                      autoCapitalize="none"
                      autoCorrect="off"
                      spellCheck={false}
                      placeholder="Например, 2024-XXXX"
                      aria-invalid={!!errors.login}
                      {...register('login')}
                    />
                  </Field>

                  <Field
                    id="password"
                    label="Пароль"
                    icon={<KeyRound className="size-4" />}
                    error={errors.password?.message}
                  >
                    <Input
                      id="password"
                      type="password"
                      autoComplete="current-password"
                      placeholder="••••••••"
                      aria-invalid={!!errors.password}
                      {...register('password')}
                    />
                  </Field>

                  <Button type="submit" size="lg" disabled={!token || mutation.isPending}>
                    {mutation.isPending && <Loader2 className="size-5 animate-spin" />}
                    {mutation.isPending ? 'Проверяем…' : 'Войти и подключить расписание'}
                  </Button>
                </form>

                <p className="mt-5 flex items-center gap-2 text-xs text-slate-500">
                  <ShieldCheck className="size-4 shrink-0 text-ssau-600" />
                  Данные передаются по защищённому соединению и используются только для входа в СНИУ.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </main>
  )
}

function BrandPanel() {
  return (
    <aside className="relative hidden overflow-hidden bg-linear-to-br from-ssau-900 via-ssau-800 to-ssau-600 p-12 lg:flex lg:flex-col lg:justify-between">
      <div className="pointer-events-none absolute -top-24 -right-24 size-96 rounded-full bg-ssau-400/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -left-20 size-96 rounded-full bg-ssau-500/20 blur-3xl" />

      <SsauWordmark dark className="relative" />

      <div className="relative max-w-md">
        <h2 className="text-3xl leading-tight font-bold text-white xl:text-4xl">
          Расписание СНИУ — прямо в Telegram
        </h2>
        <p className="mt-4 text-ssau-100">
          Подключи личный кабинет один раз — и получай пары на сегодня, завтра и ближайшее занятие, а
          также уведомления перед началом.
        </p>
      </div>

      <ul className="relative flex flex-col gap-3 text-sm text-ssau-100">
        <Feature icon={<CalendarClock className="size-5" />}>
          Авто-синхронизация расписания
        </Feature>
        <Feature icon={<ShieldCheck className="size-5" />}>
          Вход на защищённой странице, не в чате
        </Feature>
      </ul>
    </aside>
  )
}

function Feature({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <li className="flex items-center gap-3">
      <span className="flex size-9 items-center justify-center rounded-lg bg-white/10 text-ssau-200">
        {icon}
      </span>
      {children}
    </li>
  )
}

function Field({
  id,
  label,
  icon,
  error,
  children,
}: {
  id: string
  label: string
  icon: ReactNode
  error?: string
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id} className="flex items-center gap-1.5 text-slate-600">
        {icon}
        {label}
      </Label>
      {children}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  )
}

function SuccessCard({ groupName }: { groupName: string | null }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-4 p-8 text-center sm:p-10">
        <div className="flex size-16 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
          <CircleCheckBig className="size-9" />
        </div>
        <div className="flex flex-col gap-1.5">
          <CardTitle>Готово!</CardTitle>
          <CardDescription>
            {groupName ? (
              <>
                Группа <b className="text-slate-700">{groupName}</b> подключена.
              </>
            ) : (
              'Доступ к СНИУ сохранён.'
            )}{' '}
            Возвращайся в Telegram — расписание уже доступно.
          </CardDescription>
        </div>
      </CardContent>
    </Card>
  )
}

function describeError(error: unknown, status?: string): string {
  if (status === 'profile_fetch_error' || status === 'profile_not_found') {
    return 'Данные сохранены, но не удалось получить профиль (группа/год). Попробуй ещё раз позже.'
  }
  if (error instanceof Error && error.message) return error.message
  return 'Не удалось войти. Проверь логин и пароль.'
}
