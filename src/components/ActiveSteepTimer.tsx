import { useState, useEffect, type ReactNode } from 'react';
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
  MoreVertical,
  Trash2,
  Edit2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

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
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showCategoryPicker, setShowCategoryPicker] = useState(false);

  const allCategories = [...DEFAULT_CATEGORIES, ...customCategories];
  const progressPercent = (sessionsCompleted / totalSessions) * 100;

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsRunning(false);
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStart = () => setIsRunning(true);
  const handleStop = () => setIsRunning(false);
  const handleReset = () => {
    setIsRunning(false);
    setTimeLeft(25 * 60);
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
      {/* Header */}
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

      {/* Divider */}
      <div className="h-1 w-full bg-[#f0f4fc]"></div>

      <main className="pt-8 pb-32 px-6 max-w-4xl mx-auto">
        {/* Header Section */}
        <header className="mb-12">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-[#171c22] mb-2">
            Active Steep
          </h1>
          <p className="text-[#424753] font-medium text-lg">
            Maintaining your daily rhythm.
          </p>
        </header>

        {/* Main Timer Block */}
        <section className="bg-[#f0f4fc] rounded-[2rem] p-8 md:p-16 mb-8 text-center relative overflow-hidden">
          {/* Background Texture Decal */}
          <div className="absolute top-0 right-0 p-8 opacity-[0.03] select-none pointer-events-none">
            <Timer className="w-48 h-48 text-[#171c22]" />
          </div>

          {/* Focus Mode Indicator */}
          <div className="inline-flex items-center gap-2 bg-[#0051ae]/10 text-[#0051ae] px-4 py-2 rounded-full mb-8">
            <Zap className="w-4 h-4" />
            <span className="font-bold tracking-widest text-xs uppercase">
              {selectedCategory.name} Mode
            </span>
          </div>

          {/* The Hero Countdown */}
          <div className="font-mono text-[6rem] md:text-[10rem] font-black leading-none tracking-tighter text-[#171c22] mb-8">
            {formatTime(timeLeft)}
          </div>

          {/* Primary Controls */}
          <div className="flex flex-col md:flex-row justify-center gap-4 max-w-xl mx-auto">
            <button 
              onClick={handleStart}
              className="flex-1 h-20 bg-[#0051ae] text-white rounded-xl font-black text-2xl flex items-center justify-center gap-3 transition-transform active:scale-95 shadow-lg"
            >
              <Play className="w-8 h-8" />
              START
            </button>
            <button 
              onClick={handleStop}
              className="flex-1 h-20 bg-[#e4e8f0] text-[#171c22] rounded-xl font-black text-2xl flex items-center justify-center gap-3 transition-transform active:scale-95"
            >
              <Square className="w-8 h-8" />
              STOP
            </button>
          </div>
        </section>

        {/* Progress Horizon */}
        <section className="mb-12">
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

        {/* Mode Selector: Category Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {allCategories.slice(0, 3).map((category) => (
            <button 
              key={category.id}
              onClick={() => {
                setSelectedCategory(category);
                setShowCategoryPicker(false);
              }}
              className={`
                group p-8 rounded-[1.5rem] text-left transition-all duration-300
                ${selectedCategory.id === category.id 
                  ? `border-2 ${category.bgColor}/40` 
                  : 'hover:bg-[#e4e8f0]'
                }
              `}
            >
              <div className={`
                w-12 h-12 ${category.bgColor} text-white rounded-lg 
                flex items-center justify-center mb-6 shadow-lg
              `}>
                {category.icon}
              </div>
              <div className={`
                text-xs font-black ${category.color} uppercase tracking-[0.2em] mb-1
              `}>
                Session Mode
              </div>
              <h4 className="text-2xl font-black text-[#171c22] tracking-tight group-hover:translate-x-1 transition-transform">
                {category.name}
              </h4>
            </button>
          ))}
          
          {/* Add Category Button */}
          <button 
            onClick={() => setShowCategoryPicker(!showCategoryPicker)}
            className="group p-8 border-2 border-dashed border-[#e4e8f0] hover:border-[#0051ae]/40 rounded-[1.5rem] text-left transition-all duration-300 flex flex-col items-center justify-center"
          >
            <div className="w-12 h-12 bg-[#e4e8f0] text-[#424753] rounded-lg flex items-center justify-center mb-4">
              <Plus className="w-6 h-6" />
            </div>
            <h4 className="text-xl font-black text-[#424753]">
              Add Custom
            </h4>
          </button>
        </section>

        {/* Category Picker Dropdown */}
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
                
                {/* Existing Categories */}
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

                {/* Add New Category */}
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

        {/* Decorative Mood Image Placeholder */}
        <section className="mt-12 rounded-[2rem] overflow-hidden h-48 relative bg-gradient-to-br from-[#f0f4fc] to-[#e4e8f0]">
          <div className="absolute inset-0 bg-gradient-to-t from-[#f7f9ff] to-transparent" />
        </section>
      </main>
    </div>
  );
}
