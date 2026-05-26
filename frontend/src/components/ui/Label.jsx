import { cn } from '@/utils/cn'

export default function Label({ className, children, htmlFor, required }) {
  return (
    <label
      htmlFor={htmlFor}
      className={cn('mb-2 block text-sm font-semibold text-foreground', className)}
    >
      {children}
      {required && <span className="ml-0.5 text-destructive" aria-hidden="true">*</span>}
    </label>
  )
}
