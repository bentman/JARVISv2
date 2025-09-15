import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DollarSign, TrendingUp, AlertTriangle, Settings, Zap, Cloud, Server } from 'lucide-react';
import { budgetData, BudgetData } from '@/lib/systemData';
import { RoutingEngine, formatCurrency } from '@/lib/routingLogic';

interface BudgetDashboardProps {
  currentBudget?: BudgetData;
}

export default function BudgetDashboard({ currentBudget = budgetData }: BudgetDashboardProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  
  const budgetStatus = RoutingEngine.getBudgetStatus(currentBudget);
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-50 border-green-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const calculateUsagePercentage = (used: number, limit: number) => {
    return Math.min(100, (used / limit) * 100);
  };

  const getBurnRate = () => {
    const dailyUsed = currentBudget.daily.used;
    const hoursInDay = 24;
    const currentHour = new Date().getHours();
    const expectedUsage = (dailyUsed / Math.max(1, currentHour)) * hoursInDay;
    return expectedUsage;
  };

  const getRouteIcon = (route: string) => {
    switch (route) {
      case 'local': return <Zap className="h-4 w-4" />;
      case 'cloudSmall': return <Cloud className="h-4 w-4" />;
      case 'cloudLarge': return <Server className="h-4 w-4" />;
      default: return <DollarSign className="h-4 w-4" />;
    }
  };

  const getRouteLabel = (route: string) => {
    switch (route) {
      case 'local': return 'Local';
      case 'cloudSmall': return 'Cloud Small';
      case 'cloudLarge': return 'Cloud Large';
      case 'external': return 'External';
      default: return route;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5" />
          Budget Governance
        </CardTitle>
        <CardDescription>
          Track spending and manage resource allocation across routing tiers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="breakdown">Breakdown</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-6">
            {/* Status Alert */}
            {budgetStatus !== 'healthy' && (
              <Alert className={getStatusColor(budgetStatus)}>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  {budgetStatus === 'warning' 
                    ? 'Budget usage is approaching limits. Consider optimizing routing preferences.'
                    : 'Critical budget limits reached. Some features may be restricted.'
                  }
                </AlertDescription>
              </Alert>
            )}

            {/* Budget Overview Cards */}
            <div className="grid grid-cols-3 gap-4">
              {(['daily', 'weekly', 'monthly'] as const).map((period) => {
                const data = currentBudget[period];
                const percentage = calculateUsagePercentage(data.used, data.limit);
                
                return (
                  <Card key={period} className={`cursor-pointer transition-all ${selectedPeriod === period ? 'ring-2 ring-primary' : 'hover:shadow-md'}`} onClick={() => setSelectedPeriod(period)}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold capitalize">{period}</h3>
                        <Badge variant={percentage > 80 ? 'destructive' : percentage > 60 ? 'secondary' : 'default'}>
                          {Math.round(percentage)}%
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Used: {formatCurrency(data.used)}</span>
                          <span>Limit: {formatCurrency(data.limit)}</span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                        <div className="text-sm text-muted-foreground">
                          Remaining: {formatCurrency(data.remaining)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Burn Rate Analysis */}
            <Card className="p-4">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Burn Rate Analysis
              </h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {formatCurrency(getBurnRate())}
                  </div>
                  <div className="text-sm text-muted-foreground">Projected Daily Spend</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.round((currentBudget.monthly.remaining / (getBurnRate() || 0.01)))}
                  </div>
                  <div className="text-sm text-muted-foreground">Days Remaining</div>
                </div>
              </div>
            </Card>
          </TabsContent>
          
          <TabsContent value="breakdown" className="space-y-4">
            {/* Route Cost Breakdown */}
            <Card className="p-4">
              <h4 className="font-medium mb-4">Cost by Route Type</h4>
              <div className="space-y-3">
                {Object.entries(currentBudget.breakdown).map(([route, cost]) => {
                  const totalCost = Object.values(currentBudget.breakdown).reduce((sum, c) => sum + c, 0);
                  const percentage = totalCost > 0 ? (cost / totalCost) * 100 : 0;
                  
                  return (
                    <div key={route} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getRouteIcon(route)}
                        <span className="text-sm font-medium">{getRouteLabel(route)}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-24">
                          <Progress value={percentage} className="h-2" />
                        </div>
                        <div className="text-sm font-medium min-w-[60px] text-right">
                          {formatCurrency(cost)}
                        </div>
                        <div className="text-xs text-muted-foreground min-w-[40px] text-right">
                          {Math.round(percentage)}%
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Usage Patterns */}
            <Card className="p-4">
              <h4 className="font-medium mb-4">Usage Patterns</h4>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-green-600">47%</div>
                    <div className="text-sm text-muted-foreground">Local Processing</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-blue-600">38%</div>
                    <div className="text-sm text-muted-foreground">Cloud Small</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-purple-600">15%</div>
                    <div className="text-sm text-muted-foreground">Cloud Large</div>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>
          
          <TabsContent value="settings" className="space-y-4">
            <Card className="p-4">
              <h4 className="font-medium mb-4">Budget Limits</h4>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Daily Limit</label>
                    <div className="flex items-center gap-2 mt-1">
                      <input type="number" defaultValue={currentBudget.daily.limit} className="flex-1 px-3 py-2 border rounded text-sm" />
                      <span className="text-sm text-muted-foreground">USD</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Weekly Limit</label>
                    <div className="flex items-center gap-2 mt-1">
                      <input type="number" defaultValue={currentBudget.weekly.limit} className="flex-1 px-3 py-2 border rounded text-sm" />
                      <span className="text-sm text-muted-foreground">USD</span>
                    </div>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Monthly Limit</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input type="number" defaultValue={currentBudget.monthly.limit} className="flex-1 px-3 py-2 border rounded text-sm" />
                    <span className="text-sm text-muted-foreground">USD</span>
                  </div>
                </div>
                <Button className="w-full">Update Limits</Button>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}