import { cn } from '@/utils/cn'

export default function Select({ className, children, ...props }) {
  return (
    <select
      className={cn(
        'flex h-11 w-full rounded-md border border-input bg-card px-4 py-2 text-sm text-foreground shadow-sm',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    >
      {children}
    </select>
  )
}
