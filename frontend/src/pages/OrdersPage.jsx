import { useEffect, useState } from "react";
import { api } from "../api/client.js";

const statuses = ["created", "accepted", "preparing", "ready", "completed", "cancelled"];

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    api.listOrders().then((data) => setOrders(data.items || [])).catch(console.error);
  }, []);

  async function changeStatus(orderId, status) {
    const updated = await api.updateOrderStatus(orderId, status);
    setOrders((current) => current.map((order) => (order.id === orderId ? updated : order)));
  }

  return (
    <section className="panel">
      <div className="section-header">
        <h2>訂單系統</h2>
        <span>{orders.length} 筆訂單</span>
      </div>
      <div className="list">
        {orders.map((order) => (
          <div className="row-item order-row" key={order.id}>
            <div>
              <strong>訂單 {order.id}</strong>
              <span>NT$ {order.total} · {order.deliveryMethod}</span>
            </div>
            <select value={order.status} onChange={(event) => changeStatus(order.id, event.target.value)}>
              {statuses.map((status) => (
                <option value={status} key={status}>{status}</option>
              ))}
            </select>
          </div>
        ))}
        {!orders.length && <p className="empty-state">尚無訂單</p>}
      </div>
    </section>
  );
}
