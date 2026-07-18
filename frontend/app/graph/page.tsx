'use client';

import React, { useEffect, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';

import { useQuery } from '@tanstack/react-query';
import { useRestaurantStore } from '@/store/restaurantStore';
import { useGraphStore } from '@/store/graphStore';
import { graphService } from '@/services/graph';
import CustomNode from '@/components/graph/CustomNode';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Info,
  RefreshCw,
  FolderLock
} from 'lucide-react';

const nodeTypes = {
  restaurant: CustomNode,
  supplier: CustomNode,
  inventory: CustomNode,
  menu_item: CustomNode,
  orders: CustomNode,
  customers: CustomNode,
  revenue: CustomNode,
};

export default function GraphPage() {
  const { selectedRestaurant } = useRestaurantStore();
  const restaurantId = selectedRestaurant?.id || 'rest_01';

  const {
    selectedNodeId,
    setSelectedNodeId,
    searchFilter,
    setSearchFilter,
    typeFilters,
    toggleTypeFilter
  } = useGraphStore();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // React Query fetching operational graph data
  const { data: graphData, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['restaurant-graph', restaurantId],
    queryFn: () => graphService.getRestaurantGraph(restaurantId),
    enabled: !!restaurantId,
  });

  // Distribute nodes dynamically across structural tiers
  useEffect(() => {
    if (!graphData) return;

    // Tiers mapping
    // Tier 1: suppliers (y=50)
    // Tier 2: inventory (y=180)
    // Tier 3: menu_item (y=310)
    // Tier 4: orders (y=440), customers (y=440)
    // Tier 5: restaurant (y=570)
    // Tier 6: revenue (y=700)
    const typeCount: Record<string, number> = {};

    const positionedNodes: Node[] = graphData.nodes.map((node) => {
      const type = node.type;
      if (!typeCount[type]) typeCount[type] = 0;
      const index = typeCount[type]++;

      let x = index * 240 + 100;
      let y = 300;

      if (type === 'supplier') {
        y = 50;
      } else if (type === 'inventory') {
        y = 180;
        x = index * 260 + 180;
      } else if (type === 'menu_item') {
        y = 310;
        x = index * 250 + 160;
      } else if (type === 'orders') {
        y = 440;
        x = 200;
      } else if (type === 'customers') {
        y = 440;
        x = 500;
      } else if (type === 'restaurant') {
        y = 570;
        x = 350;
      } else if (type === 'revenue') {
        y = 700;
        x = 350;
      }

      return {
        id: node.id,
        type: node.type,
        data: {
          label: node.label,
          type: node.type,
          status: node.status,
          details: node.details,
        },
        position: { x, y },
      };
    });

    const flowEdges: Edge[] = graphData.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: edge.animated,
      style: {
        stroke: edge.animated ? 'var(--primary)' : 'var(--edge-strong)',
      },
    }));

    setNodes(positionedNodes);
    setEdges(flowEdges);
  }, [graphData, setNodes, setEdges]);

  // Compute filtered nodes & edges
  const filteredNodes = useMemo(() => {
    return nodes.filter((node) => {
      const matchesSearch = node.data.label.toLowerCase().includes(searchFilter.toLowerCase());
      const matchesType = node.type ? typeFilters.includes(node.type) : false;
      return matchesSearch && matchesType;
    });
  }, [nodes, searchFilter, typeFilters]);

  // Handle graph node click selection
  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  };

  const onPaneClick = () => {
    setSelectedNodeId(null);
  };

  const activeNodeDetails = useMemo(() => {
    if (!selectedNodeId) return null;
    const match = nodes.find((n) => n.id === selectedNodeId);
    return match ? match.data : null;
  }, [selectedNodeId, nodes]);

  const categories = [
    { key: 'restaurant', color: 'bg-blue-500' },
    { key: 'supplier', color: 'bg-orange-500' },
    { key: 'inventory', color: 'bg-purple-500' },
    { key: 'menu_item', color: 'bg-cyan-500' },
    { key: 'orders', color: 'bg-yellow-500' },
    { key: 'customers', color: 'bg-teal-500' },
    { key: 'revenue', color: 'bg-emerald-500' },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] space-y-4 font-sans">
      
      {/* Search and filter controls toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-surface-deep/40 p-4 rounded-2xl border border-edge/80">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-faint">
              <Search className="h-4 w-4" />
            </span>
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search graph nodes..."
              className="pl-9 pr-4 py-2 w-56 text-xs rounded-xl glass-input text-strong"
            />
          </div>
          
          {/* Node Category Filters */}
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => {
              const active = typeFilters.includes(cat.key);
              return (
                <button
                  key={cat.key}
                  onClick={() => toggleTypeFilter(cat.key)}
                  className={`px-2.5 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer ${
                    active
                      ? 'bg-surface-2 border-edge-strong text-strong'
                      : 'border-transparent text-faint hover:text-muted'
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${cat.color}`} />
                  <span>{cat.key.replace('_', ' ')}</span>
                </button>
              );
            })}
          </div>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="p-2.5 rounded-xl border border-edge bg-surface/40 hover:bg-surface-2 text-muted hover:text-foreground transition-colors cursor-pointer"
          aria-label="Refresh operational metrics"
        >
          <RefreshCw className={`h-4.5 w-4.5 ${isFetching ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Main Canvas + Sidebar Panel */}
      <div className="flex-1 flex gap-6 relative min-h-0">
        
        {/* React Flow canvas */}
        <div className="flex-1 glass-card rounded-2xl border border-edge overflow-hidden relative">
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-surface-deep/60 z-10">
              <div className="flex flex-col items-center gap-3">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
                <p className="text-xs font-semibold text-blue-400">Loading graph matrix...</p>
              </div>
            </div>
          ) : (
            <ReactFlow
              nodes={filteredNodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodeClick={onNodeClick}
              onPaneClick={onPaneClick}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-right"
            >
              <Background color="var(--edge)" gap={24} size={1} />
              <Controls />
              <MiniMap nodeStrokeWidth={3} zoomable pannable />
            </ReactFlow>
          )}
        </div>

        {/* Sidebar Info Panel */}
        <AnimatePresence>
          {activeNodeDetails && (
            <motion.div
              initial={{ opacity: 0, x: 50, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 320 }}
              exit={{ opacity: 0, x: 50, width: 0 }}
              transition={{ type: 'spring', stiffness: 260, damping: 25 }}
              className="glass-panel w-80 rounded-2xl border border-edge p-6 flex flex-col justify-between overflow-y-auto"
            >
              <div className="space-y-6">
                <div className="flex items-center gap-2.5 border-b border-edge/80 pb-4">
                  <Info className="h-4.5 w-4.5 text-blue-400" />
                  <h3 className="text-sm font-bold font-outfit text-foreground uppercase tracking-wider">Node Inspector</h3>
                </div>

                <div>
                  <span className="text-[10px] text-faint font-bold uppercase tracking-widest block">{activeNodeDetails.type}</span>
                  <h2 className="text-lg font-bold font-outfit text-foreground mt-1 leading-tight">{activeNodeDetails.label}</h2>
                  <p className="text-xs text-muted mt-2 leading-relaxed">{activeNodeDetails.details.description || 'No custom description defined.'}</p>
                </div>

                {/* Metrics list */}
                <div className="space-y-3.5 pt-4 border-t border-edge">
                  <h4 className="text-[10px] font-bold text-faint uppercase tracking-widest">Active Metrics</h4>
                  {Object.entries(activeNodeDetails.details.metrics).map(([key, val]) => (
                    <div key={key} className="flex justify-between items-center text-xs py-1">
                      <span className="text-muted font-semibold">{key}</span>
                      <span className="text-strong font-mono font-medium">{String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-6 border-t border-edge mt-6 text-[10px] text-faint font-medium">
                <p className="flex items-center gap-1.5">
                  <FolderLock className="h-3.5 w-3.5" />
                  <span>State locked for simulation output comparisons.</span>
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
}
