#!/usr/bin/env python3
import connexion
from flask_cors import CORS

import proxmox_api.config.configuration as config
from proxmox_api import encoder

app = connexion.App(__name__, specification_dir='./swagger/')

app.app.json_encoder = encoder.JSONEncoder
app.app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
CORS(app.app)
app.add_api('swagger.yaml', arguments={'title': 'Proxmox'}, pythonic_params=True)

from proxmox_api.db.db_models import db


## init db

db.init_app(app.app)
with app.app.app_context():
    #db.drop_all()
    db.create_all()



if __name__ == '__main__':
    app.run(port=8080, debug=True)
