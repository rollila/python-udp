import struct


def serialize(seq_nr, id, location):
    return struct.pack('IIII', seq_nr, id, location[0], location[1])


def deserialize(packet):
    unpacked = struct.unpack('IIII', packet)
    return {
        'seq_nr': unpacked[0],
        'id': unpacked[1],
        'location': (unpacked[2], unpacked[3])
    }
