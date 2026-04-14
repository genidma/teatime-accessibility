import React, { useState, useEffect } from 'react';
import { Cloud, CloudOff } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export default function SyncStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const { user } = useAuth();
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOnline) {
    return (
      <div className="fixed top-4 right-4 z-[100] flex items-center gap-1.5 px-3 py-1.5 bg-red-100/90 backdrop-blur border border-red-200 text-red-700 text-[10px] font-bold uppercase tracking-widest rounded-full shadow-sm">
        <CloudOff className="w-3.5 h-3.5" />
        <span>Offline Mode</span>
      </div>
    );
  }

  if (user && isOnline) {
    return (
      <div className="fixed top-4 right-4 z-[100] flex items-center gap-1.5 px-3 py-1.5 bg-[#eaf4eb]/90 backdrop-blur border border-[#d1e6d4] text-[#2e7a5f] text-[10px] font-bold uppercase tracking-widest rounded-full shadow-sm">
        <Cloud className="w-3.5 h-3.5" />
        <span>Cloud Active</span>
      </div>
    );
  }
  
  return null;
}
