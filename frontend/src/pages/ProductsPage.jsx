import { useEffect, useState } from "react";
import { Plus, ShoppingCart } from "lucide-react";
import { api } from "../api/client.js";

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ name: "", price: "", unit: "斤", stock: "", vendorId: "demo-vendor" });

  useEffect(() => {
    api.listProducts().then((data) => setProducts(data.items || [])).catch(console.error);
  }, []);

  async function addProduct(event) {
    event.preventDefault();
    const product = await api.createProduct(form);
    setProducts((current) => [product, ...current]);
    setForm({ name: "", price: "", unit: "斤", stock: "", vendorId: "demo-vendor" });
  }

  async function addToCart(product) {
    await api.addCartItem({
      productId: product.id,
      quantity: 1,
      vendorId: product.vendorId,
      name: product.name,
      price: product.price,
    });
  }

  return (
    <section className="content-grid">
      <div className="panel wide">
        <div className="section-header">
          <h2>商品頁</h2>
          <span>{products.length} 項商品</span>
        </div>
        <div className="product-grid">
          {products.map((product) => (
            <article className="product-card" key={product.id}>
              <div className="product-image">{product.imageUrl ? <img src={product.imageUrl} alt="" /> : <span>菜</span>}</div>
              <div>
                <h3>{product.name}</h3>
                <p>{product.description || "新鮮現貨，依攤商庫存為準"}</p>
              </div>
              <div className="card-footer">
                <strong>NT$ {product.price} / {product.unit}</strong>
                <button type="button" onClick={() => addToCart(product)} aria-label={`加入 ${product.name}`}>
                  <ShoppingCart size={16} />
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>

      <form className="panel form-panel" onSubmit={addProduct}>
        <div className="section-header">
          <h2>新增商品</h2>
          <Plus size={18} />
        </div>
        <label>
          商品名稱
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        </label>
        <label>
          價格
          <input type="number" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required />
        </label>
        <label>
          單位
          <input value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} required />
        </label>
        <label>
          庫存
          <input type="number" value={form.stock} onChange={(event) => setForm({ ...form, stock: event.target.value })} />
        </label>
        <button type="submit">建立商品</button>
      </form>
    </section>
  );
}
