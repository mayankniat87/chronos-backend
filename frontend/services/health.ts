import apiClient from './api';
import { HealthScore } from '@/types';
import { useSettingsStore } from '@/store/settingsStore';

export const healthService = {
  getRestaurantHealth: async (restaurantId: string): Promise<HealthScore> => {
    const isDemo = useSettingsStore.getState().demoMode;

    if (isDemo) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Dynamic health models depending on selected restaurant
          let score = 88;
          let status: HealthScore['status'] = 'optimal';
          let shortages = 2;
          let turnover = 8;

          if (restaurantId === 'rest_02') {
            score = 74;
            status = 'stable';
            shortages = 6;
            turnover = 12;
          } else if (restaurantId === 'rest_03') {
            score = 54;
            status = 'degraded';
            shortages = 14;
            turnover = 21;
          }

          resolve({
            score,
            status,
            timestamp: new Date().toISOString(),
            revenueTrend: [45000, 48000, 52000, 49000, 51000, 55000, 58000],
            orderTrend: [920, 980, 1050, 940, 1010, 1120, 1180],
            inventoryTrend: [88, 86, 91, 84, 80, 89, 92],
            staffTrend: [94, 94, 92, 90, 88, 92, 94],
            metrics: {
              monthlyRevenue: 58000,
              monthlyOrders: 1180,
              inventoryShortages: shortages,
              staffTurnoverRate: turnover,
              averageOrderTimeMin: restaurantId === 'rest_03' ? 18.5 : 12.4,
            },
          });
        }, 500);
      });
    }

    const response = await apiClient.get<HealthScore>(`/health/${restaurantId}`);
    return response.data;
  },
};
