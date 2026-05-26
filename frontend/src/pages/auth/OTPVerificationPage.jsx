import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import toast from 'react-hot-toast'
import AuthLayout from '@/components/common/AuthLayout'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import { verifyOtp, resendOtp } from '@/api/authApi'

function OTPVerificationPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState(location.state?.email || '')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)

  useEffect(() => {
    if (countdown <= 0) return
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000)
    return () => clearTimeout(t)
  }, [countdown])

  const handleVerify = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await verifyOtp(email.trim().toLowerCase(), otp.trim())
      if (!res.success) {
        toast.error(res.message || 'Verification failed')
        return
      }
      toast.success('Email verified. You may now sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (countdown > 0) return
    try {
      await resendOtp(email.trim().toLowerCase(), 'registration')
      toast.success('A new code has been sent')
      setCountdown(60)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Could not resend code')
    }
  }

  return (
    <AuthLayout
      title="Verify your email"
      subtitle="Enter the 6-digit verification code sent to your email address. Codes expire in 10 minutes."
      footer={
        <Link to="/login" className="font-semibold text-primary hover:underline">
          Back to sign in
        </Link>
      }
    >
      <form onSubmit={handleVerify} className="form-stack">
        <div>
          <Label htmlFor="email" required>
            Email address
          </Label>
          <Input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="otp" required>
            Verification code
          </Label>
          <Input
            id="otp"
            inputMode="numeric"
            maxLength={6}
            required
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            className="text-center text-xl tracking-[0.4em] font-semibold"
          />
        </div>
        <Button type="submit" className="w-full" size="lg" disabled={loading}>
          {loading ? 'Verifying…' : 'Verify email'}
        </Button>
        <Button
          type="button"
          variant="ghost"
          className="w-full"
          disabled={countdown > 0}
          onClick={handleResend}
        >
          {countdown > 0 ? `Resend code in ${countdown}s` : 'Resend verification code'}
        </Button>
      </form>
    </AuthLayout>
  )
}

export default OTPVerificationPage
