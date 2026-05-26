import { Building2 } from 'lucide-react'
import { cn } from '@/utils/cn'

/** Official PESO / government branding block */
export default function GovBrand({ compact = false, light = false, className }) {
  return (
    <div className={cn('flex items-start gap-3', className)}>
      <div
        className={cn(
          'flex shrink-0 items-center justify-center rounded-lg border',
          compact ? 'h-10 w-10' : 'h-12 w-12',
          light
            ? 'border-white/20 bg-white/10 text-gov-gold'
            : 'border-gov-gold/30 bg-gov-gold-muted text-primary',
        )}
        aria-hidden
      >
        <Building2 className={compact ? 'h-5 w-5' : 'h-6 w-6'} strokeWidth={1.75} />
      </div>
      <div className="min-w-0">
        <p
          className={cn(
            'text-[10px] font-semibold uppercase tracking-[0.2em]',
            light ? 'text-white/70' : 'text-muted-foreground',
          )}
        >
          Republic of the Philippines
        </p>
        <p
          className={cn(
            'font-bold leading-tight',
            compact ? 'text-base' : 'text-lg',
            light ? 'text-white' : 'text-foreground',
          )}
        >
          PESO Pila, Laguna
        </p>
        <p
          className={cn(
            'text-sm font-medium',
            light ? 'text-gov-gold' : 'text-primary',
          )}
        >
          JobBridge Employment System
        </p>
      </div>
    </div>
  )
}
