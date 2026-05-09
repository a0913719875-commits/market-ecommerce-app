const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function getUserId() {
  return localStorage.getItem("marketAppUserId") || "local-line-user";
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    "X-LIFF-User-ID": getUserId(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || data.error || "API request failed");
  }
  return data;
}

export const api = {
  health: () => request("/api/health", { headers: {} }),
  listProducts: () => request("/api/products"),
  createProduct: (payload) => request("/api/products", { method: "POST", body: JSON.stringify(payload) }),
  getCart: () => request("/api/cart"),
  addCartItem: (payload) => request("/api/cart/items", { method: "POST", body: JSON.stringify(payload) }),
  removeCartItem: (productId) => request(`/api/cart/items/${productId}`, { method: "DELETE" }),
  getWallet: () => request("/api/wallet"),
  topUpWallet: (amount) => request("/api/wallet/top-up", { method: "POST", body: JSON.stringify({ amount }) }),
  getVendorDashboard: (vendorId) => request(`/api/vendors/${vendorId}/dashboard`),
  listOrders: () => request("/api/orders"),
  createOrder: (payload) => request("/api/orders", { method: "POST", body: JSON.stringify(payload) }),
  updateOrderStatus: (orderId, status) =>
    request(`/api/orders/${orderId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  sendLineNotification: (payload) => request("/api/line/notify", { method: "POST", body: JSON.stringify(payload) }),
};
