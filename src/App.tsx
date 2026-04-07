import { useState } from 'react';
import { Timer, BarChart3, TrendingUp, User, Clock } from 'lucide-react';
import ActiveSteepTimer from './components/ActiveSteepTimer';
import SessionHistoryList from './components/SessionHistoryList';
import StatsView from './components/StatsView';

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
  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-black tracking-tight">Trends</h1>
      </header>
      <main className="px-6 pt-8">
        <p className="text-[#424753]">Trends coming soon...</p>
      </main>
    </div>
  );
}

function ProfileView() {
  return (
    <div className="min-h-screen bg-[#f7f9ff] text-[#171c22] font-sans pb-32">
      <header className="sticky top-0 z-50 bg-[#f7f9ff]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-black tracking-tight">Profile</h1>
      </header>
      <main className="px-6 pt-8">
        <p className="text-[#424753]">Profile coming soon...</p>
      </main>
    </div>
  );
}

export default function App() {
  const [currentView, setCurrentView] = useState<View>('timer');
  const [sessionsCompleted] = useState(3);

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
