import { z } from 'zod'

export const authSchema = z.object({
  login: z.string().trim().min(1, 'Введите логин СНИУ'),
  password: z.string().min(1, 'Введите пароль'),
})

export type AuthFormValues = z.infer<typeof authSchema>
