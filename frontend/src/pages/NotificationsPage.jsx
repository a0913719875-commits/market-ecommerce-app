import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "../api/client.js";

export default function NotificationsPage() {
  const [message, setMessage] = useState("您的訂單已準備完成，請至攤位取貨。");
  const [status, setStatus] = useState("");

  async function sendNotification(event) {
    event.preventDefault();
    const result = await api.sendLineNotification({ message });
    setStatus(result.status);
  }

  return (
    <section className="panel form-panel">
      <div className="section-header">
        <h2>LINE 通知</h2>
        <Send size={18} />
      </div>
      <form onSubmit={sendNotification}>
        <label>
          訊息內容
          <textarea rows="5" value={message} onChange={(event) => setMessage(event.target.value)} />
        </label>
        <button type="submit">送出通知</button>
      </form>
      {status && <p className="notice">通知狀態：{status}</p>}
    </section>
  );
}
