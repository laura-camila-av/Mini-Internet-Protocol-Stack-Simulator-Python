import protocol

class Host:
    def __init__(self, name, ip_addr, mac_addr, arp_table):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
        self.arp_table = arp_table

    # LAYER 2 HANDLING 
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
    
class Router:
    def __init__(self, name, arp_table, interfaces):
        self.name = name
        self.arp_table = arp_table
        self.interfaces = interfaces
        self.mac_table = {}

    # LAYER 2 HANDLING
    def frame_send(self, packet, next_hop_ip, interface):

        src_mac = self.interfaces[interface][1]
        dst_mac = self.arp_table[next_hop_ip]

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}")

        # encapsulate frame and send
        frame = protocol.Layer2.encapsulate(src_mac, dst_mac, packet)

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded om {interface}")

        return frame
    
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

