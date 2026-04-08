import { useState, useEffect, type ReactNode } from 'react';
import { ArrowLeft, Settings, Zap, Flame, Target, TrendingUp, Brain, Sparkles, Heart, Clock, Calendar, BarChart3 } from 'lucide-react';
import { motion } from 'motion/react';
import { getCategoryStyle } from './categories';
import {
  getAllSessions,
  initDatabase,
  isSessionFromToday,
  subscribeToSessionChanges,
  type Session,
} from '../lib/database';

const MOCK_SESSIONS: Session[] = [
  { id: '1', categoryId: 'deep-work', title: 'Deep Work', date: 'Today', time: '10:30 AM', duration: 60 },
  { id: '2', categoryId: 'deep-work', title: 'Focus Sprint', date: 'Today', time: '2:00 PM', duration: 45 },
  { id: '3', categoryId: 'meditation', title: 'Mindfulness', date: 'Today', time: '8:00 AM', duration: 15 },
  { id: '4', categoryId: 'meditation', title: 'Evening Calm', date: 'Yesterday', time: '8:30 PM', duration: 20 },
  { id: '5', categoryId: 'gratitude', title: 'Gratitude', date: 'Yesterday', time: '9:00 PM', duration: 10 },
  { id: '6', categoryId: 'deep-work', title: 'Morning Focus', date: 'Yesterday', time: '11:00 AM', duration: 55 },
  { id: '7', categoryId: 'deep-work', title: 'Architecture', date: 'Mar 13', time: '9:00 AM', duration: 90 },
  { id: '8', categoryId: 'gratitude', title: 'Morning Thanks', date: 'Mar 13', time: '7:30 AM', duration: 5 },
];

