import Badge from './Badge'
import { cn } from '@/utils/cn'

const STYLES = {
  pending: 'bg-amber-50 text-amber-800 border-amber-200',
  active: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  reviewed: 'bg-blue-50 text-blue-800 border-blue-200',
  shortlisted: 'bg-indigo-50 text-indigo-800 border-indigo-200',
  rejected: 'bg-red-50 text-red-800 border-red-200',
  hired: 'bg-gov-gold-muted text-gov-navy border-gov-gold/40',
  closed: 'bg-slate-100 text-slate-600 border-slate-200',
}

export default function StatusBadge({ status, className }) {
  const key = (status || 'pending').toLowerCase()
  return (
    <span
      className={cn(
        'inline-flex rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize',
        STYLES[key] || STYLES.pending,
        className,
      )}
    >
      {key.replace(/_/g, ' ')}
    </span>
  )
}
