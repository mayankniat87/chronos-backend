import apiClient from './api';
import { SimulationRequest, SimulationResponse } from '@/types';
import { useSettingsStore } from '@/store/settingsStore';

export const simulationService = {
  simulateDecision: async (request: SimulationRequest): Promise<SimulationResponse> => {
    const isDemo = useSettingsStore.getState().demoMode;

    if (isDemo) {
      return new Promise<SimulationResponse>((resolve) => {
        setTimeout(() => {
          const factor = request.parameters.factorChange;
          const type = request.decisionType;

          // Generate rich tailored mock data based on input type
          const optimisticRev = 8 + factor * 0.3;
          const likelyRev = 3 + factor * 0.15;
          const pessimisticRev = -2 - factor * 0.1;

          let rec = 'Approved with strict monitoring controls.';
          let insights = ['High probability of immediate margin capture.', 'Potential short-term traffic dampening.'];

          if (type === 'pricing') {
            rec = `Implement a staggered ${factor}% increase on high-margin beverages, backed by dynamic weekday evening pricing. Avoid raising prices on main lunch entrees to prevent quick-service customer churn.`;
            insights = [
              `A ${factor}% price shift captures immediate margins, but could cause a 3-5% drop in table turnaround frequencies during off-peak hours.`,
              'Cocktails and craft beers hold high price elasticity; menu items in the comfort food category do not.',
              'Competitor pricing index within 2km indicates we remain 8% cheaper on premium items.'
            ];
          } else if (type === 'staffing') {
            rec = `Deploy a flexible hybrid shift model. Adjust scheduling buffer by ${factor}% to match historic foot traffic patterns during Friday-Sunday dinner peaks.`;
            insights = [
              'Under-staffing risks customer wait times increasing by 4.2 minutes per order.',
              'Over-staffing reduces weekly margin contribution by approximately $2,400.'
            ];
          } else if (type === 'inventory') {
            rec = `Set inventory trigger points to ${factor}% buffer. Transition secondary fresh produce lines to local supplier node "LocFruit Inc" to offset logistics volatility.`;
            insights = [
              'Reducing safety stock buffers mitigates holding waste by $1,800 monthly.',
              'Severe supplier delay risks a 12% recipe substitution frequency.'
            ];
          }

          resolve({
            id: `sim_${Math.random().toString(36).substr(2, 9)}`,
            restaurantId: request.restaurantId,
            timestamp: new Date().toISOString(),
            decisionType: request.decisionType,
            horizonMonths: request.horizonMonths,
            keyInsights: insights,
            scenarios: {
              optimistic: {
                title: 'Optimistic',
                revenueChangePct: parseFloat(optimisticRev.toFixed(1)),
                profit: Math.round(45000 + (factor * 850)),
                riskScore: Math.max(10, Math.round(30 - factor * 0.5)),
                inventoryHealthPct: 92,
                staffUtilizationPct: 84,
                confidenceScore: 78,
                recommendation: rec,
                evidence: [
                  'High tourist foot traffic projections for the upcoming quarter.',
                  'Successful pricing pilot implemented in our West End venue last spring.',
                  'Sustained 94% customer satisfaction ratings in premium dining.'
                ],
                assumptions: [
                  'Competitor price indices remain stagnant.',
                  'Supply chain costs do not rise above 2.5% inflation.'
                ],
                limitations: [
                  'Does not account for catastrophic seasonal weather anomalies.',
                  'Local parking infrastructure construction starting next month is excluded.'
                ],
                details: 'In this scenario, customer response is highly receptive, and order frequencies sustain their historical trends despite changes.'
              },
              likely: {
                title: 'Likely',
                revenueChangePct: parseFloat(likelyRev.toFixed(1)),
                profit: Math.round(38000 + (factor * 450)),
                riskScore: Math.round(45 + factor * 0.2),
                inventoryHealthPct: 88,
                staffUtilizationPct: 76,
                confidenceScore: 89,
                recommendation: rec,
                evidence: [
                  'Historically stable elasticities computed from 18 months of ticket data.',
                  'Strong seasonal alignment in ordering patterns across our core menu.'
                ],
                assumptions: [
                  'Average order ticket value holds stable at $42.50.',
                  'Core ingredients supply chains do not face unexpected disruptions.'
                ],
                limitations: [
                  'Confidence levels taper beyond the 3-month forecast horizon.'
                ],
                details: 'This scenario represents our baseline forecast. It indicates strong, steady profitability gains with a manageable risk footprint.'
              },
              pessimistic: {
                title: 'Pessimistic',
                revenueChangePct: parseFloat(pessimisticRev.toFixed(1)),
                profit: Math.round(29000 - (factor * 200)),
                riskScore: Math.min(95, Math.round(65 + factor * 0.8)),
                inventoryHealthPct: 74,
                staffUtilizationPct: 62,
                confidenceScore: 65,
                recommendation: 'Delay deployment or implement in a small, isolated test menu first.',
                evidence: [
                  'Consumer confidence indices showing marginal downtrends locally.',
                  'A 4% rise in price-sensitive customer feedback surveys over the last quarter.'
                ],
                assumptions: [
                  'Inflation index spikes by over 4.8%.',
                  'Competitors launch aggressive promotional discounts in response.'
                ],
                limitations: [
                  'Worst-case supply failure thresholds are unmapped.'
                ],
                details: 'Under this scenario, customers react negatively to price increases by trading down to lower-margin menu items or eating out less frequently.'
              }
            }
          });
        }, 1500);
      });
    }

    const response = await apiClient.post<SimulationResponse>('/decisions/simulate', request);
    return response.data;
  },
};
