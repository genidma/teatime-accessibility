import { useState } from 'react';
import { ArrowLeft, Settings, Zap, User, Clock, Flame, Target, Calendar, Bell, Moon, Palette, Shield, HelpCircle, LogOut } from 'lucide-react';
import { motion } from 'motion/react';

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

function ProfileHeader() {
  return (
    <div className="bg-gradient-to-br from-[#0051ae] to-[#0969da] rounded-3xl p-8 text-white mb-8">
      <div className="flex items-center gap-6">
        <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
          <User className="w-12 h-12 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">Focus Practitioner</h2>
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

export default function ProfileView() {
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
        <ProfileHeader />

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
            <SettingItem 
              icon={Bell} 
              label="Notifications" 
              value="On"
            />
            <SettingItem 
              icon={Moon} 
              label="Dark Mode" 
              value="Off"
            />
            <SettingItem 
              icon={Palette} 
              label="Theme" 
              value="Light"
            />
            <SettingItem 
              icon={Target} 
              label="Daily Goal" 
              value="4h"
            />
            <SettingItem 
              icon={Calendar} 
              label="Week Start" 
              value="Monday"
            />
          </div>
        </section>

        <section className="mb-8">
          <h3 className="text-lg font-black uppercase tracking-widest text-[#424753] mb-4">
            Account
          </h3>
          <div className="space-y-2">
            <SettingItem 
              icon={Shield} 
              label="Privacy" 
            />
            <SettingItem 
              icon={HelpCircle} 
              label="Help & Support" 
            />
            <SettingItem 
              icon={LogOut} 
              label="Sign Out" 
            />
          </div>
        </section>

        <div className="text-center text-sm text-[#424753] pb-8">
          <p>TeaTime v1.0.0</p>
          <p className="mt-1">Discipline equals freedom</p>
        </div>
      </main>
    </div>
  );
}
