import { cn } from '@/lib/utils'

export function SsauLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={cn('h-10 w-10', className)} aria-hidden="true">
      <rect width="64" height="64" rx="14" className="fill-white/10" />
      <path
        d="M41 24.5c-1.8-2.2-4.7-3.5-8.2-3.5-6 0-9.8 3.2-9.8 7.6 0 4 3 6 8 7.1l2.7.6c2.6.6 3.7 1.4 3.7 2.8 0 1.6-1.6 2.7-4.3 2.7-2.9 0-5-1.2-6.4-3.2L22 41.4C23.9 44.2 27.4 46 32.3 46c6.3 0 10.2-3.2 10.2-7.9 0-4-2.7-6-8.1-7.2l-2.7-.6c-2.5-.5-3.6-1.3-3.6-2.7 0-1.5 1.5-2.6 4-2.6 2.6 0 4.6 1.1 5.8 2.9l4.1-3.4Z"
        className="fill-ssau-300"
      />
    </svg>
  )
}

export function SsauWordmark({ className, dark = false }: { className?: string; dark?: boolean }) {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <SsauLogo className={dark ? '' : 'h-9 w-9'} />
      <div className="leading-tight">
        <p className={cn('text-sm font-semibold', dark ? 'text-white' : 'text-slate-900')}>
          Самарский университет
        </p>
        <p className={cn('text-xs', dark ? 'text-ssau-200' : 'text-slate-500')}>
          Бот расписания
        </p>
      </div>
    </div>
  )
}
