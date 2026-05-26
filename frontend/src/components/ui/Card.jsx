import { cn } from '@/utils/cn'

export function Card({ className, children }) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-card text-card-foreground shadow-card',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, children }) {
  return <div className={cn('border-b border-border px-6 py-5', className)}>{children}</div>
}

export function CardTitle({ className, children }) {
  return <h3 className={cn('text-base font-semibold text-foreground', className)}>{children}</h3>
}

export function CardDescription({ className, children }) {
  return <p className={cn('mt-1 text-sm text-muted-foreground', className)}>{children}</p>
}

export function CardContent({ className, children }) {
  return <div className={cn('px-6 py-5', className)}>{children}</div>
}
