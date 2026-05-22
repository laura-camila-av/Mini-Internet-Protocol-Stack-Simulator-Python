# main.py
# Entry point for the Mini Internet Protocol Stack Simulator.
# Simulates data transfer from Host A to Host B across all three layers:

import sys
from devices import Host, Router
from config import (
    HOST_A_IP, HOST_A_MAC, HOST_A_ARP_TABLE, HOST_A_ROUTING_TABLE,
    HOST_B_IP, HOST_B_MAC, HOST_B_ARP_TABLE, HOST_B_ROUTING_TABLE,
    ROUTER_ARP_TABLE, ROUTER_INTERFACES, ROUTER_ROUTING_TABLE,
    SRC_PORT, DST_PORT
)

def main():

    # parse command line argument to get data size in bytes
    if len(sys.argv) != 2:
        # ensure correct input format
        print("Usage: python main.py <data_size>")
        sys.exit(1)

    data_size = int(sys.argv[1])

    # Instantiate devices
    host_a = Host(
        name          = "Host A",
        ip_addr       = HOST_A_IP,
        mac_addr      = HOST_A_MAC,
        arp_table     = HOST_A_ARP_TABLE,
        routing_table = HOST_A_ROUTING_TABLE,
        src_port      = SRC_PORT,
        dst_port      = DST_PORT
    )

    host_b = Host(
        name          = "Host B",
        ip_addr       = HOST_B_IP,
        mac_addr      = HOST_B_MAC,
        arp_table     = HOST_B_ARP_TABLE,
        routing_table = HOST_B_ROUTING_TABLE,
        src_port      = DST_PORT,
        dst_port      = SRC_PORT
    )

    router = Router(
        name          = "Router R1",
        arp_table     = ROUTER_ARP_TABLE,
        interfaces    = ROUTER_INTERFACES,
        routing_table = ROUTER_ROUTING_TABLE
    )

    # Create network so each device knows where to send data
    host_a.next_device  = router    
    router.next_device  = host_b     
    host_b.next_device  = router     
    router.prev_device  = host_a    

    # layer 3 attributes

    host_a.dst_ip = HOST_B_IP
    host_b.dst_ip = HOST_A_IP

    host_a.gateway_interface = "Interface 1"
    host_b.gateway_interface = "Interface 2"

    router.connected_devices = {
        "Interface 1": host_a,
        "Interface 2": host_b
    }
    # pass application layer data to host a for handling - triggers workflow
    host_a.receive_data(data_size)


if __name__ == "__main__":
    main()