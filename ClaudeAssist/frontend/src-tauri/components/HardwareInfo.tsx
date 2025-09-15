import React from 'react';
import { Cpu, HardDrive, Monitor, Zap } from 'lucide-react';

interface HardwareInfoProps {
  hardwareInfo: {
    tier: string;
    details: any;
  };
}

const HardwareInfo: React.FC<HardwareInfoProps> = ({ hardwareInfo }) => {
  const details = hardwareInfo.details;

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'heavy':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'npu':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getTierDescription = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'heavy':
        return 'High-performance setup with >8GB VRAM or >32GB RAM';
      case 'medium':
        return 'Balanced setup with 4-8GB VRAM or 16-32GB RAM';
      case 'npu':
        return 'Neural Processing Unit detected for optimized AI inference';
      case 'light':
        return 'CPU-only setup with <16GB RAM';
      default:
        return 'Hardware configuration detected';
    }
  };

  return (
    <div className="space-y-6">
      {/* Tier Overview */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Hardware Tier</h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTierColor(hardwareInfo.tier)}`}>
            {hardwareInfo.tier}
          </span>
        </div>
        <p className="text-gray-600 text-sm">
          {getTierDescription(hardwareInfo.tier)}
        </p>
      </div>

      {/* Detailed Hardware Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CPU Information */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <Cpu className="w-5 h-5 text-blue-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-800">Processor</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Brand:</span>
              <span className="text-gray-800 font-medium">
                {details.cpu_brand || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cores:</span>
              <span className="text-gray-800 font-medium">
                {details.cpu_count || 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        {/* Memory Information */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <HardDrive className="w-5 h-5 text-green-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-800">Memory</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total RAM:</span>
              <span className="text-gray-800 font-medium">
                {details.total_memory_gb ? `${details.total_memory_gb.toFixed(1)} GB` : 'Unknown'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: details.total_memory_gb ? `${Math.min((details.total_memory_gb / 64) * 100, 100)}%` : '0%' }}
              ></div>
            </div>
          </div>
        </div>

        {/* GPU Information */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <Monitor className="w-5 h-5 text-purple-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-800">Graphics</h4>
          </div>
          <div className="space-y-3">
            {details.gpu_info && details.gpu_info.length > 0 ? (
              details.gpu_info.map((gpu: any, index: number) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm font-medium text-gray-800 mb-1">
                    {gpu.name}
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>Vendor: {gpu.vendor}</div>
                    {gpu.vram_gb && (
                      <div>VRAM: {gpu.vram_gb.toFixed(1)} GB</div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-600">No GPU information available</div>
            )}
          </div>
        </div>

        {/* NPU Information */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <Zap className="w-5 h-5 text-orange-600 mr-2" />
            <h4 className="text-md font-semibold text-gray-800">AI Acceleration</h4>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">NPU Detected:</span>
              <span className={`font-medium ${details.npu_detected ? 'text-green-600' : 'text-gray-500'}`}>
                {details.npu_detected ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">OS:</span>
              <span className="text-gray-800 font-medium">
                {details.os_info || 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Recommendations */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h4 className="text-md font-semibold text-gray-800 mb-4">Recommended Models</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="font-medium text-blue-800 mb-1">Chat</div>
            <div className="text-blue-600">
              {hardwareInfo.tier === 'Heavy' ? 'Llama 3.1 8B' :
               hardwareInfo.tier === 'Medium' ? 'Gemma2 9B' :
               hardwareInfo.tier === 'NPU' ? 'Gemma2 2B' : 'Phi-3 3.8B'}
            </div>
          </div>
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="font-medium text-green-800 mb-1">Code</div>
            <div className="text-green-600">
              {hardwareInfo.tier === 'Heavy' ? 'DeepSeek Coder 33B' :
               hardwareInfo.tier === 'Medium' ? 'DeepSeek Coder 6.7B' : 'Phi-3 3.8B'}
            </div>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg">
            <div className="font-medium text-purple-800 mb-1">Reasoning</div>
            <div className="text-purple-600">
              {hardwareInfo.tier === 'Heavy' ? 'Llama 3.1 8B' :
               hardwareInfo.tier === 'Medium' ? 'Gemma2 9B' : 'Phi-3 3.8B'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HardwareInfo;