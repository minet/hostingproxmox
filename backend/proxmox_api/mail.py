from flask_cors import CORS
from flask_mail import Message, Mail
from flask import Flask, render_template
from datetime import date,timedelta
#from proxmox_api.__main__ import *


# Les identifiants pour le serveur smtp

app = Flask(__name__, static_folder=".", static_url_path="", template_folder=".")
app.config["MAIL_SERVER"] = "192.168.102.18"
app.config["MAIL_PORT"] = 25

email = Mail(app)  # creation d'une instance de flask-mail

def sendMail(recipient, htmlbody):
    print("send mail to", recipient)
    msg = Message(
        "[Hosting] Your VMs are about to be deteled",
        sender="hosting-noreply@minet.net",
        recipients=[recipient]
    )
    msg.html = htmlbody.encode("utf-8")
    msg.body = msg.html
    email.send(msg)  #


def mailHTMLGenerator(nb_notif, expiration_date, freeze_status):
    if nb_notif == 1:
        nb_notif_msg = "1st"
    elif nb_notif == 2:
        nb_notif_msg = "2nd"
    else:    
        nb_notif_msg = str(nb_notif) + "th"
    
    nbDaysBeforeNextStep = timedelta(days=(5 - nb_notif)*7)
    nextStepDay = date.today() + nbDaysBeforeNextStep
    secondNextSetDay = nextStepDay + timedelta(days=28)
    thirdNextSetDay = secondNextSetDay + timedelta(days=28)
    nextStep = ""
    if freeze_status ==1 :
        nextStep += "<br><strong> &#128680; WARNING :  Your VMs will be automatically stopped on " + str(nextStepDay) + "</strong>. You will still have a restricted daily access via hosting.minet.net."
    if freeze_status <= 2 : 
        nextStep += "<br><strong> &#128680; WARNING :  The access to your VMs will be blocked on " + str(secondNextSetDay) + "</strong>. You will not be able to access your VMs anymore.<br><strong> &#128680; WARNING :  Your VMs will be DEFINITIVELY detroyed on " + str(thirdNextSetDay) + "</strong>. Your data will be lost forever."
    if freeze_status == 3 : 
        nextStep += "<br><strong> &#128680; THIS IS LE LAST WARNING :  Your VMs will be DEFINITIVELY detroyed on " + str(thirdNextSetDay) + "</strong>. Your data will be lost forever."
    header="""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<style>
body{
    font-family: Times, Helvetica, sans-serif;
    font-size: 14px;
    font-color:black;
}
</style>"""
    msg = f"""
<body>
    Hi there,<br> 
    Your are using <a href="https://hosting.minet.net">hosting.minet.net</a> but your <strong>MiNET cotisation expired on {str(expiration_date)} </strong>.<br>

    Your account is frozen. <strong style='color:red;'>Please renew your membership or backup your data and delete your VMs now</strong>.<br><br>

    This is the {str(nb_notif_msg)} warning. <br>
    {str(nextStep)}<br>

    If you think this is a mistake, please contact us as soon as possible on <a href="https://tickets.minet.net">tickets.minet.net</a>. <br>

    Best regards,<br>
    <table style="font-size: medium; font-family: Arial; background:white; width:vw;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td><table style="font-size: medium; font-family: Arial;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td style="vertical-align: middle;" width="150"><span style="margin-right: 20px; display: block;" class="sc-kgAjT cuzzPp"><img src="https://www.minet.net/res/img/minet.png" role="presentation" style="max-width: 130px;" class="sc-cHGsZl bHiaRe" width="130"></span></td><td style="vertical-align: middle;"><font color="#000000" size="4"><span style="caret-color: rgb(0, 0, 0);"><b>The MiNET team</b></span></font><p color="#000000" font-size="medium" style="margin: 0px; color: rgb(0, 0, 0); font-size: 14px; line-height: 22px;" class="sc-fMiknA bxZCMx"><span></span></p><p color="#000000" font-size="medium" style="margin: 0px; font-weight: 500; color: rgb(0, 0, 0); font-size: 14px; line-height: 22px;" class="sc-dVhcbM fghLuF"><span></span></p></td><td width="30"><div style="width: 30px;"></div></td><td color="#6fa3e8" direction="vertical" style="width: 1px; border-bottom: medium none; border-left: 1px solid rgb(111, 163, 232);" class="sc-jhAzac hmXDXQ" width="1"></td><td width="30"><div style="width: 30px;"></div></td><td style="vertical-align: middle;"><table style="font-size: medium; font-family: Arial;" class="sc-gPEVay eQYmiW" cellspacing="0" cellpadding="0"><tbody><tr><td style="padding: 0px;"><a href="https://tikctes.minet.net" color="#000000" style="text-decoration: none; color: rgb(0, 0, 0); font-size: 12px;" class="sc-gipzik iyhjGb"><span style="margin-left:1px; font-family: Arial;">&#128735; tickets.minet.net</span></a></td></tr><tr><td style="padding: 0px;"><a href="//www.minet.net" color="#000000" style="text-decoration: none; color: rgb(0, 0, 0); font-size: 12px;" class="sc-gipzik iyhjGb"><span style="margin-left:1px; font-family: Arial;">&#127760;  www.minet.net</span></a></td></tr><tr style="vertical-align: middle;" height="25"><td style="padding: 0px;"><span color="#000000" style="font-size: 12px; color: rgb(0, 0, 0);" class="sc-csuQGl CQhxV"><span style="margin-left:1px; font-family: Arial;"> &#128235;  9 rue Charles Fourier, 91000, Evry</span></span></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td></td></tr><tr><td></td></tr></tbody></table></body></html>
    """
    return header+msg



