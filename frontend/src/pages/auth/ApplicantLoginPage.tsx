import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ApplicantLoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginAsApplicant } = useAuth();
  const [email, setEmail] = useState('alex.mercer@apextech.com');
  const [password, setPassword] = useState('password');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setLoginError(null);
    try {
      await loginAsApplicant(email, password);
      navigate('/applicant/dashboard');
    } catch (err: any) {
      setLoginError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 text-on-surface">
      <div className="w-full max-w-md bg-surface border border-border-subtle rounded-xl p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-border-subtle pb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-[#2563EB] flex items-center justify-center font-bold text-white shadow-sm">
              AT
            </div>
            <div>
              <h2 className="font-display font-bold text-lg text-on-surface">Applicant Portal Login</h2>
              <p className="text-xs text-on-surface-variant">Commercial Credit & Loan Applications</p>
            </div>
          </div>
          <span className="text-[10px] font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-1 rounded font-medium">
            SSL 256-BIT
          </span>
        </div>

        {loginError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-md text-xs flex items-center gap-2">
            <span className="material-symbols-outlined text-base text-rose-600">error</span>
            <span>{loginError}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-on-surface uppercase tracking-wider mb-1">
              Corporate Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-surface-bright border border-border-subtle rounded-md text-sm text-on-surface focus:outline-none focus:border-[#2563EB]"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-semibold text-on-surface uppercase tracking-wider">
                Password
              </label>
              <a href="#forgot" className="text-xs text-[#2563EB] hover:underline">Forgot password?</a>
            </div>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 pr-9 bg-surface-bright border border-border-subtle rounded-md text-sm text-on-surface focus:outline-none focus:border-[#2563EB]"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2.5 top-2.5 text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined text-[16px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 bg-[#2563EB] hover:bg-blue-600 disabled:opacity-60 text-white rounded-md font-medium text-sm transition-colors flex items-center justify-center gap-2 shadow-xs"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Signing In...</span>
              </>
            ) : (
              <>
                <span>Sign In to Applicant Dashboard</span>
                <span className="material-symbols-outlined text-base">arrow_forward</span>
              </>
            )}
          </button>
        </form>

        <div className="pt-4 border-t border-border-subtle flex items-center justify-between text-xs text-on-surface-variant">
          <button onClick={() => navigate('/')} className="hover:text-on-surface flex items-center gap-1">
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back to Role Selection
          </button>
          <a href="#help" className="text-[#2563EB] hover:underline">Application Help</a>
        </div>
      </div>
    </div>
  );
};
