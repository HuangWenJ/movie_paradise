from app import app
from app import download
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
