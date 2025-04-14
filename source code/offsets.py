import struct
import json
import os


cwd = os.getcwd()
id_file = os.path.join(cwd, "data/data_id.json")
save_path = os.path.join(cwd, "save.BIN")

########################################################

name_char1 = 0x800
sex_char1 = 0x81a
money_char1 = 0x5d428
bag_char1 = [
    # 1st bag page
    (0x4fb8, 0x4fba), # 1st slot item, quantity
    (0x4fbc, 0x4fbe), # 2nd slot item, quantity
    (0x4fc0, 0x4fc2), # 3rd slot item, quantity
    (0x4fc4, 0x4fc6), # 4th slot item, quantity
    (0x4fc8, 0x4fca), # 5th slot item, quantity
    (0x4fcc, 0x4fce), # 6th slot item, quantity
    (0x4fd0, 0x4fd2), # 7th slot item, quantity
    (0x4fd4, 0x4fd6), # 8th slot item, quantity
    
    # 2nd bag page
    (0x4fd8, 0x4fda), # 1st slot item, quantity
    (0x4fdc, 0x4fde), # 2nd slot item, quantity
    (0x4fe0, 0x4fe2), # 3rd slot item, quantity
    (0x4fe4, 0x4fe6), # 4th slot item, quantity
    (0x4fe8, 0x4fea), # 5th slot item, quantity
    (0x4fec, 0x4fee), # 6th slot item, quantity
    (0x4ff0, 0x4ff2), # 7th slot item, quantity
    (0x4ff4, 0x4ff6), # 8th slot item, quantity
    
    # 3rd bag page
    (0x4ff8, 0x4ffa), # 1st slot item, quantity
    (0x4ffc, 0x4ffe), # 2nd slot item, quantity
    (0x5000, 0x5002), # 3rd slot item, quantity
    (0x5004, 0x5006), # 4th slot item, quantity
    (0x5008, 0x500a), # 5th slot item, quantity
    (0x500c, 0x500e), # 6th slot item, quantity
    (0x5010, 0x5012), # 7th slot item, quantity
    (0x5014, 0x5016), # 8th slot item, quantity
]

########################################################

name_char2 = 0x60800
sex_char2 = 0x6081a
money_char2 = 0xbd428
bag_char2 = [
    # 1st bag page
    (0x64fb8, 0x64fba), # 1st slot item, quantity
    (0x64fbc, 0x64fbe), # 2nd slot item, quantity
    (0x64fc0, 0x64fc2), # 3rd slot item, quantity
    (0x64fc4, 0x64fc6), # 4th slot item, quantity
    (0x64fc8, 0x64fca), # 5th slot item, quantity
    (0x64fcc, 0x64fce), # 6th slot item, quantity
    (0x64fd0, 0x64fd2), # 7th slot item, quantity
    (0x64fd4, 0x64fd6), # 8th slot item, quantity
    
    # 2nd bag page
    (0x64fd8, 0x64fda), # 1st slot item, quantity
    (0x64fdc, 0x64fde), # 2nd slot item, quantity
    (0x64fe0, 0x64fe2), # 3rd slot item, quantity
    (0x64fe4, 0x64fe6), # 4th slot item, quantity
    (0x64fe8, 0x64fea), # 5th slot item, quantity
    (0x64fec, 0x64fee), # 6th slot item, quantity
    (0x64ff0, 0x64ff2), # 7th slot item, quantity
    (0x64ff4, 0x64ff6), # 8th slot item, quantity
    
    # 3rd bag page          
    (0x64ff8, 0x64ffa), # 1st slot item, quantity
    (0x64ffc, 0x64ffe), # 2nd slot item, quantity
    (0x65000, 0x65002), # 3rd slot item, quantity
    (0x65004, 0x65006), # 4th slot item, quantity
    (0x65008, 0x6500a), # 5th slot item, quantity
    (0x6500c, 0x6500e), # 6th slot item, quantity
    (0x65010, 0x65012), # 7th slot item, quantity
    (0x65014, 0x65016), # 8th slot item, quantity
]

