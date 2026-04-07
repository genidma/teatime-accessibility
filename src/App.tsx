/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

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
  User 
} from 'lucide-react';
import { motion } from 'motion/react';

const BreakdownCard = ({ 
  icon: Icon, 
  title, 
  duration, 
  sessions, 
  percentage, 
  colorClass,
  progressColor
}: { 
  icon: any, 
  title: string, 
  duration: string, 
  sessions: string, 
  percentage: number,
  colorClass: string,
  progressColor: string
}) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group"
  >
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Icon className={`w-4 h-4 ${colorClass}`} />
        <span className={`text-[10px] font-bold uppercase tracking-widest ${colorClass}`}>
          {title}
        </span>
      </div>
      <h4 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
        {duration}
      </h4>
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
        {sessions}
      </p>
    </div>
    <div className="flex items-center gap-4 w-full md:w-auto">
      <div className="h-1.5 flex-1 md:w-32 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, delay: 0.5 }}
          className={`h-full ${progressColor}`}
        />
      </div>
      <span className="text-sm font-mono font-bold text-slate-600 dark:text-slate-300 w-8 text-right">
        {percentage}%
      </span>
    </div>
  </motion.div>
);

export default function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans pb-32">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md px-6 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-900">
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-full transition-colors">
            <ArrowLeft className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </button>
          <h1 className="text-xl font-bold tracking-tight text-blue-600 dark:text-blue-400">
            Duration Analysis
          </h1>
        </div>
        <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-full transition-colors">
          <Settings className="w-5 h-5 text-slate-500" />
        </button>
      </header>

      <main className="max-w-2xl mx-auto px-6 pt-8 space-y-8">
        {/* Focus Rhythm Score Card */}
        <motion.section 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-slate-50 dark:bg-slate-900/50 p-8 rounded-3xl space-y-6"
        >
          <div className="space-y-1">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
              Focus Rhythm Score
            </h2>
            <div className="flex items-baseline gap-3">
              <span className="text-7xl font-black tracking-tighter text-blue-600 dark:text-blue-500">
                84
              </span>
              <span className="text-lg font-bold text-emerald-600 dark:text-emerald-500">
                Optimal
              </span>
            </div>
          </div>
          <p className="text-lg leading-relaxed text-slate-600 dark:text-slate-400 max-w-sm">
            Your focus sessions are increasingly stable. Deep work segments are <span className="text-slate-900 dark:text-white font-semibold">15% longer</span> than your weekly average.
          </p>
        </motion.section>

        {/* Peak Flow Card */}
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="relative overflow-hidden bg-blue-600 rounded-3xl p-8 text-white group"
        >
          {/* Abstract Background Pattern */}
          <div className="absolute inset-0 opacity-20 pointer-events-none">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M0 100 C 20 0 50 0 100 100 Z" fill="currentColor" />
              <path d="M0 0 C 50 100 80 100 100 0 Z" fill="currentColor" />
            </svg>
          </div>
          
          <div className="relative z-10 flex flex-col items-center text-center space-y-2">
            <div className="bg-white/20 p-3 rounded-2xl backdrop-blur-sm mb-2">
              <Zap className="w-8 h-8 fill-white" />
            </div>
            <h3 className="text-2xl font-bold tracking-tight">Peak Flow</h3>
            <p className="text-blue-100 font-medium">10:15 AM - 11:45 AM</p>
          </div>
        </motion.section>

        {/* Daily Breakdown */}
        <section className="space-y-6">
          <h3 className="text-2xl font-bold tracking-tight px-1">Daily Breakdown</h3>
          <div className="grid gap-4">
            <BreakdownCard 
              icon={Timer}
              title="Short Bursts (< 1m)"
              duration="12m 40s"
              sessions="18 individual sessions today"
              percentage={15}
              colorClass="text-orange-600"
              progressColor="bg-orange-600"
            />
            <BreakdownCard 
              icon={Navigation}
              title="Focused Transitions (1m - 5m)"
              duration="45m 12s"
              sessions="12 transition tasks recorded"
              percentage={35}
              colorClass="text-emerald-600"
              progressColor="bg-emerald-600"
            />
            <BreakdownCard 
              icon={Brain}
              title="Deep Work (5m+)"
              duration="3h 15m"
              sessions="4 sustained flow blocks"
              percentage={50}
              colorClass="text-blue-600"
              progressColor="bg-blue-600"
            />
          </div>
        </section>

        {/* Split Activity Button */}
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold text-lg flex items-center justify-center gap-3 shadow-lg shadow-blue-600/20 transition-all"
        >
          <Split className="w-5 h-5" />
          Split Activity
        </motion.button>

        <p className="text-center text-sm font-medium text-slate-400 pb-8">
          Last synced: 2 minutes ago
        </p>
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-t border-slate-100 dark:border-slate-900 px-6 py-4 flex justify-between items-center z-50">
        <NavItem icon={Timer} label="Sessions" />
        <NavItem icon={BarChart3} label="Stats" active />
        <NavItem icon={TrendingUp} label="Trends" />
        <NavItem icon={User} label="Profile" />
      </nav>
    </div>
  );
}

function NavItem({ icon: Icon, label, active = false }: { icon: any, label: string, active?: boolean }) {
  return (
    <button className={`flex flex-col items-center gap-1.5 px-4 py-2 rounded-2xl transition-all ${active ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'}`}>
      <Icon className="w-5 h-5" />
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
    </button>
  );
}
