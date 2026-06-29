/**
 * NEZ-13 route metadata -- see RNEZ-13-route-map.md for the architecture notes.
 * This module just describes each hash-based route, its nav label, and the DOM section that backs the existing cards.
 */
export const routeMap = [
  {
    path: "/login",
    hash: "/login",
    label: "Login",
    sectionId: "route-login-card",
    requiresAuth: false,
    roles: [],
    enterHooks: [],
    summary: "Landing card that hosts the login form and default MVP credentials."
  },
  {
    path: "/dashboard",
    hash: "/dashboard",
    label: "Dashboard",
    sectionId: "route-dashboard",
    requiresAuth: true,
    roles: ["admin", "factory_manager", "production_supervisor", "store_manager", "warehouse_staff", "accountant", "executive"],
    enterHooks: ["refreshDashboard", "loadInventory"],
    summary: "KPI grid, activity log, and the refresh buttons for metrics/inventory."
  },
  {
    path: "/receiving",
    hash: "/receiving",
    label: "Receiving",
    sectionId: "route-receiving",
    requiresAuth: true,
    roles: ["admin", "factory_manager", "warehouse_staff"],
    enterHooks: [],
    summary: "Receiving card with supplier/product wiring and the createReceiving() action."
  },
  {
    path: "/production",
    hash: "/production",
    label: "Production",
    sectionId: "route-production",
    requiresAuth: true,
    roles: ["admin", "factory_manager", "production_supervisor"],
    enterHooks: [],
    summary: "Production card that calls completeProduction() once the batch data is filled."
  },
  {
    path: "/transfers",
    hash: "/transfers",
    label: "Transfers",
    sectionId: "route-transfers",
    requiresAuth: true,
    roles: ["admin", "factory_manager", "warehouse_staff"],
    enterHooks: [],
    summary: "Dispatch + receive forms that operate through dispatchTransfer() and receiveTransfer()."
  },
  {
    path: "/store",
    hash: "/store",
    label: "Store movement",
    sectionId: "route-store",
    requiresAuth: true,
    roles: ["admin", "factory_manager", "store_manager"],
    enterHooks: [],
    summary: "Store movement card covering sale / return / waste workflows."
  }
];
