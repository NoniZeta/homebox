#Install python 3.4 in virtual env
#https://askubuntu.com/questions/849190/python-3-4-on-ubuntu-16-04

sudo apt install -y build-essential checkinstall  
sudo apt install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev openssl  

mkdir -p $HOME/opt  
cd $HOME/opt  
curl -O https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz  
tar xzvf Python-3.4.7.tgz  
cd Python-3.4.7

./configure --enable-shared --prefix=/usr/local LDFLAGS="-Wl,--rpath=/usr/local/lib"  
sudo make altinstall  

# cree un virtual env dans le repertoire courant
python3.4 -m venv Python3.4VirtualEnv

#  active le virtual env
. Python3.4VirtualEnv/bin/activate

# desactive le virtual env
#deactivate

sudo apt-get install -y aptitude
sudo easy_install3 pip

pip3 install mysql-connector-python
pip3 install mysql-connector-python

pip3 install tornado
pip3 install pocketsphinx
pip3 install tensorflow
pip3 install gTTS
pip3 install netifaces
pip3 install pygame
pip3 install pyaudio
pip3 install websocket_client

wget https://github.com/cmusphinx/g2p-seq2seq/archive/master.zip
unzip g2p-seq2seq-master.zip
cd g2p-seq2seq-master/
sudo python3 setup.py install

#Telecharger Netifaces
#https://bitbucket.org/al45tair/netifaces/downloads/
#tar xvzf netifaces-0.10.6.tar.gz
#cd netifaces-0.10.6
#python setup.py install
