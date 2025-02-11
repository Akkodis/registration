#!/usr/bin/env python3

import connexion

from swagger_server import encoder

from waitress import serve

from swagger_server.controllers.registration_api_controller import delete_old_dataflows
import threading

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'Registration 5G Meta API'}, pythonic_params=True)
    
def main():
    threading.Thread(target=delete_old_dataflows).start()

    # Development
    app.run(port=8080)
    
    # Production
    # serve(app, host="0.0.0.0", port=8080)

if __name__ == '__main__':
    main()
