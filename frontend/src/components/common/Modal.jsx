import React from 'react';
import { X, AlertTriangle } from 'lucide-react';

export const Modal = ({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirm", isDanger = false, confirmLoading = false }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-cyber-card border border-cyber-border rounded-xl max-w-md w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-start space-x-4">
          <div className={`p-3 rounded-xl ${isDanger ? 'bg-red-500/10 text-red-400 border border-red-500/30' : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'}`}>
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
            <p className="text-sm text-slate-300 leading-relaxed mb-6">{message}</p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={onClose}
                disabled={confirmLoading}
                className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={onConfirm}
                disabled={confirmLoading}
                className={`px-4 py-2 text-sm font-semibold rounded-lg text-white transition-colors flex items-center space-x-2 ${
                  isDanger 
                    ? 'bg-red-600 hover:bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.4)]' 
                    : 'bg-cyan-600 hover:bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.4)]'
                }`}
              >
                {confirmLoading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>{confirmText}</span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
