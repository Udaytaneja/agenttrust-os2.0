import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const BankerLoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginAsBanker } = useAuth();
  const [employeeId, setEmployeeId] = useState('BKR-7749-NY');
  const [password, setPassword] = useState('password');
  const [tokenCode, setTokenCode] = useState('894 201');
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setLoginError(null);
    try {
      await loginAsBanker(employeeId, password);
      navigate('/banker/dashboard');
    } catch (err: any) {
      setLoginError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center p-4 text-white">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-[#2563EB] flex items-center justify-center font-bold text-white shadow-sm">
              AT
            </div>
            <div>
              <h2 className="font-display font-bold text-lg text-white">Banker Authentication</h2>
              <p className="text-xs text-slate-400">Institutional Risk Portal</p>
            </div>
          </div>
          <span className="text-[10px] font-mono bg-emerald-950 text-emerald-400 px-2 py-1 rounded border border-emerald-800">
            FIPS 140-3
          </span>
        </div>

        {loginError && (
          <div className="p-3 bg-rose-950/80 border border-rose-800 text-rose-300 rounded-md text-xs flex items-center gap-2">
            <span className="material-symbols-outlined text-base text-rose-400">error</span>
            <span>{loginError}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Institutional Employee ID
            </label>
            <input
              type="text"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-md text-sm text-white focus:outline-none focus:border-[#2563EB] font-mono"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-md text-sm text-white focus:outline-none focus:border-[#2563EB]"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Hardware Token / TOTP 2FA
              </label>
              <span className="text-[11px] text-[#2563EB] cursor-pointer hover:underline">Use YubiKey</span>
            </div>
            <input
              type="text"
              value={tokenCode}
              onChange={(e) => setTokenCode(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-md text-sm text-white focus:outline-none focus:border-[#2563EB] font-mono tracking-widest text-center"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 bg-[#2563EB] hover:bg-blue-600 disabled:opacity-60 text-white rounded-md font-medium text-sm transition-colors flex items-center justify-center gap-2 shadow-sm"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <span>Authenticate & Access Command Center</span>
                <span className="material-symbols-outlined text-base">arrow_forward</span>
              </>
            )}
          </button>
        </form>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <button onClick={() => navigate('/')} className="hover:text-white flex items-center gap-1">
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back to Role Selection
          </button>
          <span className="font-mono text-[10px]">Session Timeout: 15m</span>
        </div>
      </div>
    </div>
  );
};
