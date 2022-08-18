#!/usr/bin/env python3
import connexion
from flask_cors import CORS
from flask_apscheduler import APScheduler

import proxmox_api.config.configuration as config
from proxmox_api import encoder
app = connexion.App(__name__, specification_dir='./swagger/')

app.app.json_encoder = encoder.JSONEncoder

app.app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI

CORS(app.app)

scheduler = APScheduler()

app.add_api('swagger.yaml', arguments={'title': 'Proxmox'}, pythonic_params=True)

JOBS = [
        { # update all vm ips 
            "id": "update_vm_ips",
            "func": "proxmox_api.proxmox:update_vm_ips_job",
            "args": (app.app,),
            "trigger": "interval",
            "seconds": 120,
        }, 
        { # Check all cotisation to uodate endCotisationDate and send email if needed
            "id" : "check_cotisation",
            "func" : "proxmox_api.proxmox:check_cotisation_job",
            "trigger" : "interval",
            "args": (app.app,),
            "seconds": 800,
        }
    ]

app.app.config['JOBS'] = JOBS
app.app.config['SCHEDULER_API_ENABLE'] = False


from proxmox_api.db.db_models import db



## init db

db.init_app(app.app)
with app.app.app_context():
    #db.drop_all()
    db.create_all()

scheduler.init_app(app.app)
scheduler.start()

if __name__ == '__main__':
    app.run(port=8080, debug=True)

