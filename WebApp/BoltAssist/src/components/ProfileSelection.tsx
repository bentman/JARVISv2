import React from 'react';
import { DeviceProfile } from '../types';
import { ProfileCard } from './ProfileCard';
import { deviceProfiles } from '../services/deviceDetection';

interface ProfileSelectionProps {
  detectedProfile: DeviceProfile;
  activeProfile: DeviceProfile;
  onProfileChange: (profileId: 'light' | 'medium' | 'heavy') => void;
}

export function ProfileSelection({ detectedProfile, activeProfile, onProfileChange }: ProfileSelectionProps) {
  return (
    <div className="bg-gray-900 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-2">Hardware Profile</h2>
        <p className="text-gray-400 text-sm">
          Detected: <span className="text-blue-400 font-medium">{detectedProfile.name}</span>
          {activeProfile.id !== detectedProfile.id && (
            <span className="text-amber-400 ml-2">(Manual override active)</span>
          )}
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {deviceProfiles.map((profile) => (
          <ProfileCard
            key={profile.id}
            profile={profile}
            isActive={activeProfile.id === profile.id}
            onSelect={() => onProfileChange(profile.id)}
          />
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <h3 className="text-sm font-medium text-white mb-2">Current Configuration</h3>
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-gray-400">Model Size:</span>
            <span className="text-white ml-2">{activeProfile.modelSize}</span>
          </div>
          <div>
            <span className="text-gray-400">Hardware:</span>
            <span className="text-white ml-2">{activeProfile.hardware}</span>
          </div>
        </div>
      </div>
    </div>
  );
}