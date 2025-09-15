import React from 'react';
import { Cpu, Wifi, WifiOff } from 'lucide-react';
import { DeviceProfile, BackendStatus } from '../types';

interface HeaderProps {
  activeProfile: DeviceProfile;
  backendStatus: BackendStatus;
  onProfileChange: (profileId: 'light' | 'medium' | 'heavy') => void;
}

export function Header({ activeProfile, backendStatus, onProfileChange }: HeaderProps) {
  const profiles = [
    { id: 'light' as const, name: 'Light', color: 'text-amber-400' },
    { id: 'medium' as const, name: 'Medium', color: 'text-blue-400' },
    { id: 'heavy' as const, name: 'Heavy', color: 'text-green-400' }
  ];

  return (
    <header className="bg-gray-900 border-b border-gray-800 p-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Cpu className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-xl font-bold text-white">AI Assistant</h1>
            <p className="text-sm text-gray-400">Local-First Computing</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Profile:</span>
            <select
              value={activeProfile.id}
              onChange={(e) => onProfileChange(e.target.value as 'light' | 'medium' | 'heavy')}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1 text-sm text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {profiles.map(profile => (
                <option key={profile.id} value={profile.id}>
                  {profile.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            {backendStatus.connected ? (
              <Wifi className="w-5 h-5 text-green-400" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-400" />
            )}
            <span className="text-sm text-gray-400">
              {backendStatus.connected ? `${backendStatus.latency}ms` : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}