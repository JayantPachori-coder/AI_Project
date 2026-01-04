from pyngrok import ngrok, conf
from waitress import serve
from app import app
import time

# ------------------ CONFIGURATION ------------------
# Replace this with your valid Ngrok auth token
conf.get_default().auth_token = "345giaDluXu1SvTCOfZA6iYAKXe_82S25KHFNYg9uBGj1hn2V"

# ------------------ CLEANUP OLD TUNNELS ------------------
try:
    tunnels = ngrok.get_tunnels()
    if tunnels:
        for t in tunnels:
            print(f"🛑 Closing old tunnel: {t.public_url}")
            try:
                ngrok.disconnect(t.public_url)
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Failed to disconnect {t.public_url}: {e}")
    else:
        print("✅ No existing tunnels found.")
except Exception as e:
    print(f"⚠️ Could not retrieve tunnels: {e}")

# ------------------ START NEW NGROK TUNNEL ------------------
public_url = None
try:
    public_url = ngrok.connect(8000, bind_tls=True)
    print("\n✅ Ngrok tunnel created successfully!")
    print("🔒 Secure HTTPS connection established.")
    print("🌍 Your app is now accessible at:")
    print("   ├── Local:  http://127.0.0.1:8000")
    print(f"   └── Public: {public_url.public_url}")
    print("\n📡 Waiting for connections...\n")
except Exception as e:
    print(f"❌ Failed to create ngrok tunnel: {e}")
    print("⚠️ You can still access the app locally at http://127.0.0.1:8000")

# ------------------ RUN FLASK APP VIA WAITRESS ------------------
if __name__ == "__main__":
    print("🚀 Launching Flask app securely via Waitress...")
    print("⚙️  Server running on port 8000...\n")
    serve(app, host="0.0.0.0", port=8000)
