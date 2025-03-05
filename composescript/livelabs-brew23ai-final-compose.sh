#!/bin/bash

sudo firewall-cmd --permanent --add-port=1521/tcp #Database
sudo firewall-cmd --permanent --add-port=1522/tcp #Database
sudo firewall-cmd --permanent --add-port=8888/tcp #JupyterLabs
sudo firewall-cmd --permanent --add-port=8181/tcp #ORDS
sudo firewall-cmd --permanent --add-port=5000/tcp #Flask
sudo firewall-cmd --permanent --add-port=5500/tcp #EM
sudo firewall-cmd --permanent --add-port=5501/tcp #EM
sudo firewall-cmd --permanent --add-port=7000/tcp #Django
sudo firewall-cmd --permanent --add-port=27017/tcp #Mongo
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" destination address="10.0.0.0/24" service name="ssh" accept'
sudo firewall-cmd --reload

sudo dnf update -y && sudo dnf -y install container-tools oracle-database-preinstall-23ai jdk sqlcl

# Clean empty UI folders
sudo -u oracle sh -c '
set -eo pipefail
cd /home/oracle
[ -d Videos ]    && rmdir Videos
[ -d Templates ] && rmdir Templates
[ -d Pictures ]  && rmdir Pictures
[ -d Music ]     && rmdir Music
[ -d Downloads ] && rmdir Downloads
[ -d Documents ] && rmdir Documents
[ -d Public ]    && rmdir Public
exit 0
'


#folder


sudo -u oracle mkdir -p /home/oracle/.opt/

sudo -u oracle mkdir -p /home/oracle/.opt/oradata

sudo -u oracle mkdir -p /home/oracle/.opt/scripts/startup

sudo -u oracle mkdir -p /home/oracle/.opt/scripts/setup

sudo -u oracle mkdir -p /home/oracle/.opt/ords_secrets

sudo -u oracle mkdir -p /home/oracle/.opt/ords_config

sudo -u oracle mkdir -p /home/oracle/.config/systemd/oracle

sudo -u oracle mkdir -p /home/oracle/.opt/models/onnx

sudo -u oracle chmod 777 /home/oracle/.opt/models/onnx

sudo -u oracle chmod 777 /home/oracle/.opt/oradata

sudo -u oracle chmod 777 /home/oracle/.opt/ords_secrets

sudo -u oracle chmod 777 /home/oracle/.opt/ords_config

#store inital password for password reset process
vncpwdinit='Welcome23ai'
echo $vncpwdinit | sudo -u oracle tee /home/oracle/.vncpwdinit > /dev/null
sudo -u oracle bash -c 'echo vncpwdinit=$(cat /home/oracle/.vncpwdinit) > /home/oracle/.vncpwdinit.env'
