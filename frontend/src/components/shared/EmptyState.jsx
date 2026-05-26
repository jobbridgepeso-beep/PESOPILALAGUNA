import { Card, CardContent } from '@/components/ui/Card'

export default function EmptyState({ message = 'No records found.' }) {
  return (
    <Card>
      <CardContent className="py-16 text-center text-sm text-muted-foreground">
        {message}
      </CardContent>
    </Card>
  )
}
