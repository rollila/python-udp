import struct


def serialize(id, location):
    return struct.pack('III', id, location[0], location[1])


def deserialize(packet):
    unpacked = struct.unpack('III', packet)
    return {
        'id': unpacked[0],
        'location': (unpacked[1], unpacked[2])
    }


def item_size():
    return struct.calcsize('III')
