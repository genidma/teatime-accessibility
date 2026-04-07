/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import type { ReactNode } from 'react';
import { 
  ArrowLeft, 
  Settings, 
  Zap, 
  Timer, 
  Navigation, 
  Brain, 
  Split, 
  BarChart3, 
  TrendingUp, 
  User,
  Heart,
  BookOpen,
  Sparkles,
  Hourglass
} from 'lucide-react';
import { motion } from 'motion/react';

type FilterButtonProps = {
  label: string;
  active?: boolean;
  icon?: ReactNode;
};

function FilterButton({ label, active, icon }: FilterButtonProps) {
  return (
    <button className={`
      flex items-center gap-2 px-6 py-4 rounded-xl font-bold transition-all 
      hover:opacity-90 active:scale-95 whitespace-nowrap
      ${active 
        ? 'bg-[#0969da] text-white' 
        : 'bg-[#f0f4fc] text-[#171c22] hover:bg-[#e4e8f0]'
      }
    `}>
      {icon}
      <span>{label}</span>
    </button>
  );
}

type ActivityCardProps = {
  title: string;
  time: string;
  duration: string;
  sessionType: 'meditation' | 'deep-work' | 'gratitude';
};

function ActivityCard({ title, time, duration, sessionType }: ActivityCardProps) {
  const typeStyles = {
    meditation: {
      bg: 'bg-[#2e7a5f]',
      label: 'MEDITATION',
      icon: <Sparkles className="w-8 h-8 text-white" />,
    },
    'deep-work': {
      bg: 'bg-[#0969da]',
      label: 'DEEP WORK',
      icon: <BookOpen className="w-8 h-8 text-white" />,
    },
    gratitude: {
      bg: 'bg-[#fd8a42]',
      label: 'GRATITUDE',
      icon: <Heart className="w-8 h-8 text-white" />,
    },
  };

  const style = typeStyles[sessionType];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[#f0f4fc] rounded-xl p-6 flex items-center justify-between group transition-all hover:bg-[#e4e8f0]"
    >
      <div className="flex items-center gap-6">
        <div className={`w-16 h-16 ${style.bg} flex items-center justify-center rounded-xl shadow-lg`}>
          {style.icon}
        </div>
        <div>
          <h3 className="font-black text-xl leading-tight text-[#171c22]">
            {title}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="bg-[#dee3eb] px-2 py-0.5 rounded-sm text-[10px] font-black uppercase tracking-widest text-[#0a6148]">
              {style.label}
            </span>
            <span className="text-[#424753] text-sm font-semibold">{time}</span>
          </div>
        </div>
      </div>
      <div className="text-right">
        <div className="font-mono font-black text-2xl tracking-tighter text-[#171c22]">
          {duration}
        </div>
        <span className="text-[10px] font-black uppercase tracking-tighter text-[#424753]">Duration</span>
      </div>
    </motion.div>
  );
}

type BreakdownCardProps = {
  label: string;
  duration: string;
  sessions: string;
  percentage: number;
  colorClass: string;
};

