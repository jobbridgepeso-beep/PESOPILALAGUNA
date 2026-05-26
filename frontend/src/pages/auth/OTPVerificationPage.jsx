import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import toast from 'react-hot-toast'
import AuthLayout from '@/components/common/AuthLayout'
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
      toast.success('Email verified! You can now sign in.')
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
      toast.success('New code sent')
      setCountdown(60)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Could not resend code')
    }
  }

  return (
    <AuthLayout title="Verify email" subtitle="Enter the 6-digit code we sent you">
      <form onSubmit={handleVerify} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">OTP code</label>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            required
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-center text-lg tracking-widest"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-600 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? 'Verifying…' : 'Verify'}
        </button>
      </form>
      <button
        type="button"
        onClick={handleResend}
        disabled={countdown > 0}
        className="mt-3 w-full text-sm text-blue-600 hover:underline disabled:text-slate-400"
      >
        {countdown > 0 ? `Resend in ${countdown}s` : 'Resend code'}
      </button>
      <p className="mt-4 text-center text-sm">
        <Link to="/login" className="text-slate-600 hover:underline">
          Back to login
        </Link>
      </p>
    </AuthLayout>
  )
}

export default OTPVerificationPage
