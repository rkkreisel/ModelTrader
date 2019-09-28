timedatectl set-timezone America/New_York
sudo /usr/bin/Xvfb :0 -ac -screen 0 2048x1536x24 &
sudo /usr/bin/x11vnc -ncache 10 -ncache_cr -viewpasswd remote_view_only_pass -passwd sbox7879  -display :0 -forever -shared -logappend /var/log/x11vnc.log -bg -noipv6
cd /opt/IBController
DISPLAY=:0 ./IBControllerGatewayStart.sh
cd /home/ubuntu/ModelTrader
DISPLAY=:0 python3 main.py
#cd ~/Jts/ibgateway/972
#cd /home/ubuntu/Jts/ibgateway/972
#DISPLAY=:0 ./ibgateway &
#cd /home/ubuntu/ModelTrader
#DISPLAY=:0 python3 main.py
