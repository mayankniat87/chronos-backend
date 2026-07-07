import { create } from 'zustand';
import { SimulationResponse } from '@/types';

interface SimulationState {
  currentSimulation: SimulationResponse | null;
  isSimulating: boolean;
  activeScenario: 'optimistic' | 'likely' | 'pessimistic';
  comparisonMode: boolean;
  setCurrentSimulation: (simulation: SimulationResponse | null) => void;
  setIsSimulating: (isSimulating: boolean) => void;
  setActiveScenario: (scenario: 'optimistic' | 'likely' | 'pessimistic') => void;
  setComparisonMode: (enabled: boolean) => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
  currentSimulation: null,
  isSimulating: false,
  activeScenario: 'likely',
  comparisonMode: false,
  setCurrentSimulation: (simulation) => set({ currentSimulation: simulation }),
  setIsSimulating: (isSimulating) => set({ isSimulating }),
  setActiveScenario: (activeScenario) => set({ activeScenario }),
  setComparisonMode: (comparisonMode) => set({ comparisonMode }),
}));
