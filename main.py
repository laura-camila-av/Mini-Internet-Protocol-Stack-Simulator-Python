# Mini Internet Protocol Stack Simulator -> main.py

import sys
from devices import Host, Router
from config import (
    HOST_A_IP, HOST_A_MAC, HOST_A_ARP_TABLE, HOST_A_ROUTING_TABLE,
    HOST_B_IP, HOST_B_MAC, HOST_B_ARP_TABLE, HOST_B_ROUTING_TABLE,
    ROUTER_ARP_TABLE, ROUTER_INTERFACES, ROUTER_ROUTING_TABLE,
    SRC_PORT, DST_PORT
)

def main():

    # parse command line argument to get data size in bytes and source and destination
    if len(sys.argv) != 4:
        # ensure correct input format
        print("Usage: python main.py <data_size> <source> <destination>")
        sys.exit(1)

    data_size = int(sys.argv[1])
    input_src = sys.argv[2]
    input_dst = sys.argv[3]

    # instantiate devices
    host_a = Host(
        name = "Host A",
        ip_addr = HOST_A_IP,
        mac_addr = HOST_A_MAC,
        arp_table = HOST_A_ARP_TABLE,
        routing_table = HOST_A_ROUTING_TABLE,
        src_port = SRC_PORT,
        dst_port = DST_PORT
    )

    host_b = Host(
        name = "Host B",
        ip_addr = HOST_B_IP,
        mac_addr = HOST_B_MAC,
        arp_table = HOST_B_ARP_TABLE,
        routing_table = HOST_B_ROUTING_TABLE,
        src_port = DST_PORT,
        dst_port = SRC_PORT
    )

    router = Router(
        name = "Router R1",
        arp_table = ROUTER_ARP_TABLE,
        interfaces = ROUTER_INTERFACES,
        routing_table = ROUTER_ROUTING_TABLE
    )

    # map input source and destination to device names
    input_mapping = {
        "hostA" : host_a,
        "hostB" : host_b
    }

    # validate inputs 
    if input_src not in input_mapping:
        print(f"Unrecognised device: {input_src}. Please choose 'HostA' or 'HostB'. ")
        sys.exit(1)

    if input_dst not in input_mapping:
        print(f"Unrecognised device: {input_dst}. Please choose 'HostA' or 'HostB'. ")
        sys.exit(1)

    if input_src == input_dst:
        print(f"Source and destination cannot be the same device.")
        sys.exit(1)

    # map inputs to recognised devices
    source = input_mapping[input_src]
    destination = input_mapping[input_dst]

    # create network topology based on input devices
    if source == host_a and destination == host_b:
        host_a.next_device = router
        router.next_device = host_b
        host_b.next_device = router
        router.prev_device = host_a

    elif source == host_b and destination == host_a:
        host_b.next_device = router
        router.next_device = host_a
        host_a.next_device = router
        router.prev_device = host_b

    # start simulation
    print("\n" + "-" * 55)
    print(f"Starting Simulation: Sending {data_size} bytes: {source.name} -> {destination.name}")
    print("-" * 55 + "\n")

    # pass application layer data to source for handling - triggers workflow
    source.receive_data(data_size)


if __name__ == "__main__":
    main()