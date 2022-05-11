#8 /bin/bash

echo [*] List users ...
ls /home/ > /tmp/users.txt
touch /tmp/rules.txt
echo \# Created by cloud-init v. 20.2 on $(date) >> /tmp/rules.txt
echo "" >> /tmp/rules.txt
while read user; do 
	echo '# Rules for user' $user >> /tmp/rules.txt
	echo $user 'ALL=(ALL) ALL' >>  /tmp/rules.txt
done < /tmp/users.txt

echo [*] Updating cloud init ...
echo [*] Entering in sudo mode. Your password may be asked.
sudo rm /etc/sudoers.d/90-cloud-init-users

echo [*] Writing the new file ...
touch /etc/sudoers.d/90-cloud-init-users
sudo cat /tmp/rules.txt >  /etc/sudoers.d/90-cloud-init-users

echo [*] Updating file permissions ...
chmod 440 /etc/sudoers.d/90-cloud-init-users
rm /tmp/rules.txt
rm /tmp/users.txt

if grep -q NOPASSWD /etc/sudoers.d/90-cloud-init-users; then
	echo [*] An error occured. Please contact webmaster@minet.net 
else 
	echo [*] Patch applied with success
fi
echo [*] END
