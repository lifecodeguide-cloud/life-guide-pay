from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Life Guide Pay Server работает"

@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.json
    print("PAYMENT RECEIVED:", data)

    # тут потом будет логика доступа в боте

    return "OK", 200

if __name__ == "__main__":
    app.run()


