gw=$(ip r l | grep default | cut -d\  -f3)
sed -i "/dhcp-option=3,*/c\dhcp-option=3,$gw" /etc/dnsmasq.conf
