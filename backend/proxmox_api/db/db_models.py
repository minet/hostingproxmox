from flask_sqlalchemy import SQLAlchemy
#from flask_sqlalchemy import event
from proxmox_api.config.configuration import ENV
#from sqlalchemy import event

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(254), primary_key=True)
    freezeState = db.Column(db.String(10), nullable=True, default=None)
    lastNotificationDate = db.Column(db.String(254), nullable=True, default=None)
    vms = db.relationship('Vm', backref="owner", lazy=True)
    dnsEntries = db.relationship('DomainName', backref="owner", lazy=True)

class DomainName(db.Model):
    __tablename__ = 'domaineName'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(254), db.ForeignKey("user.id"), nullable=True)
    entry = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(15), nullable=True)

class Vm(db.Model):
    __tablename__ = 'vm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    userId = db.Column(db.String(254), db.ForeignKey("user.id"), nullable=True)
    type = db.Column(db.String(254), nullable=False)
    ip = db.Column(db.String(15), nullable=True)
    mac = db.Column(db.String(20), nullable=True, unique=True)
    created_on = db.Column(db.Date, nullable=False, default=db.func.date(db.func.now()))
    needToBeRestored = db.Column(db.Boolean, nullable=False, default=False)
    unsecure = db.Column(db.Boolean, nullable=False, default=False)

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(254), db.ForeignKey("user.id"), nullable=True)
    vmId = db.Column(db.Integer, nullable=True)
    ip = db.Column(db.String(15), nullable=True)
    date = db.Column(db.TIMESTAMP,default=db.func.current_timestamp(),  nullable=False)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    criticity = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    message = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=False)


if ENV != "TEST":
### Trigger for ip tracking
    TRIGGER_CREATION =  """
            CREATE TRIGGER history_insert_vm AFTER UPDATE ON vm
            FOR EACH ROW BEGIN
                IF OLD.ip != NEW.ip THEN
                    INSERT INTO history (userId, vmId, ip, date) VALUES (NEW.userId, NEW.id, NEW.ip, NOW());
                END IF;
            END;
            """
else :
    TRIGGER_CREATION = ""

#event.listen(
#    Vm.__table__,
#    "after_create",
#    db.DDL(
#       TRIGGER_CREATION
#    )
#)
#
