# Mini-Internet-Protocol-Stack-Simulator-Python

## Instructions for running the program
Please run the following command:
``` 
python main.py <datasize> <source> <destination> 
```
With datasize being the size of the data in bytes, and source and destination being either "hostA" or "hostB".
If just running `python main.py <datasize>`, source and destination will default to Host A and Host B respectively.

## Running assumptions
- There is no packet loss or frame corruption 
- All transmissions are deterministic

## Implementation
Our project defined fixed parameters in `config.py`. All IP addresses, MAC addresses, router interfaces, ARP tables, routing tables as dictionaries, for quick access and lookup. We also stored the port numbers, as they were also fixed parameters.

We used `protocol.py` to define classes for each layer (e.g. Layer2, Layer3, Layer4) and prepare the data for transmission across its respective layer. We created a constructor, that created the header in the correct format the specified layer. We also created the core functions to format the data correctly (e.g. encapsulate and decapsulate, calculate checksum etc)

`devices.py` handles the actual sending and receving of data between layers. We created classes for Host and Router, and a constructor for each that device that instantiates it with the required features (routing table, IP address, MAC address etc). Each device handles sending of data at each layer:
    - **Layer 2** - *handling frame sending and receiving*
        - the device receives a packet from the network layer, and uses the next hop IP to perform a destination MAC address lookup via the ARP table
        - the packet is then encapsulated into a frame and send to the next device
        - when a device receives a frame, it checks the destination MAC address in the header against it's own address to see if it has reached its destination
        - as the network only consists of 2 hosts, if a frame reaches a host that is not the source, it has reached it's destination - this means that only the Router class has to handle frame forwarding
        - the Router class dynamically learns source MAC addresse from the incoming frames and puts them into its MAC table
        - if the frame is at its destination, the frame is decapsulated and sent to the network layer
    - **Layer 3** - *handling packet sending, routing and TTL handling*
        - 
    - **Layer 4** - *data segmentation, checksum validation and rdt2.2*
        - as the transport layer is an end-to-end process, it only interacts with the Host class
        - the host receives data from the application layer, and checks if the data size is within the accepted range (equal to or less than 500 bytes)
        - if the data exceeds 500 bytes, it is split into chunks of 500 bytes or less and each chunk is sent sequentially using the rdt2.2 alternating bit protocol
        - each chunk is encapsulated into a UDP-like segment, which involves computing a ones' complement wraparound checksum over all header fields and data, and storing it in the header
        - the segment is then passed down to the Network Layer for delivery to the destination host
        - when a segment is received, the destination host recomputes the checksum and compares it against the stored value — if they don't match, the segment is discarded
        - if the checksum is valid and the segment is a DATA segment, the data is delivered to the application layer and an ACK segment is sent back to the sender with the same sequence number
        - the sender implements the rdt2.2 loop — it waits for the correct ACK (matching sequence number) before proceeding to the next segment - if an incorrect or duplicate ACK is received, the current segment is retransmitted
        - sequence numbers alternate between 0 and 1 for each successive segment, allowing the receiver to detect and discard duplicates

    