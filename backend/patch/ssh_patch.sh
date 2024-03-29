#! /bin/bash


echo [*] Downloading new sshd config ...
wget https://raw.githubusercontent.com/minet/hostingproxmox/master/backend/patch/sshd_config
echo [*] Installing sshd_config
mv -f sshd_config /etc/ssh/
echo [*] Restarting sshd server ...
service sshd restart
echo [*] Patch successfully installed
echo [*] END

exit 0
