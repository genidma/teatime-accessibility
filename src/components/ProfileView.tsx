import React, { useState } from 'react';
import { ArrowLeft, Settings, Zap, User, Clock, Flame, Target, Calendar, Bell, Moon, Palette, Shield, HelpCircle, LogOut, Mail, Lock, AlertCircle, Loader2, Download } from 'lucide-react';
import { motion } from 'motion/react';
import { useAuth } from '../hooks/useAuth';
import { exportDataToCsv } from '../lib/database';

function SettingItem({ 
  icon: Icon, 
  label, 
  value,
  onClick 
}: { 
  icon: any; 
  label: string; 
  value?: string;
  onClick?: () => void;
}) {
  return (
    <button 
      onClick={onClick}
      className="w-full flex items-center justify-between p-4 bg-white rounded-xl hover:bg-[#f0f4fc] transition-colors"
    >
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-[#f0f4fc] rounded-lg flex items-center justify-center">
          <Icon className="w-5 h-5 text-[#424753]" />
        </div>
        <span className="font-medium text-[#171c22]">{label}</span>
      </div>
      {value && (
        <span className="text-[#424753]">{value}</span>
      )}
    </button>
  );
}

function ProfileHeader({ email }: { email: string | null }) {
  return (
    <div className="bg-gradient-to-br from-[#0051ae] to-[#0969da] rounded-3xl p-8 text-white mb-8">
      <div className="flex items-center gap-6">
        <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center shrink-0">
          <User className="w-12 h-12 text-white" />
        </div>
        <div className="overflow-hidden">
          <h2 className="text-2xl font-black truncate">{email || 'Focus Practitioner'}</h2>
          <p className="opacity-80">Building discipline daily</p>
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5" />
              <span className="font-bold">12 day streak</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              <span className="font-bold">48h this week</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white p-4 rounded-xl text-center">
      <div className="text-2xl font-black text-[#171c22]">{value}</div>
      <div className="text-xs font-bold uppercase tracking-widest text-[#424753]">{label}</div>
    </div>
  );
}

function AuthForm() {
  const { login, signup, error, setError, loading: authLoading } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    
    setIsSubmitting(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(email, password);
      }
    } catch (err) {
      // Error handled by hook
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-[#e4e8f0] max-w-sm mx-auto my-8">
      <div className="text-center mb-8 mt-2">
        <h2 className="text-2xl font-black text-[#171c22]">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="text-sm text-[#424753] mt-2 font-medium">
          {isLogin ? 'Sign in to sync your sessions globally' : 'Sign up to sync across all your devices'}
        </p>
      </div>

      {error && (
        <div className="bg-red-50/80 border border-red-100 text-red-600 p-4 rounded-2xl text-sm flex items-start gap-3 mb-6">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-[#424753] uppercase tracking-wider mb-2 ml-1">Email</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#88909f]" />
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#f0f4fc] border-2 border-transparent rounded-2xl py-3.5 pl-12 pr-4 text-[#171c22] focus:border-[#0969da] focus:bg-white outline-none transition-all font-medium placeholder:text-[#88909f]"
              placeholder="you@example.com"
            />
          </div>
        </div>

        <div>
           <label className="block text-xs font-bold text-[#424753] uppercase tracking-wider mb-2 ml-1">Password</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#88909f]" />
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#f0f4fc] border-2 border-transparent rounded-2xl py-3.5 pl-12 pr-4 text-[#171c22] focus:border-[#0969da] focus:bg-white outline-none transition-all font-medium placeholder:text-[#88909f]"
              placeholder="••••••••"
            />
          </div>
        </div>

        <button 
          type="submit"
          disabled={isSubmitting || authLoading}
          className="w-full bg-gradient-to-r from-[#0051ae] to-[#0969da] hover:opacity-90 text-white font-bold py-4 rounded-2xl transition-opacity mt-4 flex items-center justify-center gap-2 shadow-sm"
        >
          {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? 'Sign In' : 'Create Secure Account')}
        </button>
      </form>

      <div className="mt-8 text-center pb-2">
        <button 
          type="button"
          onClick={() => { setIsLogin(!isLogin); setError(null); }}
          className="text-sm font-bold text-[#0969da] hover:text-[#0051ae] transition-colors"
        >
          {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  );
}

export default function ProfileView() {
  const { user, loading, logout } = useAuth();

  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
            <Zap className="w-5 h-5 text-[#0051ae]" />
          </button>
          <h1 className="text-xl font-black tracking-tight">TeaTime</h1>
        </div>
        <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
          <Settings className="w-5 h-5 text-[#424753]" />
        </button>
      </header>

      <div className="h-1 w-full bg-[#f0f4fc]"></div>

      <main className="pt-8 px-6 max-w-2xl mx-auto">
        {loading ? (
          <div className="flex justify-center items-center py-24">
            <Loader2 className="w-10 h-10 animate-spin text-[#0969da]" />
          </div>
        ) : user ? (
          <>
            <ProfileHeader email={user.email} />

            <section className="mb-8">
              <div className="grid grid-cols-3 gap-4 mb-8">
                <StatBox label="Sessions" value="156" />
                <StatBox label="Total Hours" value="48h" />
                <StatBox label="Streak" value="12" />
              </div>
            </section>

            <section className="mb-8">
              <h3 className="text-lg font-black uppercase tracking-widest text-[#424753] mb-4">
                Preferences
              </h3>
              <div className="space-y-2">
                <SettingItem icon={Bell} label="Notifications" value="On" />
                <SettingItem icon={Moon} label="Dark Mode" value="Off" />
                <SettingItem icon={Palette} label="Theme" value="Light" />
                <SettingItem icon={Target} label="Daily Goal" value="4h" />
                <SettingItem icon={Calendar} label="Week Start" value="Monday" />
              </div>
            </section>

            <section className="mb-8">
              <h3 className="text-lg font-black uppercase tracking-widest text-[#424753] mb-4">
                Account
              </h3>
              <div className="space-y-2">
                <SettingItem icon={Shield} label="Privacy" />
                <SettingItem icon={HelpCircle} label="Help & Support" />
                <SettingItem 
                  icon={Download} 
                  label="Export Data (CSV)" 
                  onClick={exportDataToCsv}
                />
                <SettingItem 
                  icon={LogOut}  
                  label="Sign Out" 
                  onClick={async () => {
                    await logout();
                  }}
                />
              </div>
            </section>
          </>
        ) : (
          <AuthForm />
        )}

        <div className="text-center text-sm text-[#424753] pb-8 pt-8">
          <p>TeaTime v1.0.0</p>
          <p className="mt-1">Discipline equals freedom</p>
        </div>
      </main>
    </div>
  );
}
