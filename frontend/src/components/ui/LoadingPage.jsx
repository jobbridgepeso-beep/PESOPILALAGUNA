export default function LoadingPage({ message = 'Loading…' }) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center gap-4">
      <div
        className="h-10 w-10 animate-spin rounded-full border-2 border-muted border-t-primary"
        role="status"
        aria-label="Loading"
      />
      <p className="text-sm font-medium text-muted-foreground">{message}</p>
    </div>
  )
}
