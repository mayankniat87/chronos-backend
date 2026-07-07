import apiClient from './api';
import { DecisionHistory } from '@/types';
import { useSettingsStore } from '@/store/settingsStore';

export const historyService = {
  getDecisionHistory: async (restaurantId: string): Promise<DecisionHistory[]> => {
    const isDemo = useSettingsStore.getState().demoMode;

    if (isDemo) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([
            {
              id: 'hist_01',
              restaurantId,
              timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
              question: 'Raise premium wines and domestic beer menu pricing by 12% across weekday dinner operations.',
              decisionType: 'pricing',
              scenarioChosen: 'Likely',
              simulatedImpact: 'Projected +3.4% revenue increase with a confidence interval of 89%.',
              outcomeMetric: 'Actual: +3.1% revenue captured in initial 48h, zero noticeable customer complaints.',
              status: 'implemented',
              details: 'Implemented in core register nodes. Beverage revenue increased from $3,450 to $3,556 average per evening. Table turnaround time held steady at 54 minutes.',
            },
            {
              id: 'hist_02',
              restaurantId,
              timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
              question: 'Reduce kitchen prep hours by 1.5h during slower Tuesday lunch shifts.',
              decisionType: 'staffing',
              scenarioChosen: 'Optimistic',
              simulatedImpact: 'Projected $450/week savings in labor costs with minimal impact on prep quality.',
              outcomeMetric: 'Actual: Saved $480 in weekly payroll, but prep backlog created a 4-minute delay on initial orders.',
              status: 'implemented',
              details: 'Prep schedule changed for Tuesday AM shifts. Kitchen staff reported mild rush stress during 12:15 PM peaks, leading to recommendation to keep shift duration but optimize prep workflow layout instead.',
            },
            {
              id: 'hist_03',
              restaurantId,
              timestamp: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(), // 12 days ago
              question: 'Set inventory safety buffers on fresh seafood nodes to 35% to offset supplier logistics delays.',
              decisionType: 'inventory',
              scenarioChosen: 'Pessimistic',
              simulatedImpact: 'Prevented out-of-stock events on cod/salmon, but increased food waste risk by 6.2%.',
              outcomeMetric: 'Simulation complete. Risk index evaluated at 58/100.',
              status: 'simulated',
              details: 'Simulation remains stored in sandbox memory. Manager chose not to implement because the local shipping lane weather warning was cleared early.',
            },
            {
              id: 'hist_04',
              restaurantId,
              timestamp: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
              question: 'Execute a hyper-local social media promo spend of $800 targeting neighborhood office workers.',
              decisionType: 'marketing',
              scenarioChosen: 'Likely',
              simulatedImpact: 'Projected +15% seating utilization on Tuesday and Thursday lunch service.',
              outcomeMetric: 'Actual: Yielded +18% increase in ticket volume and added 114 new guest profiles to our CRM.',
              status: 'implemented',
              details: 'Campaign run across meta platforms with geotargeted radius. Successfully increased off-peak utilization and average margins due to beverage attachment rate.',
            },
          ]);
        }, 800);
      });
    }

    const response = await apiClient.get<DecisionHistory[]>(`/decisions/history/${restaurantId}`);
    return response.data;
  },
};
