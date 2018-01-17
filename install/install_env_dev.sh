sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install -y python-software-properties
sudo apt-get install -y software-properties-common

sudo add-apt-repository ppa:webupd8team/y-ppa-manager
sudo add-apt-repository ppa:gstreamer-developers/ppa
sudo apt-get update -y

sudo apt-get install -y python-pip python-dev
sudo apt-get install -y python2.7-dev
sudo apt-get install -y build-essential checkinstall
sudo apt-get install -y ubuntu-restricted-extras
sudo apt-get install -y systemd

sudo apt-get install -y python-pyaudio
sudo apt-get install -y autoconf
sudo apt-get install -y libtool
sudo apt-get install -y automake-dev
sudo apt-get install -y g++
sudo apt-get install -y bison	
sudo apt-get install -y swig
sudo apt-get install -y python2.7-dev
sudo apt-get install -y python-netifaces
sudo apt-get install -y python-numpy
sudo apt-get install -y python-pygame
sudo apt-get install -y avahi-daemon
sudo apt-get install -y nano
sudo apt-get install -y pulseaudio
sudo apt-get install -y libpulse-dev
sudo apt-get install -y ffmpeg libmp3lame0 libavcodec-extra-53
#sudo apt-get install -y lubuntu-software-center
sudo apt-get install -y flashplugin-installer
sudo apt-get install -y nodejs npm
sudo pip install --egg mysql-connector-python-rf
sudo pip install requests
sudo apt-get install -y python-mysqldb
sudo apt install -y net-tools
sudo alsa force-reload

curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo apt-get install -y software-properties-gtk
sudo apt-get install -y ppa-purge
sudo apt-get install -y y-ppa-manager

sudo apt-get install -y gstreamer1.0*
sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt-get install -y dconf-tools
sudo apt-get install -y python-gst-1.0
sudo apt-get install -y python-gi python3-gi \
    gstreamer1.0-tools \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-libav


sudo apt-get install -y git-core gitk
sudo apt-get install -y openssh-server


sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.0.0-cp27-none-linux_x86_64.whl
#sudo pip install tensorflow
git clone https://github.com/cmusphinx/g2p-seq2seq.git
cd g2p-seq2seq/
sudo python setup.py install
cd ..

sudo rm -R g2p-seq2seq

tar xvzf tornado-4.3.tar.gz
cd tornado-4.3
python setup.py build
sudo python setup.py install

cd ..
sudo rm -R tornado-4.3

tar zxvf sphinxbase-5prealpha.tar.gz
mv sphinxbase-5prealpha sphinxbase

tar zxvf pocketsphinx-5prealpha.tar.gz

tar zxvf sphinxtrain-5prealpha.tar.gz

cd sphinxbase
sudo chmod 755 configure
sudo chmod 755 autogen
./autogen.sh
./configure
make
sudo make install

cd ..
cd pocketsphinx-5prealpha
sudo chmod 755 configure
sudo chmod 755 autogen
./configure
make
sudo make install

cd ..

cd sphinxtrain-5prealpha
sudo chmod 755 configure
sudo chmod 755 autogen
./configure
make
sudo make install

cd ..

export GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0
export LD_LIBRARY_PATH=/usr/local/lib
export LD_LIBRARY_PATH=/usr/local/lib/python2.7/dist-packages/pocketsphinx
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
sudo ldconfig

sudo rm -R sphinxbase
sudo rm -R pocketsphinx-5prealpha
sudo rm -R sphinxtrain-5prealpha

sudo python ez_setup.py --insecure

tar zxvf websocket_client-0.35.0.tar.gz
cd websocket_client-0.35.0
sudo python setup.py install
cd ..
sudo rm -R websocket_client-0.35.0

sudo apt-get update -y
sudo apt-get upgrade -y

sudo npm install -g bower http-server jasmine-core karma karma-chrome-launcher karma-firefox-launcher karma-jasmine protractor
sudo npm install -g estraverse gulp gulp-autoprefixer gulp-angular-templatecache del lodash gulp-cssnano gulp-filter gulp-flatten
sudo npm install -g gulp-eslint eslint-plugin-angular gulp-load-plugins gulp-size gulp-uglify gulp-useref gulp-util gulp-ng-annotate
sudo npm install -g gulp-replace gulp-rename gulp-rev gulp-rev-replace gulp-htmlmin gulp-inject gulp-protractor gulp-sourcemaps
sudo npm install -g gulp-sass gulp-angular-filesort main-bower-files wiredep karma karma-jasmine karma-phantomjs-launcher phantomjs
sudo npm install -g karma-angular-filesort karma-phantomjs-shim karma-coverage karma-ng-html2js-preprocessor browser-sync 
sudo npm install -g browser-sync-spa http-proxy-middleware chalk uglify-save-license lite-server yo concurrently typescript typings

npm rebuild node-sass

cd ~/Documents/Jarvis/workspace/topi_box/resources/fr/
sudo rm -R model_g2p_fr
g2p-seq2seq --train frenchWords62K.dic --model model_g2p_fr


