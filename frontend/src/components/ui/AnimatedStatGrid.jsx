import { motion } from 'framer-motion'
import { staggerContainer, staggerItem } from '@/components/common/PageMotion'
import { cn } from '@/utils/cn'

/** Stat card grid with staggered fade-in animation */
export default function AnimatedStatGrid({ children, className }) {
  return (
    <motion.div
      className={cn('stat-grid', className)}
      variants={staggerContainer}
      initial="hidden"
      animate="show"
    >
      {Array.isArray(children)
        ? children.map((child, i) => (
            <motion.div key={child.key ?? i} variants={staggerItem}>
              {child}
            </motion.div>
          ))
        : children}
    </motion.div>
  )
}
