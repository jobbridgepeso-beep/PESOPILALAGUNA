import { z } from 'zod'

// ── Shared field schemas ─────────────────────────────────────────────────────

export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Enter a valid email address')

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')

export const otpSchema = z
  .string()
  .length(6, 'OTP must be exactly 6 digits')
  .regex(/^\d{6}$/, 'OTP must contain only digits')

// ── Auth form schemas ────────────────────────────────────────────────────────

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
})

export const registerSchema = z
  .object({
    role: z.enum(['jobseeker', 'employer'], {
      required_error: 'Please select a role',
    }),
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

export const forgotPasswordSchema = z.object({
  email: emailSchema,
})

export const resetPasswordSchema = z
  .object({
    otp: otpSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

// ── File validation ──────────────────────────────────────────────────────────

/** Accepted MIME types for all upload endpoints (Requirement 19.1) */
export const ACCEPTED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf']

/** Maximum file size: 5 MB (Requirement 19.2) */
export const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

/**
 * Validate a File object against JobBridge upload rules.
 * @param {File} file
 * @returns {{ valid: boolean, error: string | null }}
 */
export const validateUploadFile = (file) => {
  if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
    return { valid: false, error: 'Only JPG, PNG, and PDF files are accepted.' }
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return { valid: false, error: 'File exceeds the 5 MB size limit.' }
  }
  return { valid: true, error: null }
}
