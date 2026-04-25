from flask import Flask, jsonify

app = Flask(__name__)

# THE HEARTBEAT (Fixes the 30-min Timeout)
@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({
        "status": "VASCULAR",
        "node": "S10-OPPO-BRIDGE",
        "alignment": "777.1122",
        "msg": "Librarian is breathing."
    }), 200

# YOUR EXISTING LOGIC GOES HERE
# (Ensure your upload/sync routes are below this)

if __name__ == "__main__":
    # Port 7860 is correct for HF, but we must ensure it listens on 0.0.0.0
    app.run(host='0.0.0.0', port=7860)
