
# install java
# https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-get-on-ubuntu-16-04



sudo rm /var/lib/dpkg/lock

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install python-software-properties
sudo apt-get install software-properties-common

wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo add-apt-repository ppa:deluge-team/ppa
sudo add-apt-repository ppa:team-xbmc/ppa
sudo add-apt-repository ppa:webupd8team/java

sudo apt-get update 

sudo apt-get install -y google-chrome-stable

sudo sh -c 'echo "deb http://archive.getdeb.net/ubuntu xenial-getdeb apps" >> /etc/apt/sources.list.d/getdeb.list'
wget -q -O - http://archive.getdeb.net/getdeb-archive.key | sudo apt-key add -
sudo apt install -y filezilla

sudo apt-get install -y  deluge
sudo apt-get install -y deluged deluge-web deluge-console

sudo apt-get install -y kodi
sudo apt-get install -y git
sudo apt-get install -y openssh-server

sudo apt-get install -y oracle-java9-installer
