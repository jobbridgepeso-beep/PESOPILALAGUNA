import { cn } from '@/utils/cn'

const variants = {
  default: 'bg-primary/10 text-primary border-primary/20',
  gold: 'bg-gov-gold-muted text-gov-navy border-gov-gold/40',
  muted: 'bg-muted text-muted-foreground border-border',
}

export default function Badge({ className, variant = 'default', children }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize tracking-wide',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}
