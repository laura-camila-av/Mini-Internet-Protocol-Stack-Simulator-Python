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
    