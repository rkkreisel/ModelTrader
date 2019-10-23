timedatectl set-timezone America/New_York
sudo /usr/bin/Xvfb :0 -ac -screen 0 2048x1536x24 &
sudo /usr/bin/x11vnc -ncache 10 -ncache_cr -viewpasswd remote_view_only_pass -passwd sbox7879  -display :0 -forever -shared -logappend /var/log/x11vnc.log -bg -noipv6
cd /opt/IBController/
DISPLAY=:0 ./IBControllerGatewayStart.sh
while ! netstat -tna | grep 'LISTEN\>' | grep -q ':55555\>'; do
    sleep 10
done
cd /home/ubuntu/ModelTrader
DISPLAY=:0 python3 main.py
cd ~/Jts/972
DISPLAY=:0 ./tws