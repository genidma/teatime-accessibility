import { useState, useEffect, useMemo } from 'react';
import { Timer, BarChart3, TrendingUp, User, Clock, Flame, Calendar, Target, Award } from 'lucide-react';
import ActiveSteepTimer, { DEFAULT_CATEGORIES } from './components/ActiveSteepTimer';
import SessionHistoryList from './components/SessionHistoryList';
import StatsView from './components/StatsView';
import ProfileView from './components/ProfileView';
import {
  getCategoryStats,
  getHeatmapData,
  getProductiveRange,
  getTodaySessions,
  getWeeklyActivity,
  initDatabase,
  subscribeToSessionChanges,
} from './lib/database';
import { 
  BarChart as RechartsBarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend 
} from 'recharts';

type View = 'timer' | 'sessions' | 'stats' | 'trends' | 'profile';

function NavItem({ 
  icon: Icon, 
  label, 
  active = false, 
  onClick 
}: { 
  icon: any, 
  label: string, 
  active?: boolean, 
  onClick: () => void 
}) {
  return (
    <button 
      onClick={onClick}
      className={`
        flex flex-col items-center gap-1.5 px-4 py-2 rounded-2xl transition-all
        ${active 
          ? 'bg-[#0969da] text-white' 
          : 'text-[#424753] hover:bg-[#f0f4fc]'
        }
      `}
    >
      <Icon className="w-5 h-5" />
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
    </button>
  );
}

