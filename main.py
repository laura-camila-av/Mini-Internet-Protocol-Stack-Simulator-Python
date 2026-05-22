from devices import Host, Router
from protocol import Layer2
from config import *
import sys



def main():

    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC, HOST_A_ARP_TABLE)
    host_b = Host("Host B", HOST_B_IP, HOST_B_MAC, HOST_B_ARP_TABLE)
    router = Router("Router R1", ROUTER_ARP_TABLE, ROUTER_INTERFACES)

    # Read message size from command line argument as per spec
    data_size = int(sys.argv[1])
    mock_data = b"X" * data_size

    print("=" * 60)
    print("LAYER 2 SIMULATION: Host A → Router R1 → Host B")
    print("=" * 60)

    # Step 1: Host A sends frame to Router R1
    print("\n--- Host A sending frame to Router R1 ---\n")
    frame_to_router = host_a.frame_send(mock_data, R1_I1_IP)

    # Step 2: Router R1 receives frame on Interface 1
    print("\n--- Router R1 receiving frame on Interface 1 ---\n")
    packet_from_host_a = router.receive_frame(frame_to_router, "Interface 1")

    # Step 3: Router R1 forwards frame to Host B on Interface 2
    print("\n--- Router R1 forwarding frame to Host B ---\n")
    frame_to_host_b = router.frame_send(packet_from_host_a, HOST_B_IP, "Interface 2")

    # Step 4: Host B receives frame, then Layer 3 delivers packet to Layer 4
    print("\n--- Host B receiving frame ---\n")
    packet_at_host_b = host_b.receive_frame(frame_to_host_b)

    print("\n--- Host B: Layer 3 delivering packet to Layer 4 ---\n")
    host_b.layer3.deliver_packet(packet_at_host_b, HOST_B_IP, host_b.layer4)

    print("\n" + "=" * 60)
    print("LAYER 2 SIMULATION COMPLETE")
    print("=" * 60)

    if __name__ == "__main__":
        main()