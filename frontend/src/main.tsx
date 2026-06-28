import { StrictMode } from 'react'

import { QueryClientProvider } from '@tanstack/react-query'
import { createRoot } from 'react-dom/client'

import { queryClient } from '@/lib/query-client'

import { App } from './App'
import './index.css'

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element #root not found')

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
