#you pronbably dont want to run this in the app dir
wget http://r00tzIoTCloud.local/r00tzLights.fwupdate --output-document=/tmp/r00tzLights.fwupdate
tar -C flaskapp/ -cjvpf /home/r00tzIoT/configs_package.tbz configs
rm -rf /home/r00tzIoT/flaskapp
tar -xjvpf /tmp/r00tzLights.fwupdate --overwrite
tar -C flaskapp/ -xjvpf /home/r00tzIoT/configs_package.tbz
sudo -u www-data /bin/bash flaskapp/update.sh

