import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useUIStore } from '../store';

const Notifications: React.FC = () => {
  const { notifications, removeNotification } = useUIStore();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  const getBgColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 border-green-500/30';
      case 'warning':
        return 'bg-yellow-500/20 border-yellow-500/30';
      case 'error':
        return 'bg-red-500/20 border-red-500/30';
      default:
        return 'bg-blue-500/20 border-blue-500/30';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-md">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 100, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            className={`glass ${getBgColor(
              notification.type
            )} border rounded-lg p-4 flex items-start gap-3 shadow-lg backdrop-blur-sm`}
          >
            <div className="flex-shrink-0">{getIcon(notification.type)}</div>
            <p className="flex-1 text-sm text-dark-100">{notification.message}</p>
            <button
              onClick={() => removeNotification(notification.id)}
              className="flex-shrink-0 p-1 hover:bg-dark-800/50 rounded transition-colors"
            >
              <X className="w-4 h-4 text-dark-400" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Notifications;