function BreakdownCard({ label, duration, sessions, percentage, colorClass }: BreakdownCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[#f0f4fc] p-6 rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 group"
    >
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-bold uppercase tracking-widest ${colorClass}`}>
            {label}
          </span>
        </div>
        <h4 className="text-3xl font-black tracking-tight text-[#171c22]">
          {duration}
        </h4>
        <p className="text-sm font-medium text-[#424753]">
          {sessions}
        </p>
      </div>
      <div className="flex items-center gap-4 w-full md:w-auto">
        <div className="h-1.5 flex-1 md:w-32 bg-[#dee3eb] rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 1, delay: 0.5 }}
            className={`h-full ${colorClass.replace('text-', 'bg-')}`}
          />
        </div>
        <span className="text-sm font-mono font-bold text-[#424753] w-8 text-right">
          {percentage}%
        </span>
      </div>
    </motion.div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
            <ArrowLeft className="w-5 h-5 text-[#0051ae]" />
          </button>
          <h1 className="text-xl font-bold tracking-tight text-[#171c22]">
            Duration Analysis
          </h1>
        </div>
        <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
          <Settings className="w-5 h-5 text-[#424753]" />
        </button>
      </header>

      <div className="h-1 w-full bg-[#f0f4fc]"></div>

      <main className="max-w-2xl mx-auto px-6 pt-8 space-y-12">
        <section className="space-y-4">
          <span className="text-xs font-black uppercase tracking-[0.2em] text-[#424753]">
            Filter by Duration
          </span>
          <div className="flex gap-2 overflow-x-auto pb-2">
            <FilterButton label="All" active icon={<Zap className="w-5 h-5" />} />
            <FilterButton label="&lt; 1m" icon={<Timer className="w-5 h-5" />} />
            <FilterButton label="1 - 5m" icon={<Navigation className="w-5 h-5" />} />
            <FilterButton label="5m+" icon={<Hourglass className="w-5 h-5" />} />
          </div>
        </section>

        <section className="space-y-6">
          <div className="flex items-baseline justify-between border-b-2 border-[#e4e8f0] pb-2">
            <h2 className="text-2xl font-black tracking-tighter">Today</h2>
            <span className="text-[#424753] font-bold text-sm tracking-wide">APRIL 6</span>
          </div>

          <ActivityCard 
            title="Afternoon Stillness"
            time="14:20 PM"
            duration="12:45"
            sessionType="meditation"
          />
          <ActivityCard 
            title="Focus Sprint"
            time="11:05 AM"
            duration="04:12"
            sessionType="deep-work"
          />
          <ActivityCard 
            title="Quick Gratitude"
            time="21:45 PM"
            duration="00:45"
            sessionType="gratitude"
          />
          <ActivityCard 
            title="Project Architecture"
            time="09:00 AM"
            duration="125:00"
            sessionType="deep-work"
          />
        </section>

        <section className="grid grid-cols-2 gap-4">
          <div className="col-span-2 p-8 bg-[#171c22] rounded-xl text-white flex flex-col justify-between h-48">
            <div>
              <span className="text-[10px] uppercase tracking-[0.3em] opacity-60">
                Session Trend
              </span>
              <h4 className="text-3xl tracking-tight mt-2">Extended Focus is rising.</h4>
            </div>
            <div className="flex items-end justify-between">
              <p className="text-sm opacity-80 max-w-[200px]">
                You spent 12% more time in Deep Work sessions this week.
              </p>
              <TrendingUp className="w-12 h-12 opacity-40" />
            </div>
          </div>
        </section>

        <section className="space-y-6">
          <h3 className="text-2xl font-black tracking-tight px-1">Daily Breakdown</h3>
          <div className="grid gap-4">
            <BreakdownCard 
              label="Short Bursts (&lt; 1m)"
              duration="12m 40s"
              sessions="18 individual sessions today"
              percentage={15}
              colorClass="text-orange-600"
            />
            <BreakdownCard 
              label="Focused Transitions (1m - 5m)"
              duration="45m 12s"
              sessions="12 transition tasks recorded"
              percentage={35}
              colorClass="text-emerald-600"
            />
            <BreakdownCard 
              label="Deep Work (5m+)"
              duration="3h 15m"
              sessions="4 sustained flow blocks"
              percentage={50}
              colorClass="text-blue-600"
            />
          </div>
        </section>

        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-5 bg-[#0969da] hover:opacity-90 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-3 shadow-lg transition-all"
        >
          <Split className="w-5 h-5" />
          Split Activity
        </motion.button>

        <p className="text-center text-sm font-medium text-[#424753] pb-8">
          Last synced: 2 minutes ago
        </p>
      </main>

      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-3 bg-[#f7f9ff]/80 backdrop-blur-xl rounded-t-[0.75rem]" style={{ boxShadow: '0px 24px 48px rgba(23, 28, 34, 0.06)' }}>
        <NavItem icon={Timer} label="Sessions" />
        <NavItem icon={BarChart3} label="Stats" />
        <NavItem icon={TrendingUp} label="Trends" active />
        <NavItem icon={User} label="Profile" />
      </nav>

      <div className="fixed bottom-24 left-0 w-full px-6 pointer-events-none">
        <div className="h-3 w-full bg-[#e4e8f0] rounded-full overflow-hidden shadow-sm">
          <div className="h-full bg-gradient-to-r from-[#0051ae] via-[#0969da] to-[#0a6148] w-[65%]"></div>
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon: Icon, label, active = false }: { icon: any, label: string, active?: boolean }) {
  return (
    <button className={`
      flex flex-col items-center gap-1.5 px-4 py-2 rounded-2xl transition-all
      ${active 
        ? 'bg-[#0969da] text-white' 
        : 'text-[#424753] hover:bg-[#f0f4fc]'
      }
    `}>
      <Icon className="w-5 h-5" />
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
    </button>
  );
}
