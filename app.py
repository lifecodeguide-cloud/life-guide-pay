from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.paypal.com"   # LIVE

PRICE = "5.99"


# ===== ГЛАВНАЯ СТРАНИЦА =====
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Оплата доступа</title>
        <script src="https://www.paypal.com/sdk/js?client-id={{ client_id }}&currency=USD"></script>
    </head>
    <body style="font-family: Arial; text-align: center; padding: 40px;">
        <h1>Life Guide ✨</h1>
        <p style="font-size: 22px;">Чтобы получить полный разбор, оплатите доступ за <b>5.99 $</b></p>
        <br><br>
        <div id="paypal-button-container" style="max-width:300px; margin:auto;"></div>

        <script>
            paypal.Buttons({
                createOrder: function(data, actions) {
                    return fetch('/create-order', {
                        method: 'post'
                    }).then(res => res.json()).then(data => data.id);
                },

                onApprove: function(data, actions) {
                    return fetch('/capture-order', {
                        method: 'post',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            orderID: data.orderID
                        })
                    }).then(res => res.json()).then(data => {
                        window.location.href = "/success";
                    });
                }
            }).render('#paypal-button-container');
        </script>
    </body>
    </html>
    """, client_id=PAYPAL_CLIENT_ID)


# ===== ПОЛУЧИТЬ ACCESS TOKEN =====
def get_paypal_access_token():
    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    return response.json()["access_token"]


# ===== СОЗДАТЬ ЗАКАЗ =====
@app.route("/create-order", methods=["POST"])
def create_order():
    access_token = get_paypal_access_token()

    response = requests.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": PRICE
                    }
                }
            ]
        }
    )

    return response.json()


# ===== ПОДТВЕРДИТЬ ОПЛАТУ =====
@app.route("/capture-order", methods=["POST"])
def capture_order():
    order_id = request.json.get("orderID")
    access_token = get_paypal_access_token()

    response = requests.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )

    data = response.json()
    print("PAYMENT CAPTURED:", data)

    return data


# ===== СТРАНИЦА УСПЕХА =====
@app.route("/success")
def success():
    return """
    <h1 style='font-family:Arial; text-align:center; margin-top:80px;'>
        Оплата прошла успешно ✅<br><br>
        Спасибо! Теперь можно выдать доступ в боте.
    </h1>
    """


# ===== PAYPAL WEBHOOK =====
@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.json
    print("PAYPAL WEBHOOK RECEIVED:", data)
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

