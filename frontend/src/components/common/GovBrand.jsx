import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

const LOGO_SRC = '/images/peso-logo.png'

/** Official PESO branding with circular logo */
export default function GovBrand({ compact = false, light = false, className, animate = true }) {
  const logoSize = compact ? 'h-11 w-11' : 'h-16 w-16'

  const Logo = animate ? motion.img : 'img'
  const logoProps = animate
    ? {
        initial: { scale: 0.85, opacity: 0 },
        animate: { scale: 1, opacity: 1 },
        transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] },
      }
    : {}

  const textVariants = {
    hidden: { opacity: 0, x: -8 },
    show: (i) => ({
      opacity: 1,
      x: 0,
      transition: { delay: 0.15 + i * 0.08, duration: 0.4 },
    }),
  }

  return (
    <div className={cn('flex items-center gap-4', className)}>
      <Logo
        src={LOGO_SRC}
        alt="Public Employment Service Office (PESO) logo"
        className={cn('shrink-0 rounded-full object-contain shadow-sm', logoSize)}
        {...logoProps}
      />
      <div className="min-w-0">
        {animate ? (
          <>
            <motion.p
              custom={0}
              variants={textVariants}
              initial="hidden"
              animate="show"
              className={cn(
                'text-[10px] font-semibold uppercase tracking-[0.18em]',
                light ? 'text-white/75' : 'text-muted-foreground',
              )}
            >
              Republic of the Philippines
            </motion.p>
            <motion.p
              custom={1}
              variants={textVariants}
              initial="hidden"
              animate="show"
              className={cn(
                'font-bold leading-tight',
                compact ? 'text-base' : 'text-lg',
                light ? 'text-white' : 'text-foreground',
              )}
            >
              PESO Pila, Laguna
            </motion.p>
            <motion.p
              custom={2}
              variants={textVariants}
              initial="hidden"
              animate="show"
              className={cn(
                'text-sm font-semibold',
                light ? 'text-gov-gold' : 'text-primary',
              )}
            >
              JobBridge Employment System
            </motion.p>
          </>
        ) : (
          <>
            <p
              className={cn(
                'text-[10px] font-semibold uppercase tracking-[0.18em]',
                light ? 'text-white/75' : 'text-muted-foreground',
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
                'text-sm font-semibold',
                light ? 'text-gov-gold' : 'text-primary',
              )}
            >
              JobBridge Employment System
            </p>
          </>
        )}
      </div>
    </div>
  )
}
