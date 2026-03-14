import { useState } from "react";
import Plasma from './Plasma';

export default function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setError(null);

    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(isLogin ? "/api/auth/login" : "/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.message || "Something went wrong.");
        return;
      }

      localStorage.setItem('userEmail', email);
      onLogin(data.access_token);
    } catch (err) {
      setError("Could not connect to server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-4 gap-8"
      style={{ position: 'relative', background: isLogin ? '#030810' : '#030d0d', transition: 'background 1.5s ease' }}
    >
      {/* <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        <Plasma color="#075985" speed={0.6} direction="forward" scale={1.1} opacity={0.5} mouseInteractive={true} />
      </div> */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        <Plasma color={isLogin ? "#0e7490" : "#0d7a6e"} speed={0.5} direction="alternate" scale={1.4} opacity={0.5} mouseInteractive={false} />
      </div>
      {/* <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
        <Plasma color="#0f766e" speed={0.4} direction="reverse" scale={1.7} opacity={0.35} mouseInteractive={true} />
      </div> */}

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem', width: '100%' }}>

        {/* Logo + Title */}
        <div className="flex items-center justify-center gap-2">
          <img src="/logo.svg" className="w-20 h-20 drop-shadow-lg" />
          <h1
            className="text-6xl sm:text-7xl bg-gradient-to-r from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent"
            style={{ fontFamily: "'Outfit', sans-serif", filter: 'drop-shadow(0 0 24px rgba(34,211,238,0.35))' }}
          >
            AiMD
          </h1>
        </div>

        {/* Card */}
        <div
          className="w-full max-w-md rounded-3xl p-8 flex flex-col gap-6"
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)',
          }}
        >
          {/* Toggle */}
          <div
            className="relative flex items-center p-1 rounded-2xl"
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
            }}
          >
            <div
              className={`absolute inset-y-1 w-[calc(50%-4px)] rounded-xl transition-all duration-300 ${
                isLogin
                  ? "left-1 bg-gradient-to-r from-sky-500/80 to-cyan-500/80"
                  : "left-[calc(50%+3px)] bg-gradient-to-r from-emerald-500/80 to-teal-600/80"
              }`}
              style={{ backdropFilter: 'blur(8px)', boxShadow: '0 2px 12px rgba(0,0,0,0.3)' }}
            />
            <button
              onClick={() => { setIsLogin(true); setError(null); }}
              className={`relative z-10 w-1/2 py-2 rounded-xl text-sm font-semibold transition-colors duration-200
                ${isLogin ? "text-white" : "text-white/50 hover:text-white/80"}`}
            >
              Login
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(null); }}
              className={`relative z-10 w-1/2 py-2 rounded-xl text-sm font-semibold transition-colors duration-200
                ${!isLogin ? "text-white" : "text-white/50 hover:text-white/80"}`}
            >
              Register
            </button>
          </div>

          {/* Fields */}
          <div className="flex flex-col gap-3">
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKeyPress}
              className="px-4 py-3 rounded-2xl text-white placeholder-white/40 focus:outline-none transition duration-300"
              style={{
                background: 'rgba(255,255,255,0.07)',
                border: '1px solid rgba(255,255,255,0.12)',
                backdropFilter: 'blur(8px)',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08)',
              }}
              onFocus={e => e.target.style.border = '1px solid rgba(34,211,238,0.5)'}
              onBlur={e => e.target.style.border = '1px solid rgba(255,255,255,0.12)'}
            />
            <input
              type="password"
              id="password"
              name="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyPress}
              className="px-4 py-3 rounded-2xl text-white placeholder-white/40 focus:outline-none transition duration-300"
              style={{
                background: 'rgba(255,255,255,0.07)',
                border: '1px solid rgba(255,255,255,0.12)',
                backdropFilter: 'blur(8px)',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08)',
              }}
              onFocus={e => e.target.style.border = '1px solid rgba(34,211,238,0.5)'}
              onBlur={e => e.target.style.border = '1px solid rgba(255,255,255,0.12)'}
            />
            {!isLogin && (
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onKeyDown={handleKeyPress}
                className="px-4 py-3 rounded-2xl text-white placeholder-white/40 focus:outline-none transition duration-300"
                style={{
                  background: 'rgba(255,255,255,0.07)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  backdropFilter: 'blur(8px)',
                  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08)',
                }}
                onFocus={e => e.target.style.border = '1px solid rgba(34,211,238,0.5)'}
                onBlur={e => e.target.style.border = '1px solid rgba(255,255,255,0.12)'}
              />
            )}
          </div>

          {/* Error */}
          {error && (
            <div
              className="text-red-300 text-sm text-center rounded-xl px-4 py-2"
              style={{
                background: 'rgba(248,113,113,0.1)',
                border: '1px solid rgba(248,113,113,0.25)',
                backdropFilter: 'blur(8px)',
              }}
            >
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full py-3 font-semibold text-white rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: isLogin
                ? 'linear-gradient(135deg, rgba(14,165,233,0.7), rgba(6,182,212,0.7))'
                : 'linear-gradient(135deg, rgba(16,185,129,0.8), rgba(13,148,136,0.8))',
              border: isLogin ? '1px solid rgba(34,211,238,0.3)' : '1px solid rgba(20,184,166,0.3)',
              backdropFilter: 'blur(8px)',
              boxShadow: isLogin
                ? '0 4px 20px rgba(6,182,212,0.25), inset 0 1px 0 rgba(255,255,255,0.15)'
                : '0 4px 20px rgba(16,185,129,0.25), inset 0 1px 0 rgba(255,255,255,0.15)',
            }}
            onMouseEnter={e => !isLoading && (e.currentTarget.style.boxShadow = isLogin ? '0 4px 28px rgba(6,182,212,0.45), inset 0 1px 0 rgba(255,255,255,0.2)' : '0 4px 28px rgba(16,185,129,0.45), inset 0 1px 0 rgba(255,255,255,0.2)')}
            onMouseLeave={e => e.currentTarget.style.boxShadow = isLogin ? '0 4px 20px rgba(6,182,212,0.25), inset 0 1px 0 rgba(255,255,255,0.15)' : '0 4px 20px rgba(16,185,129,0.25), inset 0 1px 0 rgba(255,255,255,0.15)'}
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div>
                {isLogin ? "Logging in..." : "Registering..."}
              </div>
            ) : (isLogin ? "Login" : "Register")}
          </button>
        </div>
      </div>
    </div>
  );
}