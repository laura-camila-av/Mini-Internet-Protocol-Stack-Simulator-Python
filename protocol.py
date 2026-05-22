class Layer2:

    type_ipv4 = "0x0800"

    def __init__(self, src_mac, dst_mac, payload):
        # construct header
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

class Layer4:
    
    DATA = 0
    ACK = 1

    HEADER_SIZE = 10
    MAX_DATA_SIZE = 500


    def __init__(self, src_port, dst_port, seg_type, seq_num, data=b""):
        # construct header
        self.src_port = src_port
        self.dst_port = dst_port
        self.seg_type = seg_type
        self.seq_num = seq_num
        self.data = data
        self.length = self.HEADER_SIZE + len(data)
        self.checksum = self.calc_checksum()
    
    @classmethod
    def encapsulate(cls, src_port, dst_port, seg_type, seq_num, data=b""):
        # return segment 
        return cls(src_port, dst_port, seg_type, seq_num, data)
    
    def calc_checksum(self):
        # calculate checksum using UDP method
        total = (
            self.src_port
            + self.dst_port
            + self.length
            + self.seg_type
            + self.seq_num
            + sum(self.data)
        )
        # wraparound any overflow into remaining 16 bits
        while total > 0xFFFF:
            total = (total & 0xFFFF) + (total >> 16)
        return total
    
    def verify_checksum(self):
        # make sure checksum in header matches actual computed checksum
        return self.checksum == self.calc_checksum()
    
    def decapsulate(self):
        # unpackage segment and return data
        return self.data