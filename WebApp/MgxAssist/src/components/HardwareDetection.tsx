import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Cpu, HardDrive, Zap, Monitor, RefreshCw } from 'lucide-react';
import { HardwareProfile, hardwareProfiles } from '@/lib/systemData';

interface HardwareDetectionProps {
  onProfileSelected: (profile: HardwareProfile) => void;
  selectedProfile: HardwareProfile | null;
}

export default function HardwareDetection({ onProfileSelected, selectedProfile }: HardwareDetectionProps) {
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionProgress, setDetectionProgress] = useState(0);
  const [detectedProfile, setDetectedProfile] = useState<HardwareProfile | null>(null);

  const simulateDetection = async () => {
    setIsDetecting(true);
    setDetectionProgress(0);
    
    // Simulate detection process
    const steps = [
      'Detecting CPU capabilities...',
      'Scanning for GPU/NPU...',
      'Measuring memory capacity...',
      'Testing local model compatibility...',
      'Generating capability profile...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setDetectionProgress((i + 1) * 20);
    }
    
    // Randomly select a profile for simulation
    const randomProfile = hardwareProfiles[Math.floor(Math.random() * hardwareProfiles.length)];
    setDetectedProfile(randomProfile);
    setIsDetecting(false);
  };

  const getProfileTypeColor = (type: string) => {
    switch (type) {
      case 'heavy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'light': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Cpu className="h-5 w-5" />
          Hardware Capability Detection
        </CardTitle>
        <CardDescription>
          Detect and configure your device's AI processing capabilities
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="detection" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="detection">Auto Detection</TabsTrigger>
            <TabsTrigger value="manual">Manual Selection</TabsTrigger>
          </TabsList>
          
          <TabsContent value="detection" className="space-y-4">
            {!isDetecting && !detectedProfile && (
              <div className="text-center py-8">
                <Button onClick={simulateDetection} size="lg" className="gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Start Hardware Detection
                </Button>
                <p className="text-sm text-muted-foreground mt-2">
                  This will analyze your device's AI processing capabilities
                </p>
              </div>
            )}
            
            {isDetecting && (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-sm font-medium">Detecting hardware capabilities...</p>
                </div>
                <Progress value={detectionProgress} className="w-full" />
              </div>
            )}
            
            {detectedProfile && (
              <div className="space-y-4">
                <Alert>
                  <Zap className="h-4 w-4" />
                  <AlertDescription>
                    Hardware detection complete! Profile generated based on your system capabilities.
                  </AlertDescription>
                </Alert>
                
                <ProfileCard 
                  profile={detectedProfile} 
                  onSelect={() => onProfileSelected(detectedProfile)}
                  isSelected={selectedProfile?.id === detectedProfile.id}
                  isDetected={true}
                />
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="manual" className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Choose a hardware profile that best matches your device:
            </p>
            <div className="grid gap-4">
              {hardwareProfiles.map((profile) => (
                <ProfileCard
                  key={profile.id}
                  profile={profile}
                  onSelect={() => onProfileSelected(profile)}
                  isSelected={selectedProfile?.id === profile.id}
                />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

interface ProfileCardProps {
  profile: HardwareProfile;
  onSelect: () => void;
  isSelected: boolean;
  isDetected?: boolean;
}

function ProfileCard({ profile, onSelect, isSelected, isDetected = false }: ProfileCardProps) {
  const getProfileTypeColor = (type: string) => {
    switch (type) {
      case 'heavy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'light': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-primary' : 'hover:shadow-md'}`} onClick={onSelect}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-semibold flex items-center gap-2">
              {profile.name}
              {isDetected && <Badge variant="secondary">Detected</Badge>}
            </h3>
            <Badge className={getProfileTypeColor(profile.type)}>
              {profile.type.toUpperCase()} Performance
            </Badge>
          </div>
          {isSelected && (
            <Badge variant="default">Selected</Badge>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-muted-foreground" />
              <span>{profile.capabilities.cpu}</span>
            </div>
            <div className="flex items-center gap-2">
              <Monitor className="h-4 w-4 text-muted-foreground" />
              <span>{profile.capabilities.gpu || 'Integrated'}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-muted-foreground" />
              <span>{profile.capabilities.ram}GB RAM</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span>{profile.capabilities.npu ? 'NPU Available' : 'No NPU'}</span>
            </div>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t">
          <p className="text-xs text-muted-foreground mb-2">Local Models:</p>
          <div className="flex flex-wrap gap-1">
            {profile.localModels.map((model) => (
              <Badge key={model} variant="outline" className="text-xs">
                {model}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}