import { create } from 'zustand';

interface GraphState {
  selectedNodeId: string | null;
  searchFilter: string;
  typeFilters: string[];
  setSelectedNodeId: (id: string | null) => void;
  setSearchFilter: (filter: string) => void;
  setTypeFilters: (filters: string[]) => void;
  toggleTypeFilter: (filter: string) => void;
  resetFilters: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  selectedNodeId: null,
  searchFilter: '',
  typeFilters: ['restaurant', 'supplier', 'inventory', 'menu_item', 'orders', 'customers', 'revenue'],
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  setSearchFilter: (searchFilter) => set({ searchFilter }),
  setTypeFilters: (typeFilters) => set({ typeFilters }),
  toggleTypeFilter: (filter) =>
    set((state) => ({
      typeFilters: state.typeFilters.includes(filter)
        ? state.typeFilters.filter((f) => f !== filter)
        : [...state.typeFilters, filter],
    })),
  resetFilters: () =>
    set({
      searchFilter: '',
      typeFilters: ['restaurant', 'supplier', 'inventory', 'menu_item', 'orders', 'customers', 'revenue'],
      selectedNodeId: null,
    }),
}));
