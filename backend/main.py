import os
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import firestore


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    db = firestore.Client() if os.getenv("USE_FIRESTORE", "true").lower() == "true" else None

    def now_iso():
        return datetime.now(timezone.utc).isoformat()

    def collection(name):
        if db is None:
            return None
        return db.collection(name)

    def read_json():
        payload = request.get_json(silent=True)
        return payload if isinstance(payload, dict) else {}

    def require_liff_user(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get("X-LIFF-User-ID")
            if not user_id:
                return jsonify({"error": "missing_liff_user", "message": "X-LIFF-User-ID header is required"}), 401
            request.liff_user_id = user_id
            return fn(*args, **kwargs)

        return wrapper

    @app.get("/")
    def root():
        return jsonify(
            {
                "service": "market-app-backend",
                "status": "ok",
                "time": now_iso(),
            }
        )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "firestore": db is not None, "time": now_iso()})

    @app.get("/api/products")
    def list_products():
        vendor_id = request.args.get("vendorId")
        docs = []

        if db is not None:
            query = collection("products")
            if vendor_id:
                query = query.where("vendorId", "==", vendor_id)
            for doc in query.stream():
                item = doc.to_dict()
                item["id"] = doc.id
                docs.append(item)
        else:
            docs = [
                {
                    "id": "demo-tomato",
                    "name": "牛番茄",
                    "price": 80,
                    "unit": "斤",
                    "stock": 30,
                    "vendorId": "demo-vendor",
                    "imageUrl": "",
                }
            ]

        return jsonify({"items": docs})

    @app.post("/api/products")
    @require_liff_user
    def create_product():
        payload = read_json()
        required = ["name", "price", "unit", "vendorId"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            return jsonify({"error": "validation_error", "missing": missing}), 400

        product = {
            "name": payload["name"],
            "price": int(payload["price"]),
            "unit": payload["unit"],
            "stock": int(payload.get("stock", 0)),
            "vendorId": payload["vendorId"],
            "imageUrl": payload.get("imageUrl", ""),
            "description": payload.get("description", ""),
            "createdBy": request.liff_user_id,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }

        if db is None:
            product["id"] = "local-product"
            return jsonify(product), 201

        ref = collection("products").document()
        ref.set(product)
        product["id"] = ref.id
        return jsonify(product), 201

    @app.get("/api/cart")
    @require_liff_user
    def get_cart():
        user_id = request.liff_user_id
        if db is None:
            return jsonify({"userId": user_id, "items": []})

        doc = collection("carts").document(user_id).get()
        cart = doc.to_dict() if doc.exists else {"items": []}
        cart["userId"] = user_id
        return jsonify(cart)

    @app.post("/api/cart/items")
    @require_liff_user
    def add_cart_item():
        user_id = request.liff_user_id
        payload = read_json()
        required = ["productId", "quantity"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            return jsonify({"error": "validation_error", "missing": missing}), 400

        item = {
            "productId": payload["productId"],
            "quantity": int(payload["quantity"]),
            "vendorId": payload.get("vendorId"),
            "name": payload.get("name"),
            "price": int(payload.get("price", 0)),
            "updatedAt": now_iso(),
        }

        if db is None:
            return jsonify({"userId": user_id, "items": [item]}), 201

        cart_ref = collection("carts").document(user_id)
        snapshot = cart_ref.get()
        cart = snapshot.to_dict() if snapshot.exists else {"items": []}
        items = [existing for existing in cart.get("items", []) if existing.get("productId") != item["productId"]]
        items.append(item)
        cart_ref.set({"items": items, "updatedAt": now_iso()}, merge=True)
        return jsonify({"userId": user_id, "items": items}), 201

    @app.delete("/api/cart/items/<product_id>")
    @require_liff_user
    def remove_cart_item(product_id):
        user_id = request.liff_user_id
        if db is None:
            return jsonify({"userId": user_id, "items": []})

        cart_ref = collection("carts").document(user_id)
        snapshot = cart_ref.get()
        cart = snapshot.to_dict() if snapshot.exists else {"items": []}
        items = [item for item in cart.get("items", []) if item.get("productId") != product_id]
        cart_ref.set({"items": items, "updatedAt": now_iso()}, merge=True)
        return jsonify({"userId": user_id, "items": items})

    @app.get("/api/wallet")
    @require_liff_user
    def get_wallet():
        user_id = request.liff_user_id
        if db is None:
            return jsonify({"userId": user_id, "balance": 0, "transactions": []})

        wallet_doc = collection("wallets").document(user_id).get()
        wallet = wallet_doc.to_dict() if wallet_doc.exists else {"balance": 0}
        tx_docs = (
            collection("wallets")
            .document(user_id)
            .collection("transactions")
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
            .limit(30)
            .stream()
        )
        transactions = [{**doc.to_dict(), "id": doc.id} for doc in tx_docs]
        return jsonify({"userId": user_id, "balance": wallet.get("balance", 0), "transactions": transactions})

    @app.post("/api/wallet/top-up")
    @require_liff_user
    def top_up_wallet():
        user_id = request.liff_user_id
        payload = read_json()
        amount = int(payload.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "validation_error", "message": "amount must be greater than zero"}), 400

        if db is None:
            return jsonify({"userId": user_id, "balance": amount}), 201

        wallet_ref = collection("wallets").document(user_id)
        tx_ref = wallet_ref.collection("transactions").document()
        transaction = {"type": "top_up", "amount": amount, "createdAt": now_iso()}
        wallet_ref.set({"balance": firestore.Increment(amount), "updatedAt": now_iso()}, merge=True)
        tx_ref.set(transaction)
        wallet = wallet_ref.get().to_dict()
        return jsonify({"userId": user_id, "balance": wallet.get("balance", 0), "transaction": transaction}), 201

    @app.get("/api/vendors/<vendor_id>/dashboard")
    @require_liff_user
    def vendor_dashboard(vendor_id):
        if db is None:
            return jsonify({"vendorId": vendor_id, "products": [], "orders": [], "salesTotal": 0})

        products = [{**doc.to_dict(), "id": doc.id} for doc in collection("products").where("vendorId", "==", vendor_id).stream()]
        orders = [{**doc.to_dict(), "id": doc.id} for doc in collection("orders").where("vendorId", "==", vendor_id).stream()]
        sales_total = sum(int(order.get("total", 0)) for order in orders if order.get("status") != "cancelled")
        return jsonify({"vendorId": vendor_id, "products": products, "orders": orders, "salesTotal": sales_total})

    @app.post("/api/orders")
    @require_liff_user
    def create_order():
        user_id = request.liff_user_id
        payload = read_json()
        items = payload.get("items", [])
        if not isinstance(items, list) or not items:
            return jsonify({"error": "validation_error", "message": "items are required"}), 400

        total = sum(int(item.get("price", 0)) * int(item.get("quantity", 0)) for item in items)
        order = {
            "userId": user_id,
            "vendorId": payload.get("vendorId"),
            "items": items,
            "total": total,
            "status": "created",
            "deliveryMethod": payload.get("deliveryMethod", "pickup"),
            "note": payload.get("note", ""),
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }

        if db is None:
            order["id"] = "local-order"
            return jsonify(order), 201

        ref = collection("orders").document()
        ref.set(order)
        order["id"] = ref.id
        return jsonify(order), 201

    @app.get("/api/orders")
    @require_liff_user
    def list_orders():
        user_id = request.liff_user_id
        vendor_id = request.args.get("vendorId")

        if db is None:
            return jsonify({"items": []})

        query = collection("orders")
        if vendor_id:
            query = query.where("vendorId", "==", vendor_id)
        else:
            query = query.where("userId", "==", user_id)
        items = [{**doc.to_dict(), "id": doc.id} for doc in query.stream()]
        return jsonify({"items": items})

    @app.patch("/api/orders/<order_id>/status")
    @require_liff_user
    def update_order_status(order_id):
        payload = read_json()
        status = payload.get("status")
        allowed = {"created", "accepted", "preparing", "ready", "completed", "cancelled"}
        if status not in allowed:
            return jsonify({"error": "validation_error", "allowed": sorted(allowed)}), 400

        if db is None:
            return jsonify({"id": order_id, "status": status})

        ref = collection("orders").document(order_id)
        ref.set({"status": status, "updatedAt": now_iso()}, merge=True)
        order = ref.get().to_dict()
        order["id"] = order_id
        return jsonify(order)

    @app.post("/api/line/notify")
    @require_liff_user
    def send_line_notification():
        payload = read_json()
        message = payload.get("message", "")
        if not message:
            return jsonify({"error": "validation_error", "message": "message is required"}), 400

        # TODO: Integrate LINE Messaging API push message with channel access token.
        return jsonify(
            {
                "status": "queued",
                "to": payload.get("to", request.liff_user_id),
                "message": message,
                "createdAt": now_iso(),
            }
        ), 202

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
