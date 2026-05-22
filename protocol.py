import ipaddress
import config

class Layer2:

    type_ipv4 = "0x0800"

    def __init__(self, src_mac, dst_mac, payload):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.type = self.type_ipv4
        self.payload = payload
    
    @classmethod
    def encapsulate(cls, src_mac, dst_mac, payload):
        # return frame 
        return cls(src_mac, dst_mac, payload)
    
    def decapsulate(self):
        # decapsulate frame to obtain the payload
        return self.payload

#LAYER 3: NETWORK

class Layer3:
    #Assigns and validates source and destination IP addresses for Layer 3 packet
    def assign_ip_addresses(self, src_ip: str, dst_ip: str):

        self.source_IP = format_address(src_ip)
        self.dst_IP    = format_address(dst_ip)

        print(f"Layer 3: Source IP assigned: {self.source_IP}")
        print(f"Layer 3: Destination IP read: {self.dst_IP}")
    
    def __init__(self, source_IP, dst_IP, ttl, prot, size, payload):
        self.source_IP = source_IP
        self.dst_IP = dst_IP
        self.ttl = ttl
        self.prot = prot
        self.size = size
        self.payload = payload

    #encapsulates Layer (UDP-like) segment into Layer 3 (IP-like) packet
    def encapsulate_to_IP_packet(payload: bytes, src_ip: str, dst_ip: str, ttl: int = 100, protocol: int = 17) -> dict:
    # Fixed IP header size in bytes: 4 (src_ip) + 4 (dst_ip) + 1 (ttl) + 1 (protocol) + 2 (total_length) = 12
        IP_HEADER_SIZE = 12

        total_length = IP_HEADER_SIZE + len(payload)

        return Layer3(
            source_IP = src_ip,
            dst_IP    = dst_ip,
            ttl=ttl,
            prot      = protocol,
            size      = total_length,
            payload   = payload
        )
    
    #Validate and format an IPv4 address string into a standardised form.
    def format_address(address) -> str:
        try:
            return str(ipaddress.IPv4Address(address))
        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IPv4 address: '{address}'")

    def get_address_subnet(address):
        if address in ipaddress.IPv4Network('10.0.1.0/24'):
            return ipaddress.IPv4Network('10.0.1.0/24')
        elif address in ipaddress.IPv4Network('10.0.2.0/24'):
            return ipaddress.IPv4Network('10.0.2.0/24')
        else:
            return "Address out of range" #improve
        #TO DO: announce routing decision

    def decrement_TTL(TTL):
        ttl -= 1 #decrements TTL value by 1 at each router hop.
        if ttl <= 0: #if TTL has reached 0 packet should be dropped
            raise ValueError("TTL expired: packet must be dropped.")
        return ttl

    def increment_TTL(TTL):
        ttl += 1
        if ttl > 255:
            raise ValueError("TTL overflow: value cannot exceed 255 (1-byte field limit).")
        return ttl
    
    #Delivers received IP packet to layer 4 id addressed to this host
    #Assumes Layer3 class has node_name attribute for log output
    def deliver_packet(self, packet: Layer3, local_ip: str, layer4):
        
        print(f"{self.node_name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.source_IP}, DST_IP={packet.dst_IP}, TTL={packet.ttl}")

        print(f"{self.node_name}: Layer 3: Destination IP read: {packet.dst_IP}")

        if packet.dst_IP == local_ip:
            print(f"{self.node_name}: Layer 3: Packet identified as local delivery")
            print(f"{self.node_name}: Layer 3: Segment delivered to Transport Layer")
            layer4.receive_segment(packet.payload) #need to adjust this based on what the receive segment function is called in layer 4
 
        else:
            print(f"{self.node_name}: Layer 3: Packet destination {packet.dst_IP} "
                f"does not match local IP {local_ip} — discarding packet.")