import { useState } from "react";

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
    <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-teal-950
      flex flex-col items-center justify-center p-4 gap-8">

      <img src="/logo.svg" className="w-32 h-32" />
      <h1 className="text-6xl sm:text-7xl font-light bg-gradient-to-r
      from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
        AiMD
      </h1>

      <div className="w-full max-w-md bg-gradient-to-r from-gray-800/90 to-gray-700/90
        backdrop-blur-md border border-gray-600 rounded-3xl p-8 shadow-2xl flex flex-col gap-6">

        {/* Toggle */}
        <div className="relative flex items-center bg-gray-900/60 border border-gray-600 rounded-2xl p-1">
          <div className={`absolute inset-y-1 w-[calc(50%-4px)] rounded-xl transition-all duration-300
            ${isLogin
              ? "left-1 bg-gradient-to-r from-sky-500 to-cyan-500"
              : "left-[calc(50%+3px)] bg-gradient-to-r from-violet-500 to-purple-600"}`}
          />
          <button onClick={() => { setIsLogin(true); setError(null); }}
            className={`relative z-10 w-1/2 py-2 rounded-xl text-sm font-semibold transition-colors duration-200
              ${isLogin ? "text-white" : "text-gray-400 hover:text-white"}`}>
            Login
          </button>
          <button onClick={() => { setIsLogin(false); setError(null); }}
            className={`relative z-10 w-1/2 py-2 rounded-xl text-sm font-semibold transition-colors duration-200
              ${!isLogin ? "text-white" : "text-gray-400 hover:text-white"}`}>
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
            className="px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
              text-white placeholder-gray-400 focus:outline-none focus:ring-2
              focus:ring-sky-500 transition duration-300"
          />
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyPress}
            className="px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
              text-white placeholder-gray-400 focus:outline-none focus:ring-2
              focus:ring-sky-500 transition duration-300"
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
              className="px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
                text-white placeholder-gray-400 focus:outline-none focus:ring-2
                focus:ring-sky-500 transition duration-300"
            />
          )}
        </div>

        {error && (
          <div className="text-red-400 text-sm text-center bg-red-400/10 border border-red-400/30
            rounded-xl px-4 py-2">
            {error}
          </div>
        )}

        <button onClick={handleSubmit} disabled={isLoading}
          className="w-full py-3 bg-gradient-to-r from-sky-500 to-cyan-500 hover:opacity-80
            text-white font-semibold rounded-2xl transition disabled:opacity-50 disabled:cursor-not-allowed">
          {isLoading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div>
              {isLogin ? "Logging in..." : "Registering..."}
            </div>
          ) : (isLogin ? "Login" : "Register")}
        </button>
      </div>
    </div>
  );
}