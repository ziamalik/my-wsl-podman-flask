from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World from Flask in a Podman container!'

if __name__ == '__main__':
# Listen on all network interfaces within the container
# and use port 5000 (or any port you prefer)
    app.run(host='0.0.0.0', port=5000)


