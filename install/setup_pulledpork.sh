#!/bin/bash

# install build dependencies
sudo apt-get install -y libcrypt-ssleay-perl liblwp-useragent-determined-perl


# install pulledpork
# modify the link to get the latest version
git clone https://github.com/shirkdog/pulledpork.git
cd pulledpork
sudo cp pulledpork.pl /usr/local/bin
sudo chmod +x /usr/local/bin/pulledpork.pl
sudo cp etc/*.conf /etc/snort

# initialize pulledpork
sudo mkdir /etc/snort/rules/iplists
sudo touch /etc/snort/rules/iplists/default.blacklist

# test pulledpork installation
/usr/local/bin/pulledpork.pl -V


