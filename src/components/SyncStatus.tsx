import React, { useState, useEffect } from 'react';
import { Cloud, CloudOff, RefreshCw } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { subscribeToSyncStatus, SyncState } from '../lib/database';
import { motion, AnimatePresence } from 'motion/react';

export default function SyncStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncState, setSyncState] = useState<SyncState>('idle');
  const { user } = useAuth();
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const unsubscribe = subscribeToSyncStatus((state) => {
      setSyncState(state);
    });

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubscribe();
    };
  }, []);

  return (
    <div className="fixed top-6 right-6 z-[100]">
      <AnimatePresence mode="wait">
        {!isOnline ? (
          <motion.div 
            key="offline"
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="flex items-center gap-2 px-3.5 py-2 bg-red-50/90 backdrop-blur-md border border-red-100 text-red-600 text-[10px] font-black uppercase tracking-widest rounded-full shadow-[0_4px_12px_rgba(220,38,38,0.1)]"
          >
            <CloudOff className="w-3.5 h-3.5" />
            <span>Offline (Saved locally)</span>
          </motion.div>
        ) : syncState === 'syncing' ? (
          <motion.div 
            key="syncing"
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ 
              opacity: 1, 
              scale: 1, 
              y: 0,
            }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="flex items-center gap-2 px-3.5 py-2 bg-amber-50/90 backdrop-blur-md border border-amber-100 text-amber-600 text-[10px] font-black uppercase tracking-widest rounded-full shadow-[0_4px_12px_rgba(217,119,6,0.1)]"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </motion.div>
            <motion.span
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              Syncing...
            </motion.span>
          </motion.div>
        ) : user ? (
          <motion.div 
            key="synced"
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-50/90 backdrop-blur-md border border-emerald-100 text-emerald-600 text-[10px] font-black uppercase tracking-widest rounded-full shadow-[0_4px_12px_rgba(5,150,105,0.05)]"
          >
            <Cloud className="w-3.5 h-3.5" />
            <span>Synced</span>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
