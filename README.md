


installation on image

switch:
create a switch user

export $switchuser=<switchuser>

git clone https://github.com/phar/r00tzIoTCTF
mv r00tzIoTCTF/switch /home/

add the following line to /etc/rc.local
/usr/bin/python3 /home/<switchuser>/switch/daemon/switchDaemon.py

cp   r00tzIoTCTF/switch/rpiconfig/uswgi.ini.switch  /home/$switchuser/switch/uwsgi.ini
sudo rm /etc/nginx/sites-enabled/default
sudo cp  r00tzIoTCTF/rpiconfig/flask_proxy nano /etc/nginx/sites-enabled/flask_proxy
sudo ln -s /etc/nginx/sites-available/flask_proxy /etc/nginx/sites-enabled
sed  's/\/home\/pi/$switchuser/g'   r00tzIoTCTF/switch/rpiconfig/uwsgi.service  >> /etc/systemd/system/uwsgi.service
sudo chown www-data /home/$switchuser/switch -R



cloud
create a cloud user
export $clouduser=<clouduser>
git clone https://github.com/phar/r00tzIoTCTF
mv r00tzIoTCTF/cloud /home/

cp   r00tzIoTCTF/switch/rpiconfig/uswgi.ini.cloud  /home/$clouduser/switch/uwsgi.ini
sudo rm /etc/nginx/sites-enabled/default
sudo cp  r00tzIoTCTF/rpiconfig/flask_proxy nano /etc/nginx/sites-enabled/flask_proxy
sudo ln -s /etc/nginx/sites-available/flask_proxy /etc/nginx/sites-enabled
sed  's/\/home\/pi/$clouduser/g'   r00tzIoTCTF/switch/rpiconfig/uwsgi.service  >> /etc/systemd/system/uwsgi.service
sudo chown www-data /home/$clouduser/cloud -R







----------------------------------
#TODO create r00tzLights_1.0_fw.img file on the could server

TODO: more logging
TODO debug

TODO firmware update unzip and execute
TODO fix logo transparency
TODO cleanup api behavior in server out scenarios
