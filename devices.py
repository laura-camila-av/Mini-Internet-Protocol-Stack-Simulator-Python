import protocol
import ipaddress

class Host:
    def __init__(self, name, ip_addr, mac_addr, routing_table, arp_table, src_port, dst_port):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
        self.arp_table = arp_table
        self.routing_table = routing_table
        self.src_port = src_port
        self.dst_port = dst_port

    # -------------LAYER 2 HANDLING-------------
    def frame_send(self, packet, next_hop_ip):

        src_mac = self.mac_addr
        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}")

        # encapsulate frame and send
        frame = protocol.Layer2.encapsulate(src_mac, dst_mac, packet)

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")

        return frame
    
    def receive_frame(self, frame):

        # check destination mac matches own mac
        if frame.dst_mac != self.mac_addr:
            return None

        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")

        # decapsulate frame into packet and deliver to network layer
        packet = frame.decapsulate()

        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        return packet
    
      # -------------LAYER 3 HANDLING-------------
    def deliver_packet(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.source_IP}, DST_IP={packet.dst_IP}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_IP}")

        if packet.dst_IP == self.ip_addr:
            print(f"{self.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
            return self.receive_segment(packet.payload)
        else:
            print(f"{self.name}: Layer 3: Packet not for this host — discarding.")
            return None

    #Wraps segment in IP packet, performs routing table lookup to find next-hop IP and interface, then forwards to Layer 2.
    def send_packet(self, segment, dst_ip):
        """L3 encapsulation + routing + L2 framing. Returns the frame."""
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={self.ip_addr}, DST_IP={dst_ip}, TTL=100")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        for subnet, (next_hop_ip, interface) in self.routing_table.items():
            if ipaddress.IPv4Address(dst_ip) in ipaddress.IPv4Network(subnet):
                print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
                print(f"{self.name}: Layer 3: Outgoing interface selected")
                print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
                packet = protocol.Layer3.encapsulate_to_IP_packet(segment, self.ip_addr, dst_ip)
                return self.frame_send(packet, next_hop_ip)

        raise ValueError(f"No route found for destination IP: {dst_ip}")
    
    def handle_incoming(self, frame):
        """Receiver side: process incoming DATA frame, return ACK frame"""
        packet = self.receive_frame(frame)
        ack_segment = self.deliver_packet(packet)
        # send ACK back through L3 → L2
        ack_frame = self.send_packet(ack_segment, packet.source_IP)
        return ack_frame
    
    # -------------LAYER 4 HANDLING-------------

    def receive_data(self, data_size):
        data = b'A' * data_size
        # receiving data from application layer
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={data_size}")

        # split data into chunks if it exceeds MAX_DATA_SIZE (500)
        if data_size > protocol.Layer4.MAX_DATA_SIZE:
            chunks = [
                # segment message into 500 byte chunks
                data[i:i + protocol.Layer4.MAX_DATA_SIZE]
                for i in range(0, data_size, protocol.Layer4.MAX_DATA_SIZE)
            ]
        else:
            chunks = [data]

        # send each chunk sequentially using rdt2.2
        seq_num = 0
        for chunk in chunks:
            self.send_segment(chunk, seq_num)
            # alternate sequence number after each successful send
            seq_num = 1 - seq_num
        return

    def send_segment(self, data, seq_num):
        segment = protocol.Layer4.encapsulate(self.src_port, self.dst_port, protocol.Layer4.DATA, seq_num, data)

        print(f"{self.name}: Layer 4: Checksum computed")
        print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={seq_num}) (encapsulation)")
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        while True:
            # send through network, get ACK back
            frame = self.send_packet(segment, self.dst_ip)
            ack_frame = self.next_device.relay(frame, self.gateway_interface)
            ack_packet = self.receive_frame(ack_frame)
            ack_segment = self.deliver_packet(ack_packet)

            if ack_segment.seg_type == protocol.Layer4.ACK and ack_segment.seq_num == seq_num:
                print(f"{self.name}: Layer 4: ACK received: seq={ack_segment.seq_num}")
                break
            else:
                print(f"{self.name}: Layer 4: Incorrect ACK received. Retransmitting segment seq={seq_num}")
    
    def receive_segment(self, segment):

        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        # verify checksum
        if segment.verify_checksum():
            print(f"{self.name}: Layer 4: Checksum verified")

        # if DATA
        if segment.seg_type == protocol.Layer4.DATA:
            # decapsulate segment and deliver to application layer
            data = segment.decapsulate()
            print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(data)}")

            # return ack to sender
            ack = protocol.Layer4.encapsulate(segment.src_port, segment.dst_port, protocol.Layer4.ACK, segment.seq_num)
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num}) (encapsulation)")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            return ack
        
        # if ACK
        if segment.seg_type == protocol.Layer4.ACK:

            return segment

        
        return segment

class Router:
    def __init__(self, name, arp_table, interfaces, routing_table):
        self.name = name
        self.arp_table = arp_table
        self.interfaces = interfaces
        self.mac_table = {}
        self.routing_table = routing_table

    # LAYER 2 HANDLING
    def frame_send(self, packet, next_hop_ip, interface):

        src_mac = self.interfaces[interface][1]
        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}")

        # encapsulate frame and send
        frame = protocol.Layer2.encapsulate(src_mac, dst_mac, packet)

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {interface}")

        return frame
    

    # LAYER 3 HANDLING
    def receive_frame(self, frame, interface):

        # check dst_mac against current destination
        interface_mac = self.interfaces[interface][1]
        if frame.dst_mac != interface_mac:
            # forward frame if mac address doesn't match
            return None
        
        print(f"{self.name}: Layer 2: Frame received on {interface}")
        
        # else is at destination
        self.mac_table[frame.src_mac] = interface
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {interface}")

        # decapsulate frame into packet and deliver to network layer
        packet = frame.decapsulate()

        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        return packet
    
    def decrement_TTL(self, packet):
        """
        Decrements TTL by 1 at each router hop.
        Returns False if TTL reaches 0 (packet should be dropped), True otherwise.
        """
        old_ttl = packet.ttl
        packet.ttl -= 1
        if packet.ttl <= 0:
            print(f"{self.name}: Layer 3: TTL expired. Packet dropped.")
            return False
        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} → {packet.ttl}")
        return True

    def forward_packet(self, packet):
        """Returns (frame, out_interface) tuple"""
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.source_IP}, DST_IP={packet.dst_IP}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_IP}")

        if not self.decrement_TTL(packet):
            return None, None

        print(f"{self.name}: Layer 3: Routing table lookup performed")

        for subnet, (next_hop_ip, out_interface) in self.routing_table.items():
            if ipaddress.IPv4Address(packet.dst_IP) in ipaddress.IPv4Network(subnet):
                print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
                print(f"{self.name}: Layer 3: Outgoing interface selected ({out_interface})")
                print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
                frame = self.frame_send(packet, next_hop_ip, out_interface)
                return frame, out_interface

        raise ValueError(f"No route found for destination IP: {packet.dst_IP}")

    def relay(self, frame, in_interface):
        """Full round-trip: receive frame, forward to destination, relay response back"""
        #forward direction
        packet = self.receive_frame(frame, in_interface)
        out_frame, out_interface = self.forward_packet(packet)

        # deliver to connected host, get ACK frame back
        response_frame = self.connected_devices[out_interface].handle_incoming(out_frame)

        # reverse direction — ACK comes back through router
        response_packet = self.receive_frame(response_frame, out_interface)
        reverse_frame, reverse_interface = self.forward_packet(response_packet)
        return reverse_frame