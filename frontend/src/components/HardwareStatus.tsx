import React, { useEffect, useState } from 'react';
import { ApiService, HardwareInfo } from '../services/api';
import { Cpu, Zap, Activity } from 'lucide-react';

export const HardwareStatus: React.FC = () => {
  const [info, setInfo] = useState<HardwareInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
    // Poll every 30s
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const data = await ApiService.getHardwareInfo();
      setInfo(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !info) return null;

  const profileColor = {
    light: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    heavy: 'bg-red-100 text-red-800',
    'npu-optimized': 'bg-purple-100 text-purple-800',
  }[info.profile] || 'bg-gray-100 text-gray-800';

  return (
    <div className="flex items-center space-x-4 text-sm">
      <div className={`flex items-center px-2 py-1 rounded-full ${profileColor} font-medium`}>
        <Zap className="w-3 h-3 mr-1" />
        {info.profile.toUpperCase()}
      </div>
      
      <div className="flex items-center text-gray-600 hidden md:flex">
        <Cpu className="w-4 h-4 mr-1" />
        <span>{info.capabilities.cpu.architecture} ({info.capabilities.cpu.cores}c)</span>
      </div>

      {info.capabilities.gpu && (
        <div className="flex items-center text-gray-600 hidden md:flex">
          <Activity className="w-4 h-4 mr-1" />
          <span>{info.capabilities.gpu.name}</span>
        </div>
      )}
      
      <div className="text-gray-500 text-xs">
        Model: <span className="font-mono">{info.selected_model.split('/').pop()}</span>
      </div>
    </div>
  );
};
