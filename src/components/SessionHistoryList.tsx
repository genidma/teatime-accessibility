import { useState } from 'react';
import { ArrowLeft, Settings, Zap, Flame, Target } from 'lucide-react';
import { motion } from 'motion/react';
import { getCategoryStyle, type CategoryStyle } from './categories';

export type Session = {
  id: string;
  categoryId: string;
  title: string;
  date: string;
  time: string;
  duration: number;
  notes?: string;
};

const MOCK_SESSIONS: Session[] = [
  {
    id: '1',
    categoryId: 'deep-work',
    title: 'Deep Work',
    date: 'Today',
    time: '10:30 AM',
    duration: 60,
    notes: 'Focused on UI architecture and design system implementation.',
  },
  {
    id: '2',
    categoryId: 'meditation',
    title: 'Mindfulness',
    date: 'Today',
    time: '8:00 AM',
    duration: 15,
    notes: 'Deep breathing and body scan for morning grounding.',
  },
  {
    id: '3',
    categoryId: 'gratitude',
    title: 'Gratitude',
    date: 'Yesterday',
    time: '9:00 PM',
    duration: 10,
    notes: 'Reflected on what I am grateful for today.',
  },
  {
    id: '4',
    categoryId: 'deep-work',
    title: 'Focus Sprint',
    date: 'Yesterday',
    time: '2:00 PM',
    duration: 45,
    notes: 'Working on React components integration.',
  },
  {
    id: '5',
    categoryId: 'meditation',
    title: 'Evening Calm',
    date: 'Mar 13',
    time: '8:30 PM',
    duration: 20,
    notes: 'Wind down meditation before bed.',
  },
  {
    id: '6',
    categoryId: 'gratitude',
    title: 'Morning Thanks',
    date: 'Mar 13',
    time: '7:30 AM',
    duration: 5,
    notes: 'Quick gratitude before starting the day.',
  },
];

type SessionCardProps = {
  session: Session;
  onClick?: () => void;
};

function SessionCard({ session, onClick }: SessionCardProps) {
  const category = getCategoryStyle(session.categoryId);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className="group bg-white p-6 rounded-xl flex items-center justify-between transition-all duration-300 hover:bg-[#f0f4fc] active:scale-[0.98] cursor-pointer"
    >
      <div className="flex items-center gap-6">
        <div className={`w-16 h-16 ${category.bgColor} rounded-2xl flex items-center justify-center text-white shadow-lg`}>
          {category.icon}
        </div>
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h3 className="text-2xl font-bold tracking-tight text-[#171c22] leading-none">
              {session.title}
            </h3>
            <span className={`${category.bgColor}/10 ${category.color} text-[10px] font-black px-2 py-1 rounded uppercase tracking-tighter`}>
              {category.label}
            </span>
          </div>
          <p className="text-[#424753] text-sm font-medium">
            {session.date} • {session.time}
          </p>
          {session.notes && (
            <p className="text-[#424753] text-sm mt-2 italic max-w-md line-clamp-1">
              {session.notes}
            </p>
          )}
        </div>
      </div>
      <div className="hidden md:block text-right">
        <span className="text-xl font-black text-[#171c22]">
          {session.duration} min
        </span>
        <p className="text-[10px] font-black text-[#727785] uppercase tracking-widest">
          Duration
        </p>
      </div>
    </motion.div>
  );
}

function WeeklySummaryCard({ 
  label, 
  value, 
  icon, 
  colorClass 
}: { 
  label: string; 
  value: string; 
  icon: React.ReactNode; 
  colorClass: string;
}) {
  return (
    <div className="bg-[#f0f4fc] p-6 rounded-xl flex flex-col justify-between aspect-square md:aspect-auto">
      <div className={`${colorClass} font-bold uppercase tracking-widest text-xs mb-4`}>
        {label}
      </div>
      <div className="flex items-center gap-3">
        {icon}
        <div className="text-4xl font-black tracking-tighter text-[#171c22]">
          {value}
        </div>
      </div>
    </div>
  );
}

type SessionHistoryListProps = {
  onBack?: () => void;
};

export default function SessionHistoryList({ onBack }: SessionHistoryListProps) {
  const [sessions] = useState<Session[]>(MOCK_SESSIONS);

  const groupedSessions = sessions.reduce((acc, session) => {
    if (!acc[session.date]) {
      acc[session.date] = [];
    }
    acc[session.date].push(session);
    return acc;
  }, {} as Record<string, Session[]>);

  const dates = Object.keys(groupedSessions);
  const totalMinutes = sessions.reduce((sum, s) => sum + s.duration, 0);
  const hours = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;

  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {onBack ? (
            <button 
              onClick={onBack}
              className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-[#0051ae]" />
            </button>
          ) : (
            <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
              <Zap className="w-5 h-5 text-[#0051ae]" />
            </button>
          )}
          <h1 className="text-xl font-black tracking-tight">TeaTime</h1>
        </div>
        <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
          <Settings className="w-5 h-5 text-[#424753]" />
        </button>
      </header>

      <div className="h-1 w-full bg-[#f0f4fc]"></div>

      <main className="pt-8 px-6 max-w-4xl mx-auto">
        <div className="mb-12">
          <h2 className="text-5xl font-extrabold tracking-tight text-[#171c22] mb-2">
            Your Steeps
          </h2>
          <p className="text-[#424753] font-medium">
            intentional moments to structure.
          </p>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <WeeklySummaryCard 
            label="Total Time"
            value={`${hours}h ${mins}m`}
            icon={<Zap className="w-8 h-8 text-[#0051ae]" />}
            colorClass="text-[#0051ae]"
          />
          <WeeklySummaryCard 
            label="Streaks"
            value="12 Days"
            icon={<Flame className="w-8 h-8 text-[#0a6148]" />}
            colorClass="text-[#0a6148]"
          />
          <WeeklySummaryCard 
            label="Daily Goal"
            value="85%"
            icon={<Target className="w-8 h-8 text-[#9b4500]" />}
            colorClass="text-[#9b4500]"
          />
        </section>

        <div className="space-y-8">
          {dates.map((date) => (
            <div key={date} className="space-y-4">
              <h3 className="text-lg font-black tracking-tight text-[#424753] uppercase">
                {date}
              </h3>
              <div className="space-y-3">
                {groupedSessions[date].map((session) => (
                  <SessionCard 
                    key={session.id} 
                    session={session}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
