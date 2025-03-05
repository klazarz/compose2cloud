#!/bin/bash


#######
#######    S T A R T      S C R I P T    ######
#######   (this is for Oracle Linux 9)   ######

sudo dnf update -y

sudo iptables -F
sudo iptables-save
sudo systemctl stop firewalld
sudo systemctl disable firewalld

#expand boot volume (https://docs.oracle.com/en-us/iaas/oracle-linux/oci-utils/index.htm#oci-growfs)
sudo /usr/libexec/oci-growfs -y

#podman and utensils - https://docs.oracle.com/en/operating-systems/oracle-linux/podman/podman-InstallingPodmanandRelatedUtilities.html
sudo dnf install -y container-tools sqlcl jdk21 wget git podman-compose 
# sudo dnf install -y oracle-epel-release-el9
# sudo dnf config-manager --enable ol9_developer_EPEL




#git clone the compose sources to be added
git clone https://github.com/klazarz/compose2cloud.git

mkdir -p compose2cloud/composescript/oradata

chmod 777 compose2cloud/composescript/oradata/
chmod 777 compose2cloud/composescript/ords_secrets/
chmod 777 compose2cloud/composescript/ords_config/
chmod 777 compose2cloud/composescript/app/
chmod 777 compose2cloud/composescript/model/

podman-compose -f compose2cloud/composescript/compose.yml up 



