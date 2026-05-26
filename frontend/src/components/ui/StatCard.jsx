import { cn } from '@/utils/cn'
import { Card, CardContent } from './Card'

export default function StatCard({ label, value, icon: Icon, className, loading }) {
  return (
    <Card className={cn('transition-shadow hover:shadow-card-hover', className)}>
      <CardContent className="flex items-start justify-between gap-4 p-6">
        <div className="min-w-0 flex-1 space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          {loading ? (
            <div className="h-9 w-20 animate-pulse rounded bg-muted" />
          ) : (
            <p className="text-3xl font-bold tabular-nums tracking-tight text-foreground">
              {value ?? '—'}
            </p>
          )}
        </div>
        {Icon && (
          <div
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary"
            aria-hidden
          >
            <Icon className="h-6 w-6" strokeWidth={1.75} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
