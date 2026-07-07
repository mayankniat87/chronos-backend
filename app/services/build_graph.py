import logging
import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models.restaurant import Restaurant, Supplier, InventoryItem, MenuItem, Customer, Order

logger = logging.getLogger(__name__)

def build_restaurant_graph(restaurant_id: int, db: Session):
    """
    Builds a NetworkX DiGraph and a React Flow JSON payload for a restaurant.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
       logger.warning(f"Restaurant with ID    {restaurant_id} not found while building graph.")
       return None, None
    G = nx.DiGraph()
    nodes = []
    edges = []

    def add_node(node_id, node_type, data):
        if not G.has_node(node_id):
            G.add_node(node_id, type=node_type, **data)
            nodes.append({"id": node_id, "type": node_type, "data": data})

    def add_edge(source_id, target_id, label):
        edge_id = f"e_{source_id}_{target_id}"
        if not G.has_edge(source_id, target_id):
            G.add_edge(source_id, target_id, label=label)
            edges.append({"id": edge_id, "source": source_id, "target": target_id, "label": label})

    # 1. Restaurant
    res_id = f"res_{restaurant.id}"
    add_node(res_id, "restaurant", {"label": restaurant.name})

    # 2. Suppliers
    suppliers = db.query(Supplier).filter(Supplier.restaurant_id == restaurant_id).all()
    for sup in suppliers:
        sup_id = f"sup_{sup.id}"
        add_node(sup_id, "supplier", {"label": sup.name, "reliability_score": sup.reliability_score})

    # 3. Menu Items
    menu_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    for mi in menu_items:
        mi_id = f"menu_{mi.id}"
        add_node(mi_id, "menu_item", {"label": mi.name, "price": mi.sell_price})
        add_edge(mi_id, res_id, "belongs_to")

    # 4. Inventory
    inventory_items = db.query(InventoryItem).options(joinedload(InventoryItem.menu_item)).filter(InventoryItem.restaurant_id == restaurant_id).all()
    for inv in inventory_items:
        inv_id = f"inv_{inv.id}"
        label = f"Inv: {inv.menu_item.name}" if inv.menu_item else f"Inv {inv.id}"
        add_node(inv_id, "inventory", {"label": label, "stock_qty": inv.stock_qty})
        if inv.supplier_id:
            add_edge(f"sup_{inv.supplier_id}", inv_id, "supplies")
        if inv.menu_item_id:
            add_edge(inv_id, f"menu_{inv.menu_item_id}", "stocks")

    # 5. Customers
    customers = db.query(Customer).filter(Customer.restaurant_id == restaurant_id).all()
    for cust in customers:
        cust_id = f"cust_{cust.id}"
        add_node(cust_id, "customer", {"label": cust.name, "churn_flag": cust.churn_flag})

    # 6. Orders
    # We load recent orders to avoid massive graphs
    orders = db.query(Order).options(joinedload(Order.order_items)).filter(Order.restaurant_id == restaurant_id).order_by(Order.date.desc()).limit(50).all()
    
    revenue_node_added = False
    
    for order in orders:
        order_id = f"order_{order.id}"
        add_node(order_id, "order", {"label": f"Order {order.id}", "status": order.status})
        
        if order.customer_id:
            add_edge(order_id, f"cust_{order.customer_id}", "fulfilled_by")
            
        for oi in order.order_items:
            add_edge(f"menu_{oi.menu_item_id}", order_id, "ordered_as")
            
        # Add Revenue node logic: Order -> Revenue
        rev_id = "rev_1"
        if not revenue_node_added:
            add_node(rev_id, "revenue", {"label": "Revenue"})
            revenue_node_added = True
        add_edge(order_id, rev_id, "generates")
        
        # And Customer -> Revenue just to make the demo chain work
        if order.customer_id:
            add_edge(f"cust_{order.customer_id}", rev_id, "generates")

    react_flow_payload = {
       "status": "success",
        "restaurant_id": restaurant_id,
        "nodes": nodes,
        "edges": edges
    }

    logger.info(
        f"Graph generated successfully for restaurant {restaurant_id}. "
        f"Nodes={len(nodes)}, Edges={len(edges)}"
    )

    return react_flow_payload, G
