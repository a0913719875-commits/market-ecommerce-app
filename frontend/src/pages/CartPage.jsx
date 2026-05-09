import { useEffect, useMemo, useState } from "react";
import { Trash2 } from "lucide-react";
import { api } from "../api/client.js";

export default function CartPage() {
  const [cart, setCart] = useState({ items: [] });
  const total = useMemo(
    () => cart.items.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0),
    [cart]
  );

  useEffect(() => {
    api.getCart().then(setCart).catch(console.error);
  }, []);

  async function removeItem(productId) {
    const nextCart = await api.removeCartItem(productId);
    setCart(nextCart);
  }

  async function checkout() {
    if (!cart.items.length) return;
    await api.createOrder({ vendorId: cart.items[0].vendorId, items: cart.items, deliveryMethod: "pickup" });
  }

  return (
    <section className="panel">
      <div className="section-header">
        <h2>購物車</h2>
        <strong>NT$ {total}</strong>
      </div>
      <div className="list">
        {cart.items.map((item) => (
          <div className="row-item" key={item.productId}>
            <div>
              <strong>{item.name || item.productId}</strong>
              <span>數量 {item.quantity}</span>
            </div>
            <div className="row-actions">
              <span>NT$ {Number(item.price || 0) * Number(item.quantity || 0)}</span>
              <button type="button" onClick={() => removeItem(item.productId)} aria-label="移除商品">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
        {!cart.items.length && <p className="empty-state">購物車目前沒有商品</p>}
      </div>
      <button type="button" onClick={checkout} disabled={!cart.items.length}>建立訂單</button>
    </section>
  );
}
