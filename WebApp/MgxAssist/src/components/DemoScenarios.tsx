import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  TrendingDown, 
  Shield, 
  Zap, 
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { mockBackend } from '@/lib/mockBackend';

interface Scenario {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  steps: ScenarioStep[];
  category: 'routing' | 'privacy' | 'budget' | 'performance';
}

interface ScenarioStep {
  title: string;
  description: string;
  action: () => Promise<void>;
  expectedOutcome: string;
}

interface DemoScenariosProps {
  onScenarioComplete: (results: any) => void;
}

export default function DemoScenarios({ onScenarioComplete }: DemoScenariosProps) {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [scenarioResults, setScenarioResults] = useState<any[]>([]);

  const scenarios: Scenario[] = [
    {
      id: 'cost-optimization',
      title: 'Cost Optimization Demo',
      description: 'Demonstrate how routing saves costs vs. cloud-only approach',
      icon: <TrendingDown className="h-5 w-5" />,
      category: 'budget',
      steps: [
        {
          title: 'Reset Budget Tracking',
          description: 'Start with fresh budget to track savings',
          action: async () => {
            mockBackend.resetBudget();
            await new Promise(resolve => setTimeout(resolve, 500));
          },
          expectedOutcome: 'Budget reset to $2.00 daily limit'
        },
        {
          title: 'Process Simple Query Locally',
          description: 'Handle basic question with local processing',
          action: async () => {
            await mockBackend.processQuery(
              'What is React?',
              'assistant',
              { id: 'heavy-1', name: 'High-Performance Workstation', type: 'heavy', capabilities: { npu: true, gpu: 'RTX 4090', cpu: 'i9-13900K', ram: 64 }, localModels: ['Llama-70B'], preferredRoutes: ['local'] },
              'cloud-allowed'
            );
          },
          expectedOutcome: 'Cost: $0.00 (local processing)'
        },
        {
          title: 'Calculate Total Savings',
          description: 'Show cost comparison vs. cloud-only approach',
          action: async () => {
            const budget = mockBackend.getBudgetData();
            const totalUsed = budget.daily.used;
            const cloudOnlyEstimate = totalUsed * 3.5;
            setScenarioResults([
              { label: 'Hybrid Approach Cost', value: `$${totalUsed.toFixed(2)}` },
              { label: 'Cloud-Only Estimate', value: `$${cloudOnlyEstimate.toFixed(2)}` },
              { label: 'Savings', value: `$${(cloudOnlyEstimate - totalUsed).toFixed(2)}` }
            ]);
            await new Promise(resolve => setTimeout(resolve, 1000));
          },
          expectedOutcome: 'Demonstrates 60-80% cost savings with intelligent routing'
        }
      ]
    },
    {
      id: 'privacy-escalation',
      title: 'Privacy-First Processing',
      description: 'Show how sensitive data stays local while allowing cloud escalation',
      icon: <Shield className="h-5 w-5" />,
      category: 'privacy',
      steps: [
        {
          title: 'Process Sensitive Data Locally',
          description: 'Handle confidential information with local-only processing',
          action: async () => {
            await mockBackend.processQuery(
              'Review this confidential document',
              'assistant',
              { id: 'heavy-1', name: 'High-Performance Workstation', type: 'heavy', capabilities: { npu: true, gpu: 'RTX 4090', cpu: 'i9-13900K', ram: 64 }, localModels: ['Llama-70B'], preferredRoutes: ['local'] },
              'local-only'
            );
          },
          expectedOutcome: 'Processed locally, no data sent to cloud'
        },
        {
          title: 'Process General Query with Cloud',
          description: 'Allow cloud processing for non-sensitive information',
          action: async () => {
            await mockBackend.processQuery(
              'What are React best practices?',
              'coding',
              { id: 'medium-1', name: 'Gaming Laptop', type: 'medium', capabilities: { npu: false, gpu: 'RTX 4060', cpu: 'Ryzen 7', ram: 32 }, localModels: ['Mistral-7B'], preferredRoutes: ['cloud-small'] },
              'cloud-allowed'
            );
          },
          expectedOutcome: 'Routed to cloud-small for enhanced capabilities'
        }
      ]
    },
    {
      id: 'budget-enforcement',
      title: 'Budget Cap Enforcement',
      description: 'Show how budget limits prevent overspending',
      icon: <DollarSign className="h-5 w-5" />,
      category: 'budget',
      steps: [
        {
          title: 'Simulate High Usage',
          description: 'Set budget to near-limit state',
          action: async () => {
            mockBackend.simulateHighUsage();
            await new Promise(resolve => setTimeout(resolve, 500));
          },
          expectedOutcome: 'Budget at 85% of daily limit'
        },
        {
          title: 'Demonstrate Budget Protection',
          description: 'Show system prevents overspending',
          action: async () => {
            const budget = mockBackend.getBudgetData();
            setScenarioResults([
              { label: 'Budget Status', value: 'Near limit (85% used)' },
              { label: 'Protection', value: 'Automatic cost monitoring active' },
              { label: 'Remaining', value: `$${budget.daily.remaining.toFixed(2)}` }
            ]);
          },
          expectedOutcome: 'Budget protection mechanisms active'
        }
      ]
    }
  ];

  const runScenario = async (scenario: Scenario) => {
    setActiveScenario(scenario.id);
    setIsRunning(true);
    setCurrentStep(0);
    setScenarioResults([]);

    for (let i = 0; i < scenario.steps.length; i++) {
      setCurrentStep(i);
      await scenario.steps[i].action();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    setIsRunning(false);
    onScenarioComplete(scenarioResults);
  };

  const resetScenario = () => {
    setActiveScenario(null);
    setCurrentStep(0);
    setIsRunning(false);
    setScenarioResults([]);
    mockBackend.resetBudget();
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'budget': return 'text-green-600 bg-green-50';
      case 'privacy': return 'text-red-600 bg-red-50';
      case 'performance': return 'text-blue-600 bg-blue-50';
      case 'routing': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="h-5 w-5" />
          Interactive Demo Scenarios
        </CardTitle>
        <CardDescription>
          Explore key features through guided demonstrations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Scenario Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {scenarios.map((scenario) => (
              <Card 
                key={scenario.id}
                className={`cursor-pointer transition-all ${
                  activeScenario === scenario.id ? 'ring-2 ring-primary' : 'hover:shadow-md'
                }`}
                onClick={() => !isRunning && runScenario(scenario)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-muted">
                      {scenario.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">{scenario.title}</h3>
                      <p className="text-sm text-muted-foreground mb-2">
                        {scenario.description}
                      </p>
                      <Badge className={getCategoryColor(scenario.category)}>
                        {scenario.category}
                      </Badge>
                    </div>
                  </div>
                  
                  {activeScenario === scenario.id && (
                    <div className="mt-4 pt-3 border-t">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Progress</span>
                        <span className="text-sm text-muted-foreground">
                          {currentStep + 1} / {scenario.steps.length}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ width: `${((currentStep + 1) / scenario.steps.length) * 100}%` }}
                        />
                      </div>
                      
                      {isRunning && (
                        <div className="mt-3">
                          <div className="flex items-center gap-2 text-sm">
                            <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                            <span>{scenario.steps[currentStep]?.title}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Active Scenario Details */}
          {activeScenario && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    {scenarios.find(s => s.id === activeScenario)?.title}
                  </CardTitle>
                  <div className="flex gap-2">
                    {isRunning ? (
                      <Button variant="outline" size="sm" disabled>
                        <Pause className="h-4 w-4 mr-2" />
                        Running...
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={resetScenario}>
                        <RotateCcw className="h-4 w-4 mr-2" />
                        Reset
                      </Button>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scenarios.find(s => s.id === activeScenario)?.steps.map((step, index) => (
                    <div 
                      key={index}
                      className={`flex items-start gap-3 p-3 rounded-lg ${
                        index < currentStep ? 'bg-green-50' :
                        index === currentStep ? 'bg-blue-50' :
                        'bg-gray-50'
                      }`}
                    >
                      <div className="mt-1">
                        {index < currentStep ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : index === currentStep && isRunning ? (
                          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{step.title}</h4>
                        <p className="text-sm text-muted-foreground mb-1">
                          {step.description}
                        </p>
                        <p className="text-sm text-green-600">
                          Expected: {step.expectedOutcome}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Results Display */}
                {scenarioResults.length > 0 && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      Scenario Results
                    </h4>
                    <div className="space-y-2">
                      {scenarioResults.map((result, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span className="font-medium">{result.label}:</span>
                          <span>{result.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Quick Demo Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Demo Actions</CardTitle>
              <CardDescription>
                Instantly demonstrate key system behaviors
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => mockBackend.simulateHighUsage()}
                  className="gap-2"
                >
                  <AlertTriangle className="h-4 w-4" />
                  High Usage
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => mockBackend.resetBudget()}
                  className="gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset Budget
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => mockBackend.simulateNetworkIssues()}
                  className="gap-2"
                >
                  <AlertTriangle className="h-4 w-4" />
                  Network Issues
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => mockBackend.simulateBudgetExceeded()}
                  className="gap-2"
                >
                  <DollarSign className="h-4 w-4" />
                  Budget Exceeded
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  );
}