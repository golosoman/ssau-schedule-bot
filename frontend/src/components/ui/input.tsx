import * as React from 'react'

import { cn } from '@/lib/utils'

export const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<'input'>>(
  ({ className, type, ...props }, ref) => (
    <input
      ref={ref}
      type={type}
      className={cn(
        'flex h-11 w-full rounded-[var(--radius)] border border-slate-300 bg-white px-3.5 text-base shadow-sm transition-colors',
        'placeholder:text-slate-400 focus-visible:border-ssau-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ssau-500/30',
        'disabled:cursor-not-allowed disabled:opacity-50 sm:text-sm',
        'aria-[invalid=true]:border-red-500 aria-[invalid=true]:ring-red-500/30',
        className,
      )}
      {...props}
    />
  ),
)
Input.displayName = 'Input'
