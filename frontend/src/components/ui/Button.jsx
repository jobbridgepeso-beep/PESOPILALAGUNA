import { cn } from '@/utils/cn'

const variants = {
  primary:
    'bg-primary text-primary-foreground hover:bg-gov-navy-light shadow-sm',
  secondary:
    'border border-border bg-card text-foreground hover:bg-muted',
  ghost: 'text-muted-foreground hover:bg-muted hover:text-foreground',
  outline:
    'border-2 border-primary bg-transparent text-primary hover:bg-primary hover:text-primary-foreground',
}

const sizes = {
  sm: 'h-9 px-4 text-sm',
  md: 'h-11 px-6 text-sm',
  lg: 'h-12 px-8 text-base',
}

export default function Button({
  className,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled,
  children,
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-all duration-200 ease-out hover:scale-[1.02] active:scale-[0.98] focus-ring disabled:pointer-events-none disabled:opacity-50 disabled:hover:scale-100',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}
