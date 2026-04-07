import { useState, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { 
  ArrowLeft, 
  Settings, 
  Zap, 
  Timer, 
  Play, 
  Square, 
  Plus,
  Heart,
  BookOpen,
  Sparkles,
  Brain,
  Trash2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { initDatabase, saveSession } from '../lib/database';

export type SessionCategory = {
  id: string;
  name: string;
  icon: ReactNode;
  color: string;
  bgColor: string;
  isCustom?: boolean;
};

export const DEFAULT_CATEGORIES: SessionCategory[] = [
  {
    id: 'meditation',
    name: 'Meditation',
    icon: <Sparkles className="w-6 h-6" />,
    color: 'text-[#0a6148]',
    bgColor: 'bg-[#2e7a5f]',
  },
  {
    id: 'gratitude',
    name: 'Gratitude',
    icon: <Heart className="w-6 h-6" />,
    color: 'text-[#9b4500]',
    bgColor: 'bg-[#fd8a42]',
  },
  {
    id: 'deep-work',
    name: 'Deep Work',
    icon: <Brain className="w-6 h-6" />,
    color: 'text-[#0051ae]',
    bgColor: 'bg-[#0969da]',
  },
];

const QUICK_TIMES = [1, 2, 3, 4, 5];

type CircularDialProps = {
  value: number;
  onChange: (value: number) => void;
  maxValue?: number;
};

function CircularDial({ value, onChange, maxValue = 60 }: CircularDialProps) {
  const [isDragging, setIsDragging] = useState(false);
  const dialRef = useRef<SVGSVGElement>(null);

  const radius = 120;
  const circumference = 2 * Math.PI * radius;
  const progress = (value / maxValue) * circumference;

  const handleInteraction = (clientX: number, clientY: number) => {
    if (!dialRef.current) return;
    
    const rect = dialRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const angle = Math.atan2(clientY - centerY, clientX - centerX);
    let degrees = (angle * 180 / Math.PI) + 90;
    
    if (degrees < 0) degrees += 360;
    
    const newValue = Math.round((degrees / 360) * maxValue);
    onChange(Math.max(1, Math.min(maxValue, newValue)));
  };

  return (
    <div className="relative w-64 h-64 mx-auto mb-8">
      <svg 
        ref={dialRef}
        viewBox="0 0 280 280" 
        className="w-full h-full cursor-pointer"
        onMouseDown={(e) => {
          setIsDragging(true);
          handleInteraction(e.clientX, e.clientY);
        }}
        onMouseMove={(e) => {
          if (isDragging) handleInteraction(e.clientX, e.clientY);
        }}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onTouchStart={(e) => {
          setIsDragging(true);
          handleInteraction(e.touches[0].clientX, e.touches[0].clientY);
        }}
        onTouchMove={(e) => {
          if (isDragging) handleInteraction(e.touches[0].clientX, e.touches[0].clientY);
        }}
        onTouchEnd={() => setIsDragging(false)}
      >
        <defs>
          <linearGradient id="dialGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0051ae" />
            <stop offset="100%" stopColor="#0969da" />
          </linearGradient>
        </defs>
        
        <circle 
          cx="140" 
          cy="140" 
          r={radius} 
          fill="none" 
          stroke="#e4e8f0" 
          strokeWidth="12"
        />
        
        <circle 
          cx="140" 
          cy="140" 
          r={radius} 
          fill="none" 
          stroke="url(#dialGradient)" 
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          transform="rotate(-90 140 140)"
          className="transition-all duration-150"
        />
        
        {Array.from({ length: maxValue }).map((_, i) => {
          const angle = (i / maxValue) * 360;
          const rad = angle * Math.PI / 180;
          const x1 = 140 + (radius - 20) * Math.cos(rad);
          const y1 = 140 + (radius - 20) * Math.sin(rad);
          const x2 = 140 + (radius - 10) * Math.cos(rad);
          const y2 = 140 + (radius - 10) * Math.sin(rad);
          
          if (i % 5 === 0) {
            return (
              <line 
                key={i}
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#0051ae"
                strokeWidth="3"
                strokeLinecap="round"
              />
            );
          }
          return null;
        })}
        
        <circle cx="140" cy="140" r="30" fill="#f7f9ff" stroke="#0051ae" strokeWidth="3" />
      </svg>
      
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <div className="font-mono text-5xl font-black text-[#171c22]">
            {value}
          </div>
          <div className="text-sm font-bold text-[#424753] uppercase tracking-wider">
            min
          </div>
        </div>
      </div>
    </div>
  );
}

type QuickTimeButtonProps = {
  minutes: number;
  selected: boolean;
  onClick: () => void;
};

function QuickTimeButton({ minutes, selected, onClick }: QuickTimeButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        w-14 h-14 rounded-full flex items-center justify-center font-black text-lg
        transition-all duration-200
        ${selected 
          ? 'bg-[#0051ae] text-white shadow-lg scale-110' 
          : 'bg-[#e4e8f0] text-[#424753] hover:bg-[#dee3eb]'
        }
      `}
    >
      {minutes}
    </button>
  );
}

type ActiveSteepTimerProps = {
  onBack?: () => void;
  sessionsCompleted?: number;
  totalSessions?: number;
};

export default function ActiveSteepTimer({ 
  onBack,
  sessionsCompleted = 3,
  totalSessions = 8 
}: ActiveSteepTimerProps) {
  const [selectedCategory, setSelectedCategory] = useState<SessionCategory>(DEFAULT_CATEGORIES[2]);
  const [customCategories, setCustomCategories] = useState<SessionCategory[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [dialMinutes, setDialMinutes] = useState(25);
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showCategoryPicker, setShowCategoryPicker] = useState(false);
  const [useQuickTime, setUseQuickTime] = useState(false);
  const [sessionSaved, setSessionSaved] = useState(false);

  const allCategories = [...DEFAULT_CATEGORIES, ...customCategories];
  const progressPercent = (sessionsCompleted / totalSessions) * 100;

  useEffect(() => {
    initDatabase().catch(console.error);
  }, []);

  const handleTimerComplete = useCallback(() => {
    console.log('Timer complete! Saving session...', selectedCategory, dialMinutes);
    const now = new Date();
    const session = {
      id: `session-${Date.now()}`,
      categoryId: selectedCategory.id,
      title: selectedCategory.name,
      date: 'Today',
      time: now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
      duration: dialMinutes,
      notes: ''
    };
    saveSession(session);
    setSessionSaved(true);
    setTimeout(() => setSessionSaved(false), 3000);
    handleReset();
  }, [selectedCategory, dialMinutes]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsRunning(false);
      handleTimerComplete();
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft, handleTimerComplete]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStart = () => {
    if (useQuickTime) {
      setTimeLeft(dialMinutes * 60);
    }
    setIsRunning(true);
  };

  const handleStop = () => setIsRunning(false);
  
  const handleReset = () => {
    setIsRunning(false);
    setTimeLeft(dialMinutes * 60);
  };

  const handleQuickTimeSelect = (minutes: number) => {
    setDialMinutes(minutes);
    setTimeLeft(minutes * 60);
    setUseQuickTime(true);
  };

  const handleDialChange = (minutes: number) => {
    setDialMinutes(minutes);
    setTimeLeft(minutes * 60);
    setUseQuickTime(false);
  };

  const addCustomCategory = () => {
    if (newCategoryName.trim()) {
      const newCategory: SessionCategory = {
        id: `custom-${Date.now()}`,
        name: newCategoryName.trim(),
        icon: <BookOpen className="w-6 h-6" />,
        color: 'text-[#424753]',
        bgColor: 'bg-[#424753]',
        isCustom: true,
      };
      setCustomCategories([...customCategories, newCategory]);
      setSelectedCategory(newCategory);
      setNewCategoryName('');
      setShowAddCategory(false);
    }
  };

  const deleteCategory = (id: string) => {
    setCustomCategories(customCategories.filter(c => c.id !== id));
    if (selectedCategory.id === id) {
      setSelectedCategory(DEFAULT_CATEGORIES[0]);
    }
  };

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
          <h1 className="text-xl font-black tracking-tight text-[#171c22]">
            TeaTime
          </h1>
        </div>
        <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#e4e8f0] transition-all">
          <Settings className="w-5 h-5 text-[#424753]" />
        </button>
      </header>

      <div className="h-1 w-full bg-[#f0f4fc]"></div>

      <main className="pt-8 pb-32 px-6 max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-[#171c22] mb-2">
            Active Steep
          </h1>
          <p className="text-[#424753] font-medium text-lg">
            Set your intention.
          </p>
        </header>

        <section className="bg-[#f0f4fc] rounded-[2rem] p-8 mb-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
            <Timer className="w-48 h-48 text-[#171c22]" />
          </div>

          <div className="inline-flex items-center gap-2 bg-[#0051ae]/10 text-[#0051ae] px-4 py-2 rounded-full mb-6">
            <Zap className="w-4 h-4" />
            <span className="font-bold tracking-widest text-xs uppercase">
              {selectedCategory.name} Mode
            </span>
          </div>

          <CircularDial 
            value={dialMinutes} 
            onChange={handleDialChange}
            maxValue={60}
          />

          <div className="mb-6">
            <p className="text-sm font-bold text-[#424753] mb-3">Quick Select (1-5 min)</p>
            <div className="flex justify-center gap-3">
              {QUICK_TIMES.map((mins) => (
                <QuickTimeButton
                  key={mins}
                  minutes={mins}
                  selected={useQuickTime && dialMinutes === mins}
                  onClick={() => handleQuickTimeSelect(mins)}
                />
              ))}
            </div>
          </div>

          {isRunning && (
            <div className="font-mono text-5xl font-black leading-none tracking-tighter text-[#171c22] mb-6">
              {formatTime(timeLeft)}
            </div>
          )}

          {sessionSaved && (
            <div className="mb-4 px-4 py-2 bg-[#0a6148] text-white rounded-full font-bold text-sm">
              Session saved!
            </div>
          )}

          <div className="flex flex-col md:flex-row justify-center gap-4 max-w-xl mx-auto">
            {!isRunning ? (
              <button 
                onClick={handleStart}
                className="flex-1 h-20 bg-[#0051ae] text-white rounded-xl font-black text-2xl flex items-center justify-center gap-3 transition-transform active:scale-95 shadow-lg"
              >
                <Play className="w-8 h-8" />
                START
              </button>
            ) : (
              <button 
                onClick={handleStop}
                className="flex-1 h-20 bg-[#e4e8f0] text-[#171c22] rounded-xl font-black text-2xl flex items-center justify-center gap-3 transition-transform active:scale-95"
              >
                <Square className="w-8 h-8" />
                STOP
              </button>
            )}
          </div>
        </section>

        <section className="mb-8">
          <div className="flex justify-between items-end mb-4">
            <h3 className="font-black text-xl tracking-tight uppercase">
              Rhythm and Flow
            </h3>
            <span className="font-bold text-[#0051ae]">
              {sessionsCompleted} / {totalSessions} Sessions
            </span>
          </div>
          <div className="w-full h-4 bg-[#e4e8f0] rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-[#0051ae] to-[#0a6148] rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {allCategories.slice(0, 3).map((category) => (
            <button 
              key={category.id}
              onClick={() => {
                setSelectedCategory(category);
                setShowCategoryPicker(false);
              }}
              className={`
                group p-6 rounded-[1.5rem] text-left transition-all duration-300
                ${selectedCategory.id === category.id 
                  ? `border-2 ${category.bgColor.replace('bg-', 'border-')}/40 ${category.bgColor}/10` 
                  : 'hover:bg-[#e4e8f0] border-2 border-transparent'
                }
              `}
            >
              <div className={`
                w-12 h-12 ${category.bgColor} text-white rounded-lg 
                flex items-center justify-center mb-4
              `}>
                {category.icon}
              </div>
              <h4 className="text-xl font-black text-[#171c22]">
                {category.name}
              </h4>
            </button>
          ))}
          
          <button 
            onClick={() => setShowCategoryPicker(!showCategoryPicker)}
            className="group p-6 border-2 border-dashed border-[#e4e8f0] hover:border-[#0051ae]/40 rounded-[1.5rem] text-left transition-all duration-300 flex flex-col items-center justify-center"
          >
            <div className="w-12 h-12 bg-[#e4e8f0] text-[#424753] rounded-lg flex items-center justify-center mb-4">
              <Plus className="w-6 h-6" />
            </div>
            <h4 className="text-xl font-black text-[#424753]">
              Add Custom
            </h4>
          </button>
        </section>

        <AnimatePresence>
          {showCategoryPicker && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <div className="bg-[#f0f4fc] rounded-[1.5rem] p-6">
                <h3 className="font-black text-lg mb-4">Choose a Category</h3>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                  {allCategories.map((category) => (
                    <div key={category.id} className="relative">
                      <button
                        onClick={() => {
                          setSelectedCategory(category);
                          setShowCategoryPicker(false);
                        }}
                        className={`
                          w-full p-4 rounded-xl text-center transition-all
                          ${selectedCategory.id === category.id 
                            ? `${category.bgColor} text-white` 
                            : 'bg-white hover:bg-[#e4e8f0]'
                          }
                        `}
                      >
                        <div className="flex justify-center mb-2">
                          {category.icon}
                        </div>
                        <span className="text-sm font-bold">{category.name}</span>
                      </button>
                      {category.isCustom && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteCategory(category.id);
                          }}
                          className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                {showAddCategory ? (
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={newCategoryName}
                      onChange={(e) => setNewCategoryName(e.target.value)}
                      placeholder="Category name..."
                      className="flex-1 px-4 py-3 rounded-xl border-2 border-[#e4e8f0] focus:border-[#0051ae] outline-none"
                      autoFocus
                    />
                    <button
                      onClick={addCustomCategory}
                      className="px-6 py-3 bg-[#0051ae] text-white rounded-xl font-bold"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => {
                        setShowAddCategory(false);
                        setNewCategoryName('');
                      }}
                      className="px-4 py-3 text-[#424753] font-bold"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowAddCategory(true)}
                    className="flex items-center gap-2 text-[#0051ae] font-bold"
                  >
                    <Plus className="w-5 h-5" />
                    Create New Category
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
