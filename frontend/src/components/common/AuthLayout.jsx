import { motion } from 'framer-motion'
import GovBrand from './GovBrand'
import PageMotion from './PageMotion'

export default function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      {/* Government branding panel */}
      <aside className="relative flex flex-col justify-between bg-gov-navy px-8 py-10 text-white lg:w-[42%] lg:min-h-screen lg:px-12 lg:py-14">
        <div className="gov-strip absolute left-0 right-0 top-0" />
        <motion.div
          className="pointer-events-none absolute -right-20 top-1/3 h-64 w-64 rounded-full bg-gov-gold/10 blur-3xl"
          animate={{ opacity: [0.3, 0.5, 0.3], scale: [1, 1.05, 1] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        />
        <div className="relative space-y-10 pt-4">
          <GovBrand light />
          <div className="hidden max-w-md space-y-4 lg:block">
            <p className="text-lg font-semibold leading-snug text-white">
              Public Employment Service Office
            </p>
            <p className="text-sm leading-relaxed text-white/75">
              Digitized job matching, applicant management, and employment monitoring for
              the municipality of Pila, Laguna — in service of our community.
            </p>
          </div>
        </div>
        <p className="mt-8 hidden text-xs text-white/50 lg:block">
          Official use only · Authorized personnel
        </p>
      </aside>

      {/* Form panel */}
      <main className="flex flex-1 flex-col justify-center bg-gov-surface px-6 py-10 lg:px-16 lg:py-14">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 space-y-2 lg:hidden">
            <GovBrand compact />
          </div>

          <PageMotion>
            <div className="rounded-lg border border-border bg-card p-8 shadow-card lg:p-10">
              <header className="mb-8 space-y-2 border-b border-border pb-6">
                <h1 className="text-2xl font-bold text-foreground">{title}</h1>
                {subtitle && (
                  <p className="text-sm leading-relaxed text-muted-foreground">{subtitle}</p>
                )}
              </header>
              {children}
            </div>
          </PageMotion>

          {footer && (
            <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>
          )}
        </div>
      </main>
    </div>
  )
}
