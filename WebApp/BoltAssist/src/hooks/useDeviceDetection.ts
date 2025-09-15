import { useState, useEffect } from 'react';
import { DeviceProfile } from '../types';
import { detectDeviceCapability, getProfileById, saveProfilePreference, getProfilePreference } from '../services/deviceDetection';

export function useDeviceDetection() {
  const [detectedProfile, setDetectedProfile] = useState<DeviceProfile | null>(null);
  const [activeProfile, setActiveProfile] = useState<DeviceProfile | null>(null);
  const [isDetecting, setIsDetecting] = useState(true);

  useEffect(() => {
    const runDetection = async () => {
      setIsDetecting(true);
      
      try {
        // Check for saved preference first
        const savedProfile = getProfilePreference();
        
        // Run hardware detection
        const detected = await detectDeviceCapability();
        setDetectedProfile(detected);
        
        // Use saved preference if available, otherwise use detected
        const profileToUse = savedProfile ? getProfileById(savedProfile) : detected;
        setActiveProfile(profileToUse);
        
        console.log('Device detection complete:', {
          detected: detected.name,
          active: profileToUse.name,
          wasSaved: !!savedProfile
        });
        
      } catch (error) {
        console.error('Device detection failed:', error);
        // Fallback to light profile
        const fallback = getProfileById('light');
        setDetectedProfile(fallback);
        setActiveProfile(fallback);
      } finally {
        setIsDetecting(false);
      }
    };

    runDetection();
  }, []);

  const changeProfile = (profileId: 'light' | 'medium' | 'heavy') => {
    const profile = getProfileById(profileId);
    setActiveProfile(profile);
    saveProfilePreference(profileId);
    
    console.log('Profile changed to:', profile.name);
  };

  return {
    detectedProfile,
    activeProfile,
    isDetecting,
    changeProfile
  };
}