########################################################

name_char3 = 0xc0800
sex_char3 = 0xc081a
money_char3 = 0x11d428
bag_char3 = [
    # 1st bag page
    (0xc4fb8, 0xc4fba), # 1st slot item, quantity
    (0xc4fbc, 0xc4fbe), # 2nd slot item, quantity
    (0xc4fc0, 0xc4fc2), # 3rd slot item, quantity
    (0xc4fc4, 0xc4fc6), # 4th slot item, quantity
    (0xc4fc8, 0xc4fca), # 5th slot item, quantity
    (0xc4fcc, 0xc4fce), # 6th slot item, quantity
    (0xc4fd0, 0xc4fd2), # 7th slot item, quantity
    (0xc4fd4, 0xc4fd6), # 8th slot item, quantity
    
    # 2nd bag page
    (0xc4fd8, 0xc4fda), # 1st slot item, quantity
    (0xc4fdc, 0xc4fde), # 2nd slot item, quantity
    (0xc4fe0, 0xc4fe2), # 3rd slot item, quantity
    (0xc4fe4, 0xc4fe6), # 4th slot item, quantity
    (0xc4fe8, 0xc4fea), # 5th slot item, quantity
    (0xc4fec, 0xc4fee), # 6th slot item, quantity
    (0xc4ff0, 0xc4ff2), # 7th slot item, quantity
    (0xc4ff4, 0xc4ff6), # 8th slot item, quantity
    
    # 3rd bag page
    (0xc4ff8, 0xc4ffa), # 1st slot item, quantity
    (0xc4ffc, 0xc4ffe), # 2nd slot item, quantity
    (0xc5000, 0xc5002), # 3rd slot item, quantity
    (0xc5004, 0xc5006), # 4th slot item, quantity
    (0xc5008, 0xc500a), # 5th slot item, quantity
    (0xc500c, 0xc500e), # 6th slot item, quantity
    (0xc5010, 0xc5012), # 7th slot item, quantity
    (0xc5014, 0xc5016), # 8th slot item, quantity
]

########################################################

class Character:
    shared_db = None

    def __init__(self, file_path, offsets, id_file):
        self.file_path = file_path
        self.offsets = offsets
        self.id_file = id_file
        self.data = None
    
    def load_file(self):
        with open(self.file_path, 'rb') as file:
            self.data = file.read()

    def read_name(self, offset, size):
        raw_data = self.data[offset:offset + size]
        name = "".join(s for s in raw_data.decode("ascii", errors="ignore") if s.isprintable())
        return name.strip("\x00") if name else None

    def read_2byte(self, offset, size):
        raw_data = self.data[offset:offset + size]
        return struct.unpack("<H", raw_data)[0]  # "<": Little Endian, "H": Unsigned short (2 byte)

    def read_4byte(self, offset, size):
        raw_data = self.data[offset:offset + size]
        return struct.unpack("<L", raw_data)[0]  # "<": Little Endian, "L": Unsigned long (4 byte)

    def bag_items(self, slot_offset, quantity_offset):
        item_slot = int.from_bytes(self.data[slot_offset:slot_offset + 2], 'little')
        item_quantity = int.from_bytes(self.data[quantity_offset:quantity_offset + 2], 'little')
        return item_slot, item_quantity

    def load_shared_db(self):
        if Character.shared_db is None:
            with open(self.id_file, "r") as items:
                items_dict = json.load(items)
                Character.shared_db = dict(sorted(items_dict["items"].items(), key=lambda item: item[1]))
    
    def read_bag(self):
        self.load_shared_db()  # Loading shared db
        data = []
        for i, (slot_offset, quantity_offset) in enumerate(self.offsets, start=1):
            slot_item, slot_quantity = self.bag_items(slot_offset, quantity_offset)
            item_name = Character.shared_db.get(str(slot_item), "Unknown Item")
            data.append({"Slot": i, "Name": item_name, "Quantity": slot_quantity})
        return data

