import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Cpu, 
  ArrowRight, 
  DollarSign, 
  Database, 
  MessageSquare, 
  Settings, 
  Activity,
  Shield,
  Zap,
  Cloud,
  Server,
  AlertTriangle,
  CheckCircle,
  Play,
  TrendingUp,
  Users
} from 'lucide-react';

// Import enhanced components
import HardwareDetection from '@/components/HardwareDetection';
import RoutingEngine from '@/components/RoutingEngine';
import BudgetDashboard from '@/components/BudgetDashboard';
import MemoryStore from '@/components/MemoryStore';
import EnhancedChatInterface from '@/components/EnhancedChatInterface';
import DemoScenarios from '@/components/DemoScenarios';

// Import data types and backend
import { HardwareProfile, hardwareProfiles, systemHealth } from '@/lib/systemData';
import { mockBackend } from '@/lib/mockBackend';

export default function Index() {
  const [selectedProfile, setSelectedProfile] = useState<HardwareProfile | null>(null);
  const [currentMode, setCurrentMode] = useState<'assistant' | 'coding' | 'search'>('assistant');
  const [privacyLevel, setPrivacyLevel] = useState<'local-only' | 'cloud-allowed' | 'external-ok'>('cloud-allowed');
  const [activeTab, setActiveTab] = useState('overview');
  const [budgetData, setBudgetData] = useState(mockBackend.getBudgetData());
  const [routingHistory, setRoutingHistory] = useState(mockBackend.getRoutingHistory());
  const [demoResults, setDemoResults] = useState<any>(null);

  // Auto-select a default profile for demo purposes
  useEffect(() => {
    if (!selectedProfile) {
      setSelectedProfile(hardwareProfiles[1]); // Default to medium profile
    }
  }, [selectedProfile]);

  // Update data from backend periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setBudgetData(mockBackend.getBudgetData());
      setRoutingHistory(mockBackend.getRoutingHistory());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getSystemHealthStatus = () => {
    const { overall, components } = systemHealth;
    const degradedCount = Object.values(components).filter(status => status === 'degraded').length;
    const offlineCount = Object.values(components).filter(status => status === 'offline').length;
    
    if (offlineCount > 0) return 'critical';
    if (degradedCount > 0) return 'warning';
    return 'healthy';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-50 border-green-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPrivacyLevelColor = (level: string) => {
    switch (level) {
      case 'local-only': return 'text-red-600 bg-red-50';
      case 'cloud-allowed': return 'text-yellow-600 bg-yellow-50';
      case 'external-ok': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getBudgetStatus = () => {
    const dailyUsage = (budgetData.daily.used / budgetData.daily.limit) * 100;
    if (dailyUsage > 90) return 'critical';
    if (dailyUsage > 70) return 'warning';
    return 'healthy';
  };

  const calculateTotalSavings = () => {
    const totalSpent = budgetData.daily.used;
    const cloudOnlyEstimate = totalSpent * 3.5; // Estimated 3.5x cost for cloud-only
    const savings = cloudOnlyEstimate - totalSpent;
    const savingsPercentage = totalSpent > 0 ? (savings / cloudOnlyEstimate) * 100 : 0;
    return { savings, savingsPercentage };
  };

  const handleBudgetUpdate = (newBudgetData: any) => {
    setBudgetData(newBudgetData);
  };

  const handleScenarioComplete = (results: any) => {
    setDemoResults(results);
  };

  const { savings, savingsPercentage } = calculateTotalSavings();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Hybrid Local-First AI Architecture
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Working Proof of Concept - Intelligent routing, privacy-first processing, 
            and budget governance with real-time demonstrations
          </p>
          <Badge className="bg-green-100 text-green-800 px-4 py-2">
            <CheckCircle className="h-4 w-4 mr-2" />
            Live POC - Fully Interactive
          </Badge>
        </div>

        {/* Real-time System Status Bar */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                <span className="font-medium">System Status:</span>
                <Badge className={getStatusColor(getSystemHealthStatus())}>
                  {getSystemHealthStatus().toUpperCase()}
                </Badge>
              </div>
              
              {selectedProfile && (
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4" />
                  <span className="text-sm">Hardware:</span>
                  <Badge variant="outline">{selectedProfile.type.toUpperCase()}</Badge>
                </div>
              )}
              
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                <span className="text-sm">Privacy:</span>
                <Badge className={getPrivacyLevelColor(privacyLevel)}>
                  {privacyLevel.replace('-', ' ').toUpperCase()}
                </Badge>
              </div>

              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                <span className="text-sm">Budget:</span>
                <Badge className={getStatusColor(getBudgetStatus())}>
                  ${budgetData.daily.remaining.toFixed(2)} remaining
                </Badge>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPrivacyLevel(
                  privacyLevel === 'local-only' ? 'cloud-allowed' :
                  privacyLevel === 'cloud-allowed' ? 'external-ok' : 'local-only'
                )}
              >
                <Shield className="h-4 w-4 mr-2" />
                Toggle Privacy
              </Button>
              <Button variant="outline" size="sm" onClick={() => setActiveTab('demo')}>
                <Play className="h-4 w-4 mr-2" />
                Run Demo
              </Button>
            </div>
          </div>
        </Card>

        {/* Live Metrics Dashboard */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">Cost Savings</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {savingsPercentage.toFixed(0)}%
            </div>
            <div className="text-xs text-muted-foreground">
              ${savings.toFixed(2)} saved vs cloud-only
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <ArrowRight className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Total Queries</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {routingHistory.length}
            </div>
            <div className="text-xs text-muted-foreground">
              {routingHistory.filter(r => r.route === 'local').length} local, {routingHistory.filter(r => r.route !== 'local').length} cloud
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium">Memory Snippets</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {mockBackend.getMemorySnippets().length}
            </div>
            <div className="text-xs text-muted-foreground">
              Auto-saved from sessions
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-4 w-4 text-orange-600" />
              <span className="text-sm font-medium">Privacy Score</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {privacyLevel === 'local-only' ? '100' : privacyLevel === 'cloud-allowed' ? '85' : '70'}%
            </div>
            <div className="text-xs text-muted-foreground">
              Based on current settings
            </div>
          </Card>
        </div>

        {/* Main Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="chat">Live Chat</TabsTrigger>
            <TabsTrigger value="demo">Demo Scenarios</TabsTrigger>
            <TabsTrigger value="routing">Routing Engine</TabsTrigger>
            <TabsTrigger value="budget">Budget Dashboard</TabsTrigger>
            <TabsTrigger value="memory">Memory Store</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-6">
            {/* Hardware Detection */}
            <HardwareDetection
              onProfileSelected={setSelectedProfile}
              selectedProfile={selectedProfile}
            />

            {/* Key Features Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-green-600" />
                  Intelligent Routing
                </h3>
                <p className="text-muted-foreground mb-4">
                  Real-time routing decisions based on hardware capability, privacy settings, and budget constraints.
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Local Processing:</span>
                    <Badge variant="outline">{routingHistory.filter(r => r.route === 'local').length} queries</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Cloud-Small:</span>
                    <Badge variant="outline">{routingHistory.filter(r => r.route === 'cloud-small').length} queries</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Cloud-Large:</span>
                    <Badge variant="outline">{routingHistory.filter(r => r.route === 'cloud-large').length} queries</Badge>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  Privacy-First Design
                </h3>
                <p className="text-muted-foreground mb-4">
                  Sensitive data stays local by default with intelligent escalation policies.
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Current Level:</span>
                    <Badge className={getPrivacyLevelColor(privacyLevel)}>
                      {privacyLevel.replace('-', ' ')}
                    </Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Local Processing:</span>
                    <Badge variant="outline">
                      {Math.round((routingHistory.filter(r => r.route === 'local').length / Math.max(1, routingHistory.length)) * 100)}%
                    </Badge>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="chat">
            {selectedProfile ? (
              <EnhancedChatInterface
                currentMode={currentMode}
                hardwareProfile={selectedProfile}
                privacyLevel={privacyLevel}
                onModeChange={setCurrentMode}
                onBudgetUpdate={handleBudgetUpdate}
              />
            ) : (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Please select a hardware profile first to use the chat interface.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="demo">
            <DemoScenarios onScenarioComplete={handleScenarioComplete} />
          </TabsContent>
          
          <TabsContent value="routing">
            {selectedProfile ? (
              <RoutingEngine
                hardwareProfile={selectedProfile}
                currentMode={currentMode}
                privacyLevel={privacyLevel}
              />
            ) : (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Please select a hardware profile first to view routing decisions.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="budget">
            <BudgetDashboard currentBudget={budgetData} />
          </TabsContent>
          
          <TabsContent value="memory">
            <MemoryStore />
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <Card className="p-4 text-center">
          <p className="text-sm text-muted-foreground">
            Hybrid Local-First AI Architecture - Working Proof of Concept
          </p>
          <div className="flex justify-center gap-4 mt-2">
            <Badge variant="outline">✓ Real-time Routing</Badge>
            <Badge variant="outline">✓ Budget Tracking</Badge>
            <Badge variant="outline">✓ Privacy Controls</Badge>
            <Badge variant="outline">✓ Interactive Demos</Badge>
          </div>
        </Card>
      </div>
    </div>
  );
}