function StatCard({ 
  label, 
  value, 
  icon, 
  colorClass,
  bgColor 
}: { 
  label: string; 
  value: string; 
  icon: ReactNode; 
  colorClass: string;
  bgColor?: string;
}) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-6 rounded-3xl flex flex-col justify-between ${bgColor || 'bg-white'}`}
    >
      <div className={`${colorClass} font-bold uppercase tracking-widest text-xs mb-4`}>
        {label}
      </div>
      <div className="flex items-center gap-3">
        {icon}
        <div className="text-4xl font-black tracking-tighter text-[#171c22]">
          {value}
        </div>
      </div>
    </motion.div>
  );
}

function CategoryBreakdown({ 
  categoryId, 
  sessions, 
  totalDuration 
}: { 
  categoryId: string; 
  sessions: number; 
  totalDuration: number;
}) {
  const category = getCategoryStyle(categoryId);
  
  return (
    <div className="flex items-center justify-between p-6 bg-[#f0f4fc] rounded-2xl">
      <div className="flex items-center gap-4">
        <div className={`w-16 h-16 ${category.bgColor} rounded-xl flex items-center justify-center text-white`}>
          {category.icon}
        </div>
        <div>
          <p className="text-2xl font-black text-[#171c22]">{sessions} Sessions</p>
          <p className={`font-bold uppercase tracking-widest text-xs ${category.color}`}>
            {category.name}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className={`text-xl font-bold ${category.color}`}>
          {Math.floor(totalDuration / 60)}h {totalDuration % 60}m
        </p>
      </div>
    </div>
  );
}

function DailyRhythmBar({ sessions }: { sessions: Session[] }) {
  const hours = ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'];
  
  const getHeightForHour = (hour: string) => {
    const hourSessions = sessions.filter(s => {
      const timeHour = parseInt(s.time);
      return s.time.includes(hour) || (s.time.includes('AM') && hour === '9am');
    });
    if (hourSessions.length === 0) return 'h-2';
    const maxDuration = Math.max(...hourSessions.map(s => s.duration));
    if (maxDuration >= 60) return 'h-full';
    if (maxDuration >= 45) return 'h-4/5';
    if (maxDuration >= 30) return 'h-3/5';
    if (maxDuration >= 15) return 'h-2/5';
    return 'h-1/5';
  };

  const getColorForHour = (hour: string) => {
    const hourSessions = sessions.filter(s => s.time.includes(hour));
    if (hourSessions.length === 0) return 'bg-[#dee3eb] opacity-40';
    const mainCategory = hourSessions[0].categoryId;
    const category = getCategoryStyle(mainCategory);
    return category.bgColor;
  };

  return (
    <div className="flex-grow flex items-end gap-2 h-48 mb-8">
      {hours.map((hour, i) => (
        <div key={hour} className="flex-1 flex flex-col items-center gap-2">
          <div 
            className={`w-full ${getHeightForHour(hour)} ${getColorForHour(hour)} rounded-t-2xl transition-all hover:opacity-100`}
            title={hour}
          />
          <span className="text-[10px] font-bold text-[#727785]">{hour}</span>
        </div>
      ))}
    </div>
  );
}

export default function StatsView() {
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    async function loadSessions() {
      try {
        await initDatabase();
        const dbSessions = await getAllSessions();
        setSessions(dbSessions.length > 0 ? dbSessions : MOCK_SESSIONS);
      } catch (e) {
        setSessions(MOCK_SESSIONS);
      }
    }

    loadSessions();
    return subscribeToSessionChanges(loadSessions);
  }, []);
  
  const todaySessions = sessions.filter(isSessionFromToday);
  const totalMinutes = sessions.reduce((sum, s) => sum + s.duration, 0);
  const totalHours = Math.floor(totalMinutes / 60);
  const totalMins = totalMinutes % 60;
  
  const categoryBreakdown = todaySessions.reduce((acc, session) => {
    if (!acc[session.categoryId]) {
      acc[session.categoryId] = { sessions: 0, duration: 0 };
    }
    acc[session.categoryId].sessions += 1;
    acc[session.categoryId].duration += session.duration;
    return acc;
  }, {} as Record<string, { sessions: number; duration: number }>);
  const categoryEntries = Object.entries(categoryBreakdown) as Array<
    [string, { sessions: number; duration: number }]
  >;

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

      <main className="pt-8 px-6 max-w-7xl mx-auto">
        <section className="mb-12">
          <h2 className="text-5xl md:text-7xl font-black tracking-tight mb-4">Statistics</h2>
          <p className="text-xl text-[#424753] font-medium max-w-2xl">
            Your cognitive pulse. Intentionality measured through deep work and restorative pauses.
          </p>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-12">
          <div className="md:col-span-8 bg-[#f0f4fc] rounded-3xl p-8 flex flex-col justify-between min-h-[400px]">
            <div className="flex justify-between items-start mb-8">
              <div>
                <h3 className="text-3xl font-bold tracking-tight">Daily Rhythm</h3>
                <p className="text-[#424753] font-semibold">Pulse of Work vs. Rest</p>
              </div>
              <TrendingUp className="w-10 h-10 text-[#0051ae]" />
            </div>
            <DailyRhythmBar sessions={todaySessions} />
            <div className="flex flex-wrap gap-6 border-t border-[#c2c6d6]/15 pt-6">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-[#0969da]"></span>
                <span className="font-bold uppercase tracking-widest text-xs">Deep Work</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-[#2e7a5f]"></span>
                <span className="font-bold uppercase tracking-widest text-xs">Meditation</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-[#fd8a42]"></span>
                <span className="font-bold uppercase tracking-widest text-xs">Gratitude</span>
              </div>
            </div>
          </div>

          <div className="md:col-span-4 bg-[#0051ae] text-white rounded-3xl p-8 flex flex-col justify-between relative overflow-hidden">
            <div className="z-10">
              <h3 className="text-xl font-bold uppercase tracking-widest opacity-80 mb-2">Focus Streak</h3>
              <div className="text-[8rem] font-black leading-none tracking-tighter">12</div>
              <p className="text-2xl font-bold">Days in Flow</p>
            </div>
            <div className="z-10 mt-8 flex items-center gap-2">
              <Flame className="w-6 h-6" />
              <span className="font-semibold text-lg">Top 5% of all focusers</span>
            </div>
            <div className="absolute -right-16 -bottom-16 w-64 h-64 bg-[#0969da] rounded-full opacity-50"></div>
          </div>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard 
            label="Total Time"
            value={`${totalHours}h ${totalMins}m`}
            icon={<Clock className="w-8 h-8 text-[#0051ae]" />}
            colorClass="text-[#0051ae]"
            bgColor="bg-white"
          />
          <StatCard 
            label="This Week"
            value="24h 15m"
            icon={<BarChart3 className="w-8 h-8 text-[#0a6148]" />}
            colorClass="text-[#0a6148]"
            bgColor="bg-white"
          />
          <StatCard 
            label="Daily Goal"
            value="85%"
            icon={<Target className="w-8 h-8 text-[#9b4500]" />}
            colorClass="text-[#9b4500]"
            bgColor="bg-white"
          />
        </section>

        <section className="mb-12">
          <h3 className="text-3xl font-bold tracking-tight mb-8">Today's Steeps</h3>
          <div className="space-y-4">
            {categoryEntries.map(([categoryId, data]) => (
              <div key={categoryId}>
                <CategoryBreakdown
                  categoryId={categoryId}
                  sessions={data.sessions}
                  totalDuration={data.duration}
                />
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
