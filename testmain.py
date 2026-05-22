# main.py

import sys
from protocol import Layer2, Layer4
from devices import Host, Router
from config import (
    HOST_A_IP, HOST_A_MAC, HOST_A_ARP_TABLE,
    HOST_B_IP, HOST_B_MAC, HOST_B_ARP_TABLE,
    ROUTER_ARP_TABLE, ROUTER_INTERFACES,
    R1_I1_IP, R1_I2_IP,
    SRC_PORT, DST_PORT
)

# ─────────────────────────────────────────────
# MOCK LAYER 3 BYPASS (for testing Layer 4 only)
# This simulates the full journey of a segment from
# Host A to Host B and back without Layer 3 logic.
# Will be replaced once Layer 3 is implemented.
# ─────────────────────────────────────────────

def mock_layer3_send(sender, receiver, segment):
    """
    Bypasses Layer 3 entirely — directly delivers the segment
    from sender to receiver and returns the ACK.

    Args:
        sender   (Host)  : the sending host
        receiver (Host)  : the receiving host
        segment  (Layer4): the segment to deliver

    Returns:
        Layer4: the ACK segment returned by the receiver
    """
    # simulate segment arriving at Host B's Layer 4
    ack = receiver.receive_segment(segment)
    return ack

def main():

    # parse command line argument for data size
    if len(sys.argv) != 2:
        print("Usage: python main.py <data_size>")
        sys.exit(1)

    data_size = int(sys.argv[1])

    # ─────────────────────────────────────────────
    # Instantiate devices
    # ─────────────────────────────────────────────
    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC, HOST_A_ARP_TABLE, SRC_PORT, DST_PORT)
    host_b = Host("Host B", HOST_B_IP, HOST_B_MAC, HOST_B_ARP_TABLE, DST_PORT, SRC_PORT)
    router = Router("Router R1", ROUTER_ARP_TABLE, ROUTER_INTERFACES)

    # ─────────────────────────────────────────────
    # LAYER 4 TEST
    # ─────────────────────────────────────────────
    # generate dummy payload
    data = b'A' * data_size

    print(f"\nHost A: Layer 4: Data received from Application Layer. Data size={data_size}")

    # split data into chunks if needed
    if data_size > Layer4.MAX_DATA_SIZE:
        chunks = [
            data[i:i + Layer4.MAX_DATA_SIZE]
            for i in range(0, data_size, Layer4.MAX_DATA_SIZE)
        ]
    else:
        chunks = [data]

    # send each chunk sequentially using rdt2.2
    seq_num = 0
    for chunk in chunks:

        # build segment
        segment = Layer4.encapsulate(SRC_PORT, DST_PORT, Layer4.DATA, seq_num, chunk)
        print(f"Host A: Layer 4: Checksum computed")
        print(f"Host A: Layer 4: Segment created by adding transport layer header (DATA, seq={seq_num}) (encapsulation)")
        print(f"Host A: Layer 4: Segment sent to Network Layer")

        # rdt2.2 loop - bypass layer 3 for now
        while True:
            ack = mock_layer3_send(host_a, host_b, segment)

            if ack is not None and ack.seg_type == Layer4.ACK and ack.seq_num == seq_num:
                print(f"Host A: Layer 4: ACK received: seq={ack.seq_num}")
                break
            else:
                print(f"Host A: Layer 4: Incorrect ACK received - retransmitting segment seq={seq_num}")

        # alternate sequence number
        seq_num = 1 - seq_num

    # ─────────────────────────────────────────────
    # LAYER 2 TEST
    # ─────────────────────────────────────────────

    mock_packet = "MOCK_LAYER3_PACKET"

    frame_to_router = host_a.frame_send(mock_packet, R1_I1_IP)
    print("\n")

    packet_from_host_a = router.receive_frame(frame_to_router, "Interface 1")
    print("\n")

    frame_to_host_b = router.frame_send(packet_from_host_a, HOST_B_IP, "Interface 2")
    print("\n")

    packet_at_host_b = host_b.receive_frame(frame_to_host_b)
    print("\n")

if __name__ == "__main__":
    main()