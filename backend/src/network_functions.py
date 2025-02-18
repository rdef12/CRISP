import socket
import os

# Stuck right now on how to get the actual WSL IP (seen in /etc/resolv.conf)
# I also need this to generalise to other operating systems, so maybe entry via the GUI is best
# Add as a volume so only needed once.

def get_host_IP_address():
    """
    I need this to be the port of the host device, not the Docker container.
    """
    
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(("0.0.0.0", 80))  # 0.0.0.0 so socket binds to all interfaces on the machine - second arg is an arbitrary port
    # local_ip_address = s.getsockname()[0]
    # s.close()
    # print(local_ip_address)
    
    # print(socket.gethostbyname(socket.gethostname()))
    
    # host_ip = os.getenv("HOST_IP")
    # print(host_ip)
    # resolved_ip = socket.gethostbyname(host_ip)
    # print(resolved_ip)
    
    # Tried ubuntu eth0 and veth0
    # os.environ["LOCAL_IP_ADDRESS"] = "172.17.0.1" # docker0 IPv4
    # os.environ["LOCAL_IP_ADDRESS"] = "10.204.200.75" # eth0 IPv4
    os.environ["LOCAL_IP_ADDRESS"] = "192.168.10.2" # eth1 IPv4
    # os.environ["LOCAL_IP_ADDRESS"] = "172.24.80.1" #veth0 IPv4 for WSL - found by ipconfig in CMD 
    # os.environ["LOCAL_IP_ADDRESS"] = "192.168.10.2" #eth0 for windows host device
    return 0

