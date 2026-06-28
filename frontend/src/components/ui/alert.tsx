import * as React from 'react'

import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const alertVariants = cva(
  'flex items-start gap-3 rounded-[var(--radius)] border p-3.5 text-sm',
  {
    variants: {
      variant: {
        error: 'border-red-200 bg-red-50 text-red-800',
        warning: 'border-amber-200 bg-amber-50 text-amber-900',
        success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
      },
    },
    defaultVariants: { variant: 'error' },
  },
)

export interface AlertProps
  extends React.ComponentProps<'div'>,
    VariantProps<typeof alertVariants> {}

export function Alert({ className, variant, ...props }: AlertProps) {
  return <div role="alert" className={cn(alertVariants({ variant, className }))} {...props} />
}
