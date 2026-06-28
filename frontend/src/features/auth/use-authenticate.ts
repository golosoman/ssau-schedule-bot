import { useMutation } from '@tanstack/react-query'

import { authenticate } from './auth-api'

export function useAuthenticate() {
  return useMutation({ mutationFn: authenticate })
}
