import { DeviceProfile } from '../types';

export const deviceProfiles: DeviceProfile[] = [
  {
    id: 'light',
    name: 'Light Capacity',
    description: 'CPU-optimized for basic conversation and light reasoning',
    capabilities: ['Voice interaction', 'Text chat', 'Light reasoning', 'Basic Q&A'],
    hardware: 'CPU Only',
    modelSize: '1-3B parameters',
    icon: 'cpu'
  },
  {
    id: 'medium',
    name: 'Medium Capacity',
    description: 'GPU/NPU mid-tier with coding capabilities',
    capabilities: ['Voice interaction', 'Text chat', 'Medium reasoning', 'Basic coding', 'Code review'],
    hardware: 'GPU/NPU Mid-tier',
    modelSize: '7-13B parameters',
    icon: 'zap'
  },
  {
    id: 'heavy',
    name: 'Heavy Capacity',
    description: 'High-end GPU/NPU for advanced reasoning and coding',
    capabilities: ['Voice interaction', 'Text chat', 'Advanced reasoning', 'Complex coding', 'Architecture design', 'Multi-step analysis'],
    hardware: 'High-end GPU/NPU',
    modelSize: '30-70B parameters',
    icon: 'rocket'
  }
];

export async function detectDeviceCapability(): Promise<DeviceProfile> {
  // Real hardware detection
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  
  let gpuTier = 'none';
  let gpuRenderer = '';
  
  if (gl) {
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      gpuRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL).toLowerCase();
      
      // Detect high-end GPUs
      if (gpuRenderer.includes('rtx 4090') || 
          gpuRenderer.includes('rtx 4080') ||
          gpuRenderer.includes('rtx 3090') ||
          gpuRenderer.includes('rtx 3080') ||
          gpuRenderer.includes('radeon rx 7900') ||
          gpuRenderer.includes('radeon rx 6900')) {
        gpuTier = 'high';
      }
      // Detect mid-tier GPUs
      else if (gpuRenderer.includes('rtx') || 
               gpuRenderer.includes('gtx 1660') ||
               gpuRenderer.includes('gtx 1070') ||
               gpuRenderer.includes('radeon rx') ||
               gpuRenderer.includes('intel arc')) {
        gpuTier = 'medium';
      }
      // Detect integrated graphics
      else if (gpuRenderer.includes('intel') || 
               gpuRenderer.includes('amd') ||
               gpuRenderer.includes('apple')) {
        gpuTier = 'low';
      }
    }
  }

  // Get system information
  const memory = (navigator as any).deviceMemory || 4; // GB
  const cores = navigator.hardwareConcurrency || 4;
  const connection = (navigator as any).connection;
  
  // Check for NPU/AI acceleration hints
  const hasNPU = await checkForNPUSupport();
  
  console.log('Hardware Detection:', {
    gpuRenderer,
    gpuTier,
    memory,
    cores,
    hasNPU,
    userAgent: navigator.userAgent
  });

  // Determine profile based on hardware
  if (gpuTier === 'high' || (hasNPU && memory >= 16 && cores >= 8)) {
    return deviceProfiles[2]; // Heavy
  } else if (gpuTier === 'medium' || (memory >= 8 && cores >= 6) || hasNPU) {
    return deviceProfiles[1]; // Medium
  } else {
    return deviceProfiles[0]; // Light
  }
}

async function checkForNPUSupport(): Promise<boolean> {
  // Check for WebNN API (Neural Network API)
  if ('ml' in navigator) {
    try {
      const ml = (navigator as any).ml;
      if (ml && typeof ml.createContext === 'function') {
        return true;
      }
    } catch (error) {
      // WebNN not available
    }
  }

  // Check for WebGPU (can indicate modern hardware)
  if ('gpu' in navigator) {
    try {
      const adapter = await (navigator as any).gpu.requestAdapter();
      if (adapter) {
        const features = adapter.features;
        // Modern GPUs with compute shaders can often handle AI workloads
        return features.has('shader-f16') || features.has('timestamp-query');
      }
    } catch (error) {
      // WebGPU not available
    }
  }

  return false;
}

export function getProfileById(id: 'light' | 'medium' | 'heavy'): DeviceProfile {
  return deviceProfiles.find(p => p.id === id) || deviceProfiles[0];
}

export function saveProfilePreference(profileId: 'light' | 'medium' | 'heavy'): void {
  localStorage.setItem('active-profile', profileId);
}

export function getProfilePreference(): 'light' | 'medium' | 'heavy' | null {
  return localStorage.getItem('active-profile') as 'light' | 'medium' | 'heavy' | null;
}