function TrendsView() {
  const [allocation, setAllocation] = useState<{name: string, value: number, color: string}[]>([]);
  const [weekly, setWeekly] = useState<{date: string, duration: number}[]>([]);
  const [productiveRange, setProductiveRange] = useState("Gathering data...");
  const [heatmap, setHeatmap] = useState<{date: string, count: number}[]>([]);
  
  useEffect(() => {
    async function loadTrends() {
      await initDatabase();

      const stats = await getCategoryStats();
      const mappedAllocation = stats.map((s) => {
        const cat = DEFAULT_CATEGORIES.find((c) => c.id === s.categoryId);
        let hexColor = '#424753';
        if (cat?.bgColor.includes('0969da')) hexColor = '#0969da';
        else if (cat?.bgColor.includes('2e7a5f')) hexColor = '#2e7a5f';
        else if (cat?.bgColor.includes('fd8a42')) hexColor = '#fd8a42';
        
        return {
          name: cat?.name || s.categoryId,
          value: s.duration,
          color: hexColor
        };
      });

      setAllocation(mappedAllocation);
      setWeekly(await getWeeklyActivity());
      setProductiveRange(await getProductiveRange());
      setHeatmap(await getHeatmapData());
    }

    loadTrends().catch((error) => {
      console.error('Failed to load trends', error);
      setAllocation([]);
      setWeekly([]);
      setProductiveRange('No data');
      setHeatmap([]);
    });
  }, []);

  const totalSessions = useMemo(() => heatmap.reduce((acc, curr) => acc + curr.count, 0), [heatmap]);

  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-black tracking-tight">Trends & Flow</h1>
      </header>
      
      <main className="px-6 pt-4 max-w-4xl mx-auto space-y-6">
        {/* Quick Insights Row */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-2xl shadow-sm border border-[#e4e8f0]">
            <div className="flex items-center gap-2 mb-2 text-[#0051ae]">
              <Target className="w-5 h-5" />
              <h3 className="font-bold text-sm tracking-wide uppercase">Peak Focus</h3>
            </div>
            <p className="font-black text-lg text-[#171c22]">{productiveRange}</p>
          </div>
          <div className="bg-white p-4 rounded-2xl shadow-sm border border-[#e4e8f0]">
            <div className="flex items-center gap-2 mb-2 text-[#2e7a5f]">
              <Flame className="w-5 h-5" />
              <h3 className="font-bold text-sm tracking-wide uppercase">Total Sessions</h3>
            </div>
            <p className="font-black text-2xl text-[#171c22]">{totalSessions}</p>
          </div>
        </div>

        {/* Category Allocation Doughnut */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-[#e4e8f0]">
          <h2 className="text-xl font-black mb-6">Time Allocation (Flow)</h2>
          {allocation.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={allocation}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {allocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`${value} min`, 'Duration']}
                    contentStyle={{ borderRadius: '1rem', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-[#424753] bg-[#f0f4fc] rounded-2xl">
              No category data yet. Complete some sessions!
            </div>
          )}
        </div>

        {/* Consistency Heatmap */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-[#e4e8f0]">
           <div className="flex items-center gap-2 mb-6">
              <Calendar className="w-5 h-5 text-[#0051ae]" />
              <h2 className="text-xl font-black">Consistency</h2>
           </div>
           
           <div className="flex flex-wrap gap-1.5 justify-start">
             {heatmap.length > 0 ? (
               Array.from({ length: 90 }).map((_, i) => {
                 // Map heatmap dates to boxes. This is a naive visualizer for the last 90 days
                 // Ideally we'd map exact calendar days, but we use logged days to show density
                 const logIndex = heatmap.length - 1 - i;
                 const dayData = logIndex >= 0 ? heatmap[logIndex] : null;
                 
                 let bgClass = "bg-[#e4e8f0]";
                 if (dayData) {
                   if (dayData.count > 5) bgClass = "bg-[#0051ae]";
                   else if (dayData.count > 3) bgClass = "bg-[#0969da]";
                   else if (dayData.count > 1) bgClass = "bg-[#66a3ff]";
                   else if (dayData.count === 1) bgClass = "bg-[#b3d4ff]";
                 }

                 return (
                   <div 
                    key={i} 
                    className={`w-3 h-3 rounded-sm ${bgClass}`}
                    title={dayData ? `${dayData.date}: ${dayData.count} sessions` : 'No activity'}
                   />
                 );
               })
             ) : (
                <div className="text-[#424753] text-sm py-4">Hit your first session to start the chain!</div>
             )}
           </div>
        </div>

        {/* Weekly Activity Bar Chart */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-[#e4e8f0]">
          <h2 className="text-xl font-black mb-6">Rolling 7 Days</h2>
          {weekly.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsBarChart data={weekly}>
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(val) => val.substring(5)} // Show MM-DD
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#424753', fontSize: 12 }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#424753', fontSize: 12 }}
                  />
                  <Tooltip 
                    cursor={{ fill: '#f0f4fc' }}
                    contentStyle={{ borderRadius: '1rem', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="duration" fill="#0969da" radius={[4, 4, 0, 0]} name="Minutes" />
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-[#424753] bg-[#f0f4fc] rounded-2xl">
              Not enough data for this week!
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [currentView, setCurrentView] = useState<View>('timer');
  const [sessionsCompleted, setSessionsCompleted] = useState(0);

  useEffect(() => {
    async function loadTodaySessions() {
      try {
        await initDatabase();
        const today = await getTodaySessions();
        setSessionsCompleted(today.length);
      } catch (e) {
        console.error('Failed to load today sessions', e);
      }
    }

    if (currentView === 'timer') {
      loadTodaySessions();
    }

    return subscribeToSessionChanges(loadTodaySessions);
  }, [currentView]);

  const renderView = () => {
    switch (currentView) {
      case 'timer':
        return <ActiveSteepTimer sessionsCompleted={sessionsCompleted} />;
      case 'sessions':
        return <SessionHistoryList />;
      case 'stats':
        return <StatsView />;
      case 'trends':
        return <TrendsView />;
      case 'profile':
        return <ProfileView />;
      default:
        return <ActiveSteepTimer />;
    }
  };

  return (
    <div>
      {renderView()}
      
      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-3 bg-[#f7f9ff]/80 backdrop-blur-xl rounded-t-[0.75rem]" style={{ boxShadow: '0px 24px 48px rgba(23, 28, 34, 0.06)' }}>
        <NavItem 
          icon={Clock} 
          label="Sessions" 
          active={currentView === 'sessions'} 
          onClick={() => setCurrentView('sessions')} 
        />
        <NavItem 
          icon={Timer} 
          label="Timer" 
          active={currentView === 'timer'} 
          onClick={() => setCurrentView('timer')} 
        />
        <NavItem 
          icon={BarChart3} 
          label="Stats" 
          active={currentView === 'stats'} 
          onClick={() => setCurrentView('stats')} 
        />
        <NavItem 
          icon={TrendingUp} 
          label="Trends" 
          active={currentView === 'trends'} 
          onClick={() => setCurrentView('trends')} 
        />
        <NavItem 
          icon={User} 
          label="Profile" 
          active={currentView === 'profile'} 
          onClick={() => setCurrentView('profile')} 
        />
      </nav>
    </div>
  );
}
