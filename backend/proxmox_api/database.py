from proxmox_api.db.db_models import User, db


def get_user_id(user_id):
    return User.query.filter_by(id=user_id).first()


def add_user(user, vmid):
    new_user = User(user, vmid + " ")
    db.session.add(new_user)
    db.session.commit()


def update_vm_list(user, add_vmid):
    user = get_user_id(user_id=user)
    user.vm = user.vm + str(add_vmid) + " "
    db.session.commit()
