import React, { useEffect, useState } from 'react';
import { ApiService, PrivacySettings, BudgetStatus } from '../services/api';
import { X, Shield, DollarSign, Globe } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'privacy' | 'budget' | 'search'>('privacy');
  
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold text-gray-800">Settings</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-48 bg-gray-50 border-r p-2 space-y-1">
            <button
              onClick={() => setActiveTab('privacy')}
              className={`w-full text-left px-4 py-3 rounded-md flex items-center space-x-2 ${
                activeTab === 'privacy' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Shield className="w-5 h-5" />
              <span>Privacy</span>
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`w-full text-left px-4 py-3 rounded-md flex items-center space-x-2 ${
                activeTab === 'search' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Globe className="w-5 h-5" />
              <span>Search</span>
            </button>
            <button
              onClick={() => setActiveTab('budget')}
              className={`w-full text-left px-4 py-3 rounded-md flex items-center space-x-2 ${
                activeTab === 'budget' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <DollarSign className="w-5 h-5" />
              <span>Budget</span>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {activeTab === 'privacy' && <PrivacyTab />}
            {activeTab === 'search' && <SearchTab />}
            {activeTab === 'budget' && <BudgetTab />}
          </div>
        </div>
      </div>
    </div>
  );
};

const PrivacyTab: React.FC = () => {
  const [settings, setSettings] = useState<PrivacySettings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ApiService.getPrivacySettings().then(setSettings).finally(() => setLoading(false));
  }, []);

  const update = async (key: keyof PrivacySettings, value: any) => {
    if (!settings) return;
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    await ApiService.updatePrivacySettings(newSettings);
  };

  if (loading || !settings) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Privacy & Data</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Privacy Level</label>
          <select
            value={settings.privacy_level}
            onChange={(e) => update('privacy_level', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
          >
            <option value="local_only">Local Only (Maximum Privacy)</option>
            <option value="balanced">Balanced</option>
            <option value="performance">Performance</option>
          </select>
          <p className="mt-1 text-sm text-gray-500">
            {settings.privacy_level === 'local_only' 
              ? 'No data ever leaves your device.'
              : 'Some data may be sent to external services (redacted).'}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Redaction Aggressiveness</label>
          <select
            value={settings.redact_aggressiveness}
            onChange={(e) => update('redact_aggressiveness', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
          >
            <option value="standard">Standard (Names, Phones, Emails)</option>
            <option value="strict">Strict (Aggressive scrubbing)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Data Retention (Days)</label>
          <input
            type="number"
            value={settings.data_retention_days}
            onChange={(e) => update('data_retention_days', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
          />
        </div>
      </div>
    </div>
  );
};

const BudgetTab: React.FC = () => {
  const [status, setStatus] = useState<BudgetStatus | null>(null);

  useEffect(() => {
    ApiService.getBudgetStatus().then(setStatus);
  }, []);

  if (!status) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Cost & Budget</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg border">
          <div className="text-sm text-gray-500">Daily Spend</div>
          <div className="text-2xl font-bold text-gray-900">${status.daily_cost_usd.toFixed(4)}</div>
          <div className="text-xs text-gray-500">Limit: ${status.daily_limit_usd}</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border">
          <div className="text-sm text-gray-500">Monthly Spend</div>
          <div className="text-2xl font-bold text-gray-900">${status.monthly_cost_usd.toFixed(4)}</div>
          <div className="text-xs text-gray-500">Limit: ${status.monthly_limit_usd}</div>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${status.enforce ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-sm font-medium">Budget Enforcement is {status.enforce ? 'Active' : 'Disabled'}</span>
      </div>
    </div>
  );
};

const SearchTab: React.FC = () => {
  // Currently search providers are env vars, not runtime configurable per user in this version
  // This is a placeholder for future runtime config
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Search Providers</h3>
      <p className="text-gray-500">
        Search providers are currently configured via environment variables.
      </p>
      
      <div className="space-y-2 opacity-50 cursor-not-allowed">
        {['Bing', 'Google', 'Tavily'].map(p => (
          <div key={p} className="flex items-center justify-between p-3 border rounded-md">
            <span>{p}</span>
            <div className="w-10 h-6 bg-blue-100 rounded-full relative">
              <div className="w-4 h-4 bg-blue-500 rounded-full absolute right-1 top-1"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
