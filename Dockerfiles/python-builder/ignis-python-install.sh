#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
apt update
apt -y --no-install-recommends install python3.8 python3.8-distutils python3-numpy
apt -y install libprotobuf-dev libprotobuf-c-dev protobuf-c-compiler protobuf-compiler python3-protobuf

apt -y install wget libbsd-dev pkg-config libgnutls28-dev libnftables-dev asciidoc git build-essential libnet-dev libnl-3-dev libcap-dev
wget https://download.openvz.org/criu/criu-3.15.tar.bz2
tar -xjf criu-3.15.tar.bz2
cd criu-3.15
make install
cd ..
apt -y install iptables
apt -y install lsof


rm -rf /var/lib/apt/lists/*

python3 ${IGNIS_HOME}/bin/get-pip.py
rm -f ${IGNIS_HOME}/bin/get-pip.py
python3 -m pip install certifi

cd ${IGNIS_HOME}/core/python-libs/
cd mpi4py
python3 setup.py install
cd ..
cd thrift
python3 setup.py install
rm -fR ${IGNIS_HOME}/core/python-libs/

cd ${IGNIS_HOME}/core/python/
python3 setup.py develop

PYTHON_LIB=$(python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))")
ln -s $PYTHON_LIB/site-packages $PYTHON_LIB/dist-packages

mkdir -p /run/criu
chmod 755 /run/criu
criu service --address /run/criu/criu_service.socket &
mkdir /tmp/checkpointing
