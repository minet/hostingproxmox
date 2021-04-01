from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(254), primary_key=True)
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


