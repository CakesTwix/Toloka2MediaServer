from toloka2MediaServerWeb.app import app
import os

if __name__ == '__main__':
    # Set the default port to 5000 if not specified
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)