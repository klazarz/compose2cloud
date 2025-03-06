#!/bin/bash

source init/variable.sh

#######    S T A R T      S C R I P T    ######
#######   (this is for Oracle Linux 9)   ######

sudo dnf update -y

sudo firewall-cmd --permanent --add-port=1521/tcp #Database
sudo firewall-cmd --permanent --add-port=1522/tcp #Database
sudo firewall-cmd --permanent --add-port=8888/tcp #JupyterLabs
sudo firewall-cmd --permanent --add-port=8181/tcp #ORDS
sudo firewall-cmd --permanent --add-port=8501/tcp #Streamlit
sudo firewall-cmd --permanent --add-port=5000/tcp #Flask
sudo firewall-cmd --permanent --add-port=5500/tcp #EM
sudo firewall-cmd --permanent --add-port=5501/tcp #EM
sudo firewall-cmd --permanent --add-port=7000/tcp #Django
sudo firewall-cmd --permanent --add-port=27017/tcp #Mongo
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" destination address="10.0.0.0/24" service name="ssh" accept'
sudo firewall-cmd --reload

#expand boot volume (https://docs.oracle.com/en-us/iaas/oracle-linux/oci-utils/index.htm#oci-growfs)
sudo /usr/libexec/oci-growfs -y

#podman and utensils - https://docs.oracle.com/en/operating-systems/oracle-linux/podman/podman-InstallingPodmanandRelatedUtilities.html
sudo dnf install -y container-tools sqlcl jdk21 wget git podman-compose

#git clone the compose sources to be added
git clone https://github.com/klazarz/compose2cloud.git

mkdir -p compose2cloud/composescript/oradata

chmod 777 compose2cloud/composescript/oradata/
chmod 777 compose2cloud/composescript/ords_secrets/
chmod 777 compose2cloud/composescript/ords_config/
chmod 777 compose2cloud/composescript/app/
chmod 777 compose2cloud/composescript/model/

sudo cp compose2cloud/composescript/scripts/podman-compose.service /etc/systemd/system/.

sudo systemctl daemon-reload
sudo systemctl enable podman-compose.service