import { create } from 'zustand';
import { Restaurant } from '@/types';

interface RestaurantState {
  restaurants: Restaurant[];
  selectedRestaurant: Restaurant | null;
  setRestaurants: (restaurants: Restaurant[]) => void;
  setSelectedRestaurant: (restaurant: Restaurant | null) => void;
}

export const useRestaurantStore = create<RestaurantState>((set) => ({
  restaurants: [
    { id: 'rest_01', name: 'Chronos Bistro - Downtown', location: 'Downtown Core', type: 'Fine Dining', cuisine: 'French-Italian Mix', status: 'optimal' },
    { id: 'rest_02', name: 'Chronos Pizzeria - East End', location: 'Waterfront Plaza', type: 'Casual Dining', cuisine: 'Italian', status: 'stable' },
    { id: 'rest_03', name: 'Chronos Express - Tech Park', location: 'Silicon Avenue', type: 'Quick Service', cuisine: 'Salads & Bowls', status: 'degraded' },
  ],
  selectedRestaurant: { id: 'rest_01', name: 'Chronos Bistro - Downtown', location: 'Downtown Core', type: 'Fine Dining', cuisine: 'French-Italian Mix', status: 'optimal' },
  setRestaurants: (restaurants) => set({ restaurants }),
  setSelectedRestaurant: (restaurant) => set({ selectedRestaurant: restaurant }),
}));
