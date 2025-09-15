import React from 'react';
import { Activity, Database, Clock, Zap } from 'lucide-react';
import { BackendStatus, MemorySnippet } from '../types';

interface StatusPanelProps {
  backendStatus: BackendStatus;
  memorySnippets: MemorySnippet[];
  messageCount: number;
}

export function StatusPanel({ backendStatus, memorySnippets, messageCount }: StatusPanelProps) {
  return (
    <div className="bg-gray-900 p-6 space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Status
        </h2>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
            <span className="text-sm text-gray-300">Backend Connection</span>
            <span className={`text-sm font-medium ${backendStatus.connected ? 'text-green-400' : 'text-red-400'}`}>
              {backendStatus.connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
            <span className="text-sm text-gray-300">Latency</span>
            <span className="text-sm font-medium text-white">{backendStatus.latency}ms</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
            <span className="text-sm text-gray-300">Active Model</span>
            <span className="text-sm font-medium text-blue-400">{backendStatus.activeModel}</span>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          Memory ({memorySnippets.length})
        </h3>
        
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {memorySnippets.length === 0 ? (
            <p className="text-sm text-gray-400">No memory snippets yet</p>
          ) : (
            memorySnippets.slice(-5).map((snippet) => (
              <div key={snippet.id} className="p-3 bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-300 line-clamp-2">{snippet.content}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Clock className="w-3 h-3 text-gray-500" />
                  <span className="text-xs text-gray-500">
                    {snippet.timestamp.toLocaleTimeString()}
                  </span>
                  <span className="text-xs text-blue-400">{snippet.context}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Session Stats
        </h3>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-gray-800 rounded-lg text-center">
            <p className="text-2xl font-bold text-blue-400">{messageCount}</p>
            <p className="text-xs text-gray-400">Messages</p>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg text-center">
            <p className="text-2xl font-bold text-green-400">{backendStatus.memoryCount}</p>
            <p className="text-xs text-gray-400">Memories</p>
          </div>
        </div>
      </div>
    </div>
  );
}