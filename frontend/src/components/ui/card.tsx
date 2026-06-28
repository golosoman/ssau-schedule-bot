import * as React from 'react'

import { cn } from '@/lib/utils'

export function Card({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-slate-200 bg-white shadow-xl shadow-ssau-950/5',
        className,
      )}
      {...props}
    />
  )
}

export function CardHeader({ className, ...props }: React.ComponentProps<'div'>) {
  return <div className={cn('flex flex-col gap-1.5 p-6 sm:p-8', className)} {...props} />
}

export function CardTitle({ className, ...props }: React.ComponentProps<'h1'>) {
  return (
    <h1 className={cn('text-xl font-semibold tracking-tight sm:text-2xl', className)} {...props} />
  )
}

export function CardDescription({ className, ...props }: React.ComponentProps<'p'>) {
  return <p className={cn('text-sm text-slate-500', className)} {...props} />
}

export function CardContent({ className, ...props }: React.ComponentProps<'div'>) {
  return <div className={cn('p-6 pt-0 sm:p-8 sm:pt-0', className)} {...props} />
}
