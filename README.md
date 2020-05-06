 

<pre>
installation on image, i expect this to be run as root
switch base:
create a switch user
git clone https://github.com/phar/r00tzIoTCTF
export switchuser=r00tzIoT
mv r00tzIoTCTF/switch /home/$switchuser/flaskapp
sed  "s/\/home\/pi/\/home\/$switchuser/g"  /home/$switchuser/flaskapp/daemon/switchDaemon.py   >  /home/$switchuser/flaskapp/daemon/switchDaemon_written.py
add the following line to /etc/rc.local
/usr/bin/python3 /home/[switchuser]/flaskapp/daemon/switchDaemon_written.py
sed  "s/\/home\/pi/\/home\/$switchuser/g"   r00tzIoTCTF/rpiconfig/uwsgi.ini.switch   >  /home/$switchuser/flaskapp/uwsgi.ini

switch nginx:
sudo rm /etc/nginx/sites-enabled/default
sudo cp  r00tzIoTCTF/rpiconfig/flask_proxy  /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/flaskapp_proxy /etc/nginx/sites-enabled/flaskapp_proxy
sed  "s/\/home\/pi/\/home\/$switchuser/g"  r00tzIoTCTF/rpiconfig/uwsgi.service  > /tmp/uwsgi.service
sudo cp /tmp/uwsgi.service   /etc/systemd/system/uwsgi.service

switch finish:
sudo chown www-data /home/$switchuser/flaskapp -R
tar -cjvpf factory_reset.tbz flaskapp
rm -rf r00tzIoTCTF


cloud
git clone https://github.com/phar/r00tzIoTCTF
create a cloud user

export switchuser=[clouduser]
mv r00tzIoTCTF/cloud /home/$clouduser/flaskapp
sed  "s/\/home\/pi/\/home\/$clouduser/g"  r00tzIoTCTF/rpiconfig/uwsgi.ini.switch   >  /home/$clouduser/flaskapp/uwsgi.ini
sudo rm /etc/nginx/sites-enabled/default
sudo cp  r00tzIoTCTF/rpiconfig/flask_proxy nano /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/flaskapp_proxy /etc/nginx/sites-enabled/flaskapp_proxy
sed  "s/\/home\/pi/\/home\/$clouduser/g"  r00tzIoTCTF/rpiconfig/uwsgi.service  > /tmp/uwsgi.service
sudo cp /tmp/uwsgi.service   /etc/systemd/system/uwsgi.service
sudo chown www-data /home/$clouduser/flaskapp -R
rm -rf r00tzIoTCTF


#notes:
	if you want to run them locally to test them, you will need to manually run the daemon otherwise actions taken in the cloud will never update on the switch
and update checks will never happen



----------------------------------
#TODO create r00tzLights_1.0_fw.img file on the could server

TODO: more logging
TODO test normal workflow
TODO firmware update unzip and execute
TODO configuration for cloud hostname, cloud heartbeat frequency
TODO add html template tag if the switch is running in off line mode
TODO about page on the switch should be populated with something
TODO factory restore needs testing/debugging
</pre>
