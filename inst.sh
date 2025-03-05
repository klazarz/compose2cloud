#!/bin/bash


#######
#######    S T A R T      S C R I P T    ######
#######   (this is for Oracle Linux 9)   ######

sudo dnf update -y

sudo iptables -F
sudo iptables-save

#expand boot volume (https://docs.oracle.com/en-us/iaas/oracle-linux/oci-utils/index.htm#oci-growfs)
sudo /usr/libexec/oci-growfs -y

#podman and utensils - https://docs.oracle.com/en/operating-systems/oracle-linux/podman/podman-InstallingPodmanandRelatedUtilities.html
sudo dnf install -y container-tools sqlcl jdk21 wget git

#git clone the compose sources to be added




