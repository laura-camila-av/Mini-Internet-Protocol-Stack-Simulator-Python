import protocol

class Host:
    def __init__(self, name, ip_addr, mac_addr, arp_table, src_port, dst_port):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
        self.arp_table = arp_table
        self.src_port = src_port
        self.dst_port = dst_port
        
        self.last_ack = None

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

        # call constructor to build header and create checksum
        segment = protocol.Layer4.encapsulate(self.src_port, self.dst_port, protocol.Layer4.DATA, seq_num, data)

        print(f"{self.name}: Layer 4: Checksum completed")
        print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={seq_num}) (encapsulation)")
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        # rdt2.2 (reliable data transfer v2.2)
        while True:
            # send ACK to network layer (NOT YET DEFINED)
            ack = self.Layer3.send_packet(segment)

            if ack.seg_type == protocol.Layer4.ACK and ack.seq_num == seq_num:
                print(f"{self.name}: Layer 4: ACK received: seq={ack.seq_num}")
                break
            else:
                print(f"{self.name}: Layer 4: Incorrect ACK received. Retransmitting segment seq={ack.seq_num}")
    
    def receive_segment(self, segment):

        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        # verify checksum
        if segment.verify_checksum():
            print(f"{self.name}: Layer 4: Checksum verified")
        else:
            print(f"{self.name}: Layer 4: Checksum verification failed. Segment discarded")
            if self.last_ack is not None:
                print(f"{self.name}: Layer 4: Resending last ACK seq{self.last_ack.seq_num}")
                return self.last_ack


        # if DATA
        if segment.seg_type == protocol.Layer4.DATA:
            # decapsulate segment and deliver to application layer
            data = segment.decapsulate()
            print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(data)}")

            # return ack to sender
            ack = protocol.Layer4.encapsulate(segment.src_port, segment.dst_port, protocol.Layer4.ACK, segment.seq_num)
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num}) (encapsulation)")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            # update last ack value in case of failure
            self.last_ack = ack

            return ack
        
        # if ACK
        if segment.seg_type == protocol.Layer4.ACK:
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")

            return segment

        
        return segment

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

