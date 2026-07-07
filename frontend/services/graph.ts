import apiClient from './api';
import { GraphNode, GraphEdge } from '@/types';
import { useSettingsStore } from '@/store/settingsStore';

export const graphService = {
  getRestaurantGraph: async (restaurantId: string): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> => {
    const isDemo = useSettingsStore.getState().demoMode;

    if (isDemo) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Standard mock graph structure for restaurant intelligence
          const nodes: GraphNode[] = [
            {
              id: 'node_rest',
              type: 'restaurant',
              label: 'Bistro Downtown',
              status: 'normal',
              details: {
                title: 'Chronos Bistro - Downtown',
                metrics: {
                  'Active Staff': '14 / Shift',
                  'Daily Ticket Avg': '$48.50',
                  'Seating Capacity': '120 Seats',
                  'Occupancy Rate': '78%',
                },
                description: 'Flagship restaurant node representing downtown fine dining operations.',
              },
            },
            // Suppliers
            {
              id: 'node_sup_sysco',
              type: 'supplier',
              label: 'Sysco Logistics',
              status: 'normal',
              details: {
                title: 'Sysco Prime Distribution',
                metrics: {
                  'Lead Time': '24 Hours',
                  'On-Time Delivery': '98.5%',
                  'Weekly Orders': '3 Shipments',
                  'Active Contract': 'Tier 1 Preferred',
                },
                description: 'Primary broadline distributor sourcing dry goods, frozen inventory, and bulk supplies.',
              },
            },
            {
              id: 'node_sup_farm',
              type: 'supplier',
              label: 'GreenValley Farms',
              status: 'warning',
              details: {
                title: 'GreenValley Organic Co.',
                metrics: {
                  'Lead Time': '48 Hours',
                  'On-Time Delivery': '89.2%',
                  'Weekly Orders': '2 Shipments',
                  'Alert Status': 'Delays due to local rain storms',
                },
                description: 'Local boutique agricultural cooperative sourcing fresh heirloom tomatoes, microgreens, and organic produce.',
              },
            },
            // Inventories
            {
              id: 'node_inv_produce',
              type: 'inventory',
              label: 'Fresh Greens',
              status: 'warning',
              details: {
                title: 'Cold Storage Inventory: Produce',
                metrics: {
                  'Stock Level': '32% (Low)',
                  'Reorder Point': '40%',
                  'Days On Hand': '1.8 Days',
                  'Shrinkage Rate': '4.1%',
                },
                description: 'Perishable green vegetables, herbs, and soft fruits currently running below safety stock levels.',
              },
            },
            {
              id: 'node_inv_meat',
              type: 'inventory',
              label: 'Prime Cuts Storage',
              status: 'normal',
              details: {
                title: 'Meat & Seafood Freezer',
                metrics: {
                  'Stock Level': '76%',
                  'Days On Hand': '5.2 Days',
                  'Storage Temp': '-4°F',
                  'Asset Value': '$12,400',
                },
                description: 'Temperature-monitored holding cells containing center-of-plate proteins including dry-aged ribeye and salmon.',
              },
            },
            // Menu Items
            {
              id: 'node_menu_steak',
              type: 'menu_item',
              label: 'Dry-Aged Ribeye',
              status: 'normal',
              details: {
                title: '14oz Hand-Cut Ribeye',
                metrics: {
                  'Menu Price': '$52.00',
                  'Unit Cost': '$17.16 (33%)',
                  'Weekly Volume': '185 Plates',
                  'Popularity Rank': '#1 Dinner Entree',
                },
                description: 'Signature dry-aged prime beef steak served with truffle herb butter. High profit contribution.',
              },
            },
            {
              id: 'node_menu_salad',
              type: 'menu_item',
              label: 'Organic Harvest Salad',
              status: 'warning',
              details: {
                title: 'Local Harvest Greens Salad',
                metrics: {
                  'Menu Price': '$18.00',
                  'Unit Cost': '$4.50 (25%)',
                  'Weekly Volume': '240 Plates',
                  'Stock Risk': 'Linked to GreenValley shortages',
                },
                description: 'Light seasonal appetizer composed of organic baby greens, shaved goat cheese, and vinaigrette.',
              },
            },
            // Orders
            {
              id: 'node_ord_dinner',
              type: 'orders',
              label: 'Dinner Rush Trans.',
              status: 'normal',
              details: {
                title: 'PM Service Dine-In Transactions',
                metrics: {
                  'Active Checks': '28 Tables',
                  'Kitchen Load': '84%',
                  'Average Ticket': '$76.20',
                  'Peak Window': '6:30 PM - 9:00 PM',
                },
                description: 'Live order flows originating from evening dine-in guests.',
              },
            },
            // Customers
            {
              id: 'node_cust_locals',
              type: 'customers',
              label: 'Repeat Residents',
              status: 'normal',
              details: {
                title: 'Local neighborhood loyalists',
                metrics: {
                  'Retention Rate': '68%',
                  'Average Visit Rate': '2.4x / Month',
                  'Loyalty Members': '840 Enrolled',
                  'Feedback Rating': '4.8 / 5',
                },
                description: 'Local residents living within a 3-mile radius contributing to predictable baseline demand.',
              },
            },
            // Revenue
            {
              id: 'node_rev_main',
              type: 'revenue',
              label: 'Direct Register Rev',
              status: 'normal',
              details: {
                title: 'Point of Sale Merchant Processing',
                metrics: {
                  'Daily Gross': '$8,450',
                  'Credit Card Fees': '2.1%',
                  'Cash Share': '4.2%',
                  'Deposit Time': 'Next Day',
                },
                description: 'Primary cash and card collection streams settled directly through registers.',
              },
            },
          ];

          const edges: GraphEdge[] = [
            // Supplier -> Inventory
            { id: 'e_sys_meat', source: 'node_sup_sysco', target: 'node_inv_meat', label: 'Proteins Delivery', animated: false },
            { id: 'e_farm_produce', source: 'node_sup_farm', target: 'node_inv_produce', label: 'Organic Greens Delivery', animated: true },
            // Inventory -> Menu Items
            { id: 'e_meat_steak', source: 'node_inv_meat', target: 'node_menu_steak', label: 'Ingredient Link', animated: false },
            { id: 'e_prod_salad', source: 'node_inv_produce', target: 'node_menu_salad', label: 'Ingredient Link', animated: true },
            // Menu Items -> Orders
            { id: 'e_steak_ord', source: 'node_menu_steak', target: 'node_ord_dinner', label: 'Sales Flow', animated: false },
            { id: 'e_salad_ord', source: 'node_menu_salad', target: 'node_ord_dinner', label: 'Sales Flow', animated: false },
            // Orders -> Restaurant
            { id: 'e_ord_rest', source: 'node_ord_dinner', target: 'node_rest', label: 'Fulfillment', animated: true },
            // Customers -> Orders
            { id: 'e_cust_ord', source: 'node_cust_locals', target: 'node_ord_dinner', label: 'Demand Node', animated: false },
            // Restaurant -> Revenue
            { id: 'e_rest_rev', source: 'node_rest', target: 'node_rev_main', label: 'Cash Settlement', animated: true },
          ];

          resolve({ nodes, edges });
        }, 1000);
      });
    }

    const response = await apiClient.get<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/graph/${restaurantId}`);
    return response.data;
  },
};
