import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowRight, Zap, Cloud, Server, Cpu, Shield, DollarSign, Clock, AlertTriangle } from 'lucide-react';
import { RoutingEngine as Engine, RoutingContext, RoutingDecision, Route, formatCurrency, formatLatency, getRouteColor, getRouteIcon } from '@/lib/routingLogic';
import { HardwareProfile, recentRoutes, systemHealth } from '@/lib/systemData';

interface RoutingEngineProps {
  hardwareProfile: HardwareProfile;
  currentMode: 'assistant' | 'coding' | 'search';
  privacyLevel: 'local-only' | 'cloud-allowed' | 'external-ok';
}

export default function RoutingEngineComponent({ hardwareProfile, currentMode, privacyLevel }: RoutingEngineProps) {
  const [currentDecision, setCurrentDecision] = useState<RoutingDecision | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [simulationInput, setSimulationInput] = useState('');

  const simulateRouting = async (inputText: string = 'Sample query for routing simulation') => {
    setIsProcessing(true);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const context: RoutingContext = {
      mode: currentMode,
      inputLength: inputText.length,
      contextSize: Math.random() * 5000 + 1000,
      privacyLevel,
      hardwareProfile,
      budget: {
        monthly: { limit: 50, used: 23.45, remaining: 26.55 },
        weekly: { limit: 12.5, used: 8.2, remaining: 4.3 },
        daily: { limit: 2, used: 1.15, remaining: 0.85 }
      },
      systemHealth
    };
    
    const decision = Engine.makeRoutingDecision(context);
    setCurrentDecision(decision);
    setIsProcessing(false);
  };

  useEffect(() => {
    // Auto-simulate on component mount or when key props change
    simulateRouting();
  }, [hardwareProfile, currentMode, privacyLevel]);

  const getRouteDisplayName = (route: Route) => {
    const names = {
      local: 'Local Processing',
      'cloud-small': 'Cloud Small',
      'cloud-large': 'Cloud Large'
    };
    return names[route];
  };

  const getPrivacyImpactColor = (impact: string) => {
    switch (impact) {
      case 'none': return 'text-green-600 bg-green-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowRight className="h-5 w-5" />
          Routing Engine
        </CardTitle>
        <CardDescription>
          Real-time routing decisions and policy visualization
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="current" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="current">Current Decision</TabsTrigger>
            <TabsTrigger value="history">Recent Routes</TabsTrigger>
          </TabsList>
          
          <TabsContent value="current" className="space-y-6">
            {/* Current Context */}
            <div className="grid grid-cols-3 gap-4">
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">Mode</span>
                </div>
                <Badge variant="outline" className="capitalize">
                  {currentMode}
                </Badge>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4 text-green-600" />
                  <span className="font-medium">Privacy</span>
                </div>
                <Badge variant="outline" className="capitalize">
                  {privacyLevel.replace('-', ' ')}
                </Badge>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="h-4 w-4 text-purple-600" />
                  <span className="font-medium">Hardware</span>
                </div>
                <Badge variant="outline" className="capitalize">
                  {hardwareProfile.type}
                </Badge>
              </Card>
            </div>

            {/* Routing Decision */}
            {isProcessing ? (
              <Card className="p-6">
                <div className="text-center space-y-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="text-sm font-medium">Analyzing routing options...</p>
                  <Progress value={66} className="w-full" />
                </div>
              </Card>
            ) : currentDecision && (
              <div className="space-y-4">
                {/* Recommended Route */}
                <Card className="p-6 border-2 border-primary">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Recommended Route</h3>
                    <Badge className="text-lg px-3 py-1">
                      {getRouteIcon(currentDecision.recommendedRoute)} {getRouteDisplayName(currentDecision.recommendedRoute)}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {Math.round(currentDecision.confidence * 100)}%
                      </div>
                      <div className="text-xs text-muted-foreground">Confidence</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {formatCurrency(currentDecision.estimatedCost)}
                      </div>
                      <div className="text-xs text-muted-foreground">Est. Cost</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {formatLatency(currentDecision.estimatedLatency)}
                      </div>
                      <div className="text-xs text-muted-foreground">Est. Latency</div>
                    </div>
                    <div className="text-center">
                      <Badge className={`${getPrivacyImpactColor(currentDecision.privacyImpact)} border-0`}>
                        {currentDecision.privacyImpact}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">Privacy Impact</div>
                    </div>
                  </div>
                  
                  {/* Reasoning */}
                  <div className="space-y-2">
                    <h4 className="font-medium">Decision Reasoning:</h4>
                    <ul className="space-y-1">
                      {currentDecision.reasoning.map((reason, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-center gap-2">
                          <div className="w-1 h-1 bg-primary rounded-full"></div>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card>

                {/* Alternative Routes */}
                <Card className="p-4">
                  <h4 className="font-medium mb-3">Alternative Routes</h4>
                  <div className="space-y-2">
                    {currentDecision.alternatives.map((alt, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                        <div className="flex items-center gap-2">
                          <span>{getRouteIcon(alt.route)}</span>
                          <span className="text-sm">{getRouteDisplayName(alt.route)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={alt.score * 100} className="w-16 h-2" />
                          <span className="text-sm text-muted-foreground">
                            {Math.round(alt.score * 100)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {/* Simulation Controls */}
            <Card className="p-4">
              <h4 className="font-medium mb-3">Test Routing Decision</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter a query to test routing..."
                  value={simulationInput}
                  onChange={(e) => setSimulationInput(e.target.value)}
                  className="flex-1 px-3 py-2 border rounded-md text-sm"
                />
                <Button 
                  onClick={() => simulateRouting(simulationInput || 'Test query')}
                  disabled={isProcessing}
                >
                  Test Route
                </Button>
              </div>
            </Card>
          </TabsContent>
          
          <TabsContent value="history" className="space-y-4">
            <div className="space-y-3">
              {recentRoutes.map((route, index) => (
                <Card key={route.id} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {route.mode}
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      <Badge className={getRouteColor(route.route)}>
                        {getRouteIcon(route.route)} {getRouteDisplayName(route.route)}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {route.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-3 w-3" />
                      {formatCurrency(route.cost)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatLatency(route.latency)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      {route.factors.privacy}
                    </div>
                    <div className="flex items-center gap-1">
                      {route.success ? (
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      ) : (
                        <AlertTriangle className="h-3 w-3 text-red-500" />
                      )}
                      {route.success ? 'Success' : 'Failed'}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}