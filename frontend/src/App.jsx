import { NavLink, Route, Routes } from "react-router-dom";
import { Bell, LayoutDashboard, PackageSearch, ReceiptText, ShoppingCart, WalletCards } from "lucide-react";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import ProductsPage from "./pages/ProductsPage.jsx";
import CartPage from "./pages/CartPage.jsx";
import WalletPage from "./pages/WalletPage.jsx";
import VendorDashboardPage from "./pages/VendorDashboardPage.jsx";
import OrdersPage from "./pages/OrdersPage.jsx";
import NotificationsPage from "./pages/NotificationsPage.jsx";

const navItems = [
  { to: "/", label: "商品", icon: PackageSearch },
  { to: "/cart", label: "購物車", icon: ShoppingCart },
  { to: "/wallet", label: "錢包", icon: WalletCards },
  { to: "/vendor", label: "後台", icon: LayoutDashboard },
  { to: "/orders", label: "訂單", icon: ReceiptText },
  { to: "/notifications", label: "通知", icon: Bell },
];

function Shell() {
  const { profile, login, logout, isReady } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">市</span>
          <div>
            <strong>菜市場電商</strong>
            <small>Market Commerce</small>
          </div>
        </div>

        <nav className="nav-list" aria-label="主要功能">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} end={item.to === "/"} className="nav-link">
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <h1>今日市場</h1>
            <p>商品、訂單、錢包與攤商營運管理</p>
          </div>
          <div className="user-panel">
            {profile ? (
              <>
                <span>{profile.displayName || "LINE 使用者"}</span>
                <button type="button" onClick={logout}>登出</button>
              </>
            ) : (
              <button type="button" onClick={login} disabled={!isReady}>LINE 登入</button>
            )}
          </div>
        </header>

        <Routes>
          <Route path="/" element={<ProductsPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/wallet" element={<WalletPage />} />
          <Route path="/vendor" element={<VendorDashboardPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
