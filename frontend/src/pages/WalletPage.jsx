import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function WalletPage() {
  const [wallet, setWallet] = useState({ balance: 0, transactions: [] });
  const [amount, setAmount] = useState(500);

  useEffect(() => {
    api.getWallet().then(setWallet).catch(console.error);
  }, []);

  async function topUp(event) {
    event.preventDefault();
    const nextWallet = await api.topUpWallet(Number(amount));
    setWallet((current) => ({ ...current, balance: nextWallet.balance }));
  }

  return (
    <section className="content-grid">
      <div className="panel wallet-summary">
        <span>錢包餘額</span>
        <strong>NT$ {wallet.balance}</strong>
      </div>
      <form className="panel form-panel" onSubmit={topUp}>
        <h2>儲值</h2>
        <label>
          金額
          <input type="number" min="1" value={amount} onChange={(event) => setAmount(event.target.value)} />
        </label>
        <button type="submit">儲值錢包</button>
      </form>
      <div className="panel wide">
        <div className="section-header">
          <h2>交易紀錄</h2>
          <span>{wallet.transactions.length} 筆</span>
        </div>
        <div className="list">
          {wallet.transactions.map((tx) => (
            <div className="row-item" key={tx.id}>
              <strong>{tx.type}</strong>
              <span>NT$ {tx.amount}</span>
            </div>
          ))}
          {!wallet.transactions.length && <p className="empty-state">尚無交易紀錄</p>}
        </div>
      </div>
    </section>
  );
}
