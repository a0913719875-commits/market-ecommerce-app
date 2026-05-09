import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function VendorDashboardPage() {
  const [dashboard, setDashboard] = useState({ products: [], orders: [], salesTotal: 0 });
  const vendorId = "demo-vendor";

  useEffect(() => {
    api.getVendorDashboard(vendorId).then(setDashboard).catch(console.error);
  }, []);

  return (
    <section className="content-grid">
      <div className="metric">
        <span>商品數</span>
        <strong>{dashboard.products.length}</strong>
      </div>
      <div className="metric">
        <span>訂單數</span>
        <strong>{dashboard.orders.length}</strong>
      </div>
      <div className="metric">
        <span>銷售額</span>
        <strong>NT$ {dashboard.salesTotal}</strong>
      </div>
      <div className="panel wide">
        <div className="section-header">
          <h2>攤商後台</h2>
          <span>{vendorId}</span>
        </div>
        <div className="list">
          {dashboard.orders.map((order) => (
            <div className="row-item" key={order.id}>
              <div>
                <strong>訂單 {order.id}</strong>
                <span>{order.status}</span>
              </div>
              <span>NT$ {order.total}</span>
            </div>
          ))}
          {!dashboard.orders.length && <p className="empty-state">目前沒有攤商訂單</p>}
        </div>
      </div>
    </section>
  );
}
