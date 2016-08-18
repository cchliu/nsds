#!/bin/bash

# install build dependencies
sudo apt-get install -y build-essential
sudo apt-get install -y libpcap-dev libpcre3-dev libdumbnet-dev
sudo apt-get install -y bison flex
sudo apt-get install -y zlib1g-dev

# build and install DAQ from source
# modify the link to get the latest version
wget https://snort.org/downloads/snort/daq-2.0.6.tar.gz
tar zxvf daq-2.0.6.tar.gz
cd daq-2.0.6
./configure
make
sudo make install
cd ..

# build and install Snort from source
# modify the link to get the latest versiocn
wget https://snort.org/downloads/snort/snort-2.9.8.3.tar.gz
tar zxvf snort-2.9.8.3.tar.gz
cd snort-2.9.8.3
./configure --enable-sourcefire --enable-reload
make
sudo make install
sudo ldconfig
sudo ln -s /usr/local/bin/snort /usr/sbin/snort

# test if Snort is build and installed properly
snort -V

