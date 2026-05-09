import ipaddress

network_schemes = {

    #For use in the Network Layer
    "IP_addressing_scheme":{
        "Network_1": ipaddress.ip_network('10.0.1.0/24'), #need to check if this format actually works and will return the raw value
        "Network_2": ipaddress.ip_network('10.0.2.0/24'), 
        "Host_A": ipaddress.IPv4Address('10.0.1.10'),
        "R1_I1": ipaddress.IPv4Address('10.0.1.1'),
        "Host_B": ipaddress.IPv4Address('10.0.1.20'),
        "R1_I2": ipaddress.IPv4Address('10.0.2.1')
    },

    #For use in the Data Link Layer
    "MAC_addressing_scheme":{
        "Host_A":" AA:AA:AA:AA:AA:AA",
        "R1_I1": "BB:BB:BB:BB:BB:BB", #Router R1 (Interface 1)
        "R1_I2": "CC:CC:CC:CC:CC:CC", #Router R2 (Interface 2)
        "Host_B":"DD:DD:DD:DD:DD:DD"
    }

}

routing_tables = {

        Host_A = {
            "Host_B": {"next_hop":"R1_I1"}
            "R1": {"next_hop":"R1_I1"} #should this be R1 or R1_1 since that is the AP?
        },

        R1 = {
            "Host_A": {"next_hop":"Host_A"}
            "Host_B": {"next_hop":"Host_B"}
        },

        Host_B = {
            "Host_A": {"next_hop":"R2_T2"}
            "R1": {"next_hop":"R2_T2"}
        }

    }
   

