from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.paypal.com"  # LIVE
PRICE = "4.99"


def get_paypal_access_token():
    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    return response.json()["access_token"]


# ===== ГЛАВНАЯ СТРАНИЦА =====
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Оплата доступа</title>
    <script src="https://www.paypal.com/sdk/js?client-id={{ client_id }}&currency=USD"></script>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f7f7f7;
            margin: 0;
            padding: 20px 14px;
            display: flex;
            justify-content: center;
        }

        .box {
            width: 100%;
            max-width: 560px;
            background: white;
            border-radius: 22px;
            padding: 30px 22px;
            margin-top: 18px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            text-align: center;
        }

        h1 {
            font-size: 32px;
            margin-bottom: 16px;
        }

        .text {
            font-size: 18px;
            line-height: 1.35;
            font-weight: 400;
            margin-bottom: 18px;
        }

        .price {
            font-weight: 300;
            font-size: 24px;
        }

        #paypal-button-container {
            margin-top: 26px;
            max-width: 460px;
            margin-left: auto;
            margin-right: auto;
        }

        @media (max-width: 600px) {
            .box {
                padding: 20px 16px;
                border-radius: 16px;
                margin-top: 10px;
            }

            h1 {
                font-size: 26px;
                margin-bottom: 12px;
            }

            .text {
                font-size: 17px;
                line-height: 1.35;
                margin-bottom: 16px;
            }

            .price {
                font-size: 28px;
            }

            #paypal-button-container {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>

    <div class="box">
        <h1>Life Guide ✨</h1>

        <div class="text">
            Чтобы получить полный разбор,<br>
            оплатите доступ за <span class="price">4.99 $</span>
        </div>

        <div id="paypal-button-container"></div>
    </div>

    <script>
        paypal.Buttons({
            style: {
                layout: 'vertical',
                color: 'gold',
                shape: 'rect',
                label: 'paypal',
                height: 55
            },

            createOrder: function(data, actions) {
                return fetch('/create-order', {
                    method: 'post'
                })
                .then(res => res.json())
                .then(data => data.id);
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
                })
                .then(res => res.json())
                .then(data => {
                    window.location.href = "/success";
                });
            }
        }).render('#paypal-button-container');
    </script>

</body>
</html>
""", client_id=PAYPAL_CLIENT_ID)


# ===== СОЗДАНИЕ ЗАКАЗА =====
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


# ===== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ =====
@app.route("/capture-order", methods=["POST"])
def capture_order():
    data = request.get_json()
    order_id = data.get("orderID")
    access_token = get_paypal_access_token()

    response = requests.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )

    return response.json()


# ===== УСПЕШНАЯ ОПЛАТА =====
@app.route("/success")
def success():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Оплата прошла успешно</title>
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:80px;">
        <h1>Оплата прошла успешно 🎉</h1>
        <p>Возвращаем вас в Telegram...</p>
    <script>
        window.location.href = "https://t.me/LifeGuideVitaBot?start=paid";
    </script>
        
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
