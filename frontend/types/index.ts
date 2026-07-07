export interface Restaurant {
  id: string;
  name: string;
  location: string;
  type: string;
  cuisine?: string;
  status?: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  fileId: string;
  fileName: string;
  rowCount: number;
  columnsDetected: string[];
  validationErrors: string[];
  uploadedAt: string;
}

export interface SimulationRequest {
  restaurantId: string;
  decisionType: 'pricing' | 'staffing' | 'inventory' | 'marketing' | 'expansion' | 'general';
  parameters: {
    title: string;
    description: string;
    factorChange: number; // percentage or multiplier change, e.g. 10 for +10% price
    staffShiftHours?: number;
    inventoryBufferMultiplier?: number;
    marketingBudgetDelta?: number;
    targetItems?: string[];
  };
  horizonMonths: number;
}

export interface TimelineScenario {
  title: 'Optimistic' | 'Likely' | 'Pessimistic';
  revenueChangePct: number;
  profit: number;
  riskScore: number; // 0 to 100
  inventoryHealthPct: number; // 0 to 100
  staffUtilizationPct: number; // 0 to 100
  confidenceScore: number; // 0 to 100
  recommendation: string;
  evidence: string[];
  assumptions: string[];
  limitations: string[];
  details: string;
}

export interface SimulationResponse {
  id: string;
  restaurantId: string;
  timestamp: string;
  decisionType: string;
  horizonMonths: number;
  scenarios: {
    optimistic: TimelineScenario;
    likely: TimelineScenario;
    pessimistic: TimelineScenario;
  };
  keyInsights: string[];
}

export interface GraphNode {
  id: string;
  type: 'restaurant' | 'supplier' | 'inventory' | 'menu_item' | 'orders' | 'customers' | 'revenue';
  label: string;
  status?: 'normal' | 'warning' | 'critical';
  details: {
    title: string;
    metrics: Record<string, string | number>;
    description?: string;
    [key: string]: unknown;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
  type?: string;
}

export interface DecisionHistory {
  id: string;
  restaurantId: string;
  timestamp: string;
  question: string;
  decisionType: string;
  scenarioChosen: 'Optimistic' | 'Likely' | 'Pessimistic' | 'None';
  simulatedImpact: string;
  outcomeMetric: string;
  status: 'simulated' | 'implemented' | 'archived';
  details: string;
}

export interface HealthScore {
  score: number; // 0 to 100
  status: 'optimal' | 'stable' | 'degraded' | 'critical';
  timestamp: string;
  revenueTrend: number[];
  orderTrend: number[];
  inventoryTrend: number[];
  staffTrend: number[];
  metrics: {
    monthlyRevenue: number;
    monthlyOrders: number;
    inventoryShortages: number;
    staffTurnoverRate: number;
    averageOrderTimeMin: number;
  };
}
