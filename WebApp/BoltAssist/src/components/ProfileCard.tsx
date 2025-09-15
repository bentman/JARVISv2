import React from 'react';
import { Cpu, Zap, Rocket, Check } from 'lucide-react';
import { DeviceProfile } from '../types';

interface ProfileCardProps {
  profile: DeviceProfile;
  isActive: boolean;
  onSelect: () => void;
}

const iconMap = {
  cpu: Cpu,
  zap: Zap,
  rocket: Rocket
};

export function ProfileCard({ profile, isActive, onSelect }: ProfileCardProps) {
  const Icon = iconMap[profile.icon as keyof typeof iconMap] || Cpu;
  
  return (
    <div 
      onClick={onSelect}
      className={`
        relative p-6 rounded-xl border-2 cursor-pointer transition-all duration-300 hover:scale-105
        ${isActive 
          ? 'border-blue-500 bg-blue-500/10' 
          : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
        }
      `}
    >
      {isActive && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
          <Check className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg ${isActive ? 'bg-blue-500' : 'bg-gray-700'}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">{profile.name}</h3>
          <p className="text-sm text-gray-400">{profile.hardware}</p>
        </div>
      </div>
      
      <p className="text-sm text-gray-300 mb-4">{profile.description}</p>
      
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Model Size:</span>
          <span className="text-xs font-medium text-white">{profile.modelSize}</span>
        </div>
        
        <div className="space-y-1">
          <span className="text-xs text-gray-400">Capabilities:</span>
          <div className="flex flex-wrap gap-1">
            {profile.capabilities.map((capability, index) => (
              <span 
                key={index}
                className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded-md"
              >
                {capability}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}