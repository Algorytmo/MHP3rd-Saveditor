import os
import struct
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import offsets

cwd = os.getcwd()
root = tk.Tk()

characters_data = [
    {
        "name_offset": offsets.name_char1,
        "sex_offset": offsets.sex_char1,
        "money_offset": offsets.money_char1,
        "bag_offsets": offsets.bag_char1,
        "chest_item_offsets": offsets.item_chest1,
        "equip_item_offsets": offsets.equip_chest1
    },
    {
        "name_offset": offsets.name_char2,
        "sex_offset": offsets.sex_char2,
        "money_offset": offsets.money_char2,
        "bag_offsets": offsets.bag_char2,
        "chest_item_offsets": offsets.item_chest2,
        "equip_item_offsets": offsets.equip_chest2
    },
    {
        "name_offset": offsets.name_char3,
        "sex_offset": offsets.sex_char3,
        "money_offset": offsets.money_char3,
        "bag_offsets": offsets.bag_char3,
        "chest_item_offsets": offsets.item_chest3,
        "equip_item_offsets": offsets.equip_chest3
    },
]

characters = [
    offsets.Character(
        offsets.save_path,
        char_data["bag_offsets"],
        char_data["chest_item_offsets"],
        char_data["equip_item_offsets"],
        offsets.id_file
    )
    for char_data in characters_data
]

loaded_characters = []
for idx, (char, char_data) in enumerate(zip(characters, characters_data), start=1):
    char.load_file()
    name = char.read_name(char_data["name_offset"], 16)
    if name:
        sex = char.read_2byte(char_data["sex_offset"], 2)
        bag = char.read_bag()
        item_inventory = char.read_item_chest()
        equip_inventory = char.read_equip_chest()
        money = char.read_4byte(char_data["money_offset"], 4)
        loaded_characters.append({
            "character": char,
            "name": name,
            "sex": sex,
            "money": money,
            "money_offset": char_data["money_offset"],
            "bag": bag,
            "item_inventory": item_inventory,
            "equip_inventory": equip_inventory
        })

def update_dropdown(event, dropdown, original_values):
    typed = dropdown.get().lower()
    filtered = [v for v in original_values if typed in v.lower()]
    dropdown['values'] = filtered

def create_edit_window():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Item")
    edit_window.iconbitmap(os.path.join(cwd, "data/icon.ico"))
    edit_window.grab_set()
    return edit_window

def create_inventory_tree(parent_frame, label_text, inventory_data, columns, shared_db, inventory_type, character, all_equip_index=None):
    inventory_frame = tk.Frame(parent_frame)
    tk.Label(inventory_frame, text=label_text, font=("Arial", 12, "bold")).pack(pady=2)
    
    tree_frame = tk.Frame(inventory_frame)
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
    for col in columns:
        tree.heading(col, text=col)
    
    if inventory_type in ("item", "equip"):
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    else:
        tree.pack(fill="both", expand=True)
    
    tree_frame.pack(fill="both", padx=5)
    
    for item in inventory_data:
        values = [item[column] for column in columns]
        tree.insert("", "end", values=values)
    
    tree.character = character
    tree.inventory_type = inventory_type
    tree.bind("<Double-1>", lambda event: handle_double_click(event, tree, shared_db, all_equip_index))
    return inventory_frame

def create_character_frame(character_data, parent_frame):
    frame = tk.Frame(parent_frame, borderwidth=2, relief="solid")
    frame.pack(side="top", pady=10, fill="x")
    tk.Label(frame, text=f"Name: {character_data['name']}", font=("Arial", 14)).pack(pady=2)
    tk.Label(frame, text=f"Sex: {'Male' if character_data['sex'] == 1 else 'Female'}", font=("Arial", 14)).pack(pady=2)
    money_label = tk.Label(frame, text=f"Money: {character_data['money']}z", font=("Arial", 14))
    money_label.pack(pady=2)
    tk.Button(frame, text="Add Max Money", command=lambda: add_max_money(character_data["character"].file_path, character_data["money_offset"], money_label)).pack(pady=5)
    inventories_frame = tk.Frame(frame)
    inventories_frame.pack(side="top", fill="x")
    bag_tree = create_inventory_tree(
        inventories_frame, "Bag Items", character_data["bag"],
        ["Slot", "Name", "Quantity"], offsets.Character.shared_db,
        inventory_type="bag", character=character_data["character"]
    )
    bag_tree.pack(side="left", padx=5, fill="y")
    item_tree = create_inventory_tree(
        inventories_frame, "Item Inventory", character_data["item_inventory"],
        ["Slot", "Name", "Quantity"], offsets.Character.shared_db,
        inventory_type="item", character=character_data["character"]
    )
    item_tree.pack(side="left", padx=5, fill="y")
    equip_tree = create_inventory_tree(
        inventories_frame, "Equip Inventory", character_data["equip_inventory"],
        ["Slot", "Type", "Name"], offsets.Character.shared_db,
        inventory_type="equip", character=character_data["character"],
        all_equip_index=offsets.all_equip_index
    )
    equip_tree.pack(side="left", padx=5, fill="y")

def handle_double_click(event, tree, shared_db, all_equip_index=None):
    item_id = tree.identify_row(event.y)
    column_id = tree.identify_column(event.x)
    if not item_id or not tree.exists(item_id):
        messagebox.showerror("Error", "Selected item not found.")
        return
    current_values = tree.item(item_id, "values")
    try:
        slot_index = int(current_values[0]) - 1
    except (ValueError, IndexError):
        messagebox.showerror("Error", "Invalid slot value.")
        return
    if tree.inventory_type in ("bag", "item"):
        if column_id == "#3":
            new_quantity = simpledialog.askinteger("Edit Quantity", "Enter new quantity (1-99):", minvalue=1, maxvalue=99)
            if new_quantity is not None:
                update_quantity_in_table(tree, slot_index, new_quantity)
        elif column_id == "#2":
            edit_window = create_edit_window()
            tk.Label(edit_window, text="Choose new item:").pack(pady=5)
            selected_name = tk.StringVar()
            original_items = list(shared_db["items"].values())
            name_dropdown = ttk.Combobox(edit_window, textvariable=selected_name, values=original_items)
            name_dropdown.pack(pady=5)
            name_dropdown.bind('<KeyRelease>', lambda e: update_dropdown(e, name_dropdown, original_items))
            tk.Button(edit_window, text="Confirm", command=lambda: 
                      confirm_edit_item(name_dropdown.get(), tree, item_id, slot_index, shared_db, edit_window)
            ).pack(pady=10)
    elif tree.inventory_type == "equip":
        if column_id == "#2":
            edit_window = create_edit_window()
            tk.Label(edit_window, text="Choose new type:").pack(pady=5)
            selected_type = tk.StringVar()
            original_types = list(all_equip_index.keys())
            type_dropdown = ttk.Combobox(edit_window, textvariable=selected_type, values=original_types)
            type_dropdown.pack(pady=5)
            type_dropdown.bind('<KeyRelease>', lambda e: update_dropdown(e, type_dropdown, original_types))
            tk.Button(edit_window, text="Confirm", command=lambda: 
                      confirm_edit_type(selected_type.get(), tree, item_id, slot_index, shared_db, edit_window)
            ).pack(pady=10)
        elif column_id == "#3":
            edit_window = create_edit_window()
            tk.Label(edit_window, text="Choose new equip:").pack(pady=5)
            selected_name = tk.StringVar()
            current_type = current_values[1]
            original_equips = list(shared_db[current_type].values())
            name_dropdown = ttk.Combobox(edit_window, textvariable=selected_name, values=original_equips)
            name_dropdown.pack(pady=5)
            name_dropdown.bind('<KeyRelease>', lambda e: update_dropdown(e, name_dropdown, original_equips))
            tk.Button(edit_window, text="Confirm", command=lambda: 
                      confirm_edit_name(name_dropdown.get(), current_type, tree, item_id, slot_index, shared_db, edit_window)
            ).pack(pady=10)

def create_edit_window():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Item")
    edit_window.grab_set()
    return edit_window

def update_quantity_in_table(tree, slot_index, new_quantity):
    char = tree.character
    inv_type = tree.inventory_type
    if inv_type == "bag":
        offset_tuple = char.bag_offsets[slot_index]
    elif inv_type == "item":
        offset_tuple = char.item_chest_offsets[slot_index]
    else:
        messagebox.showerror("Error", "Invalid inventory type for quantity update.")
        return

    quantity_offset = int(offset_tuple[1], 16) if isinstance(offset_tuple[1], str) else offset_tuple[1]
    try:
        item_values = list(tree.item(tree.get_children()[slot_index], "values"))
        item_values[2] = new_quantity
        tree.item(tree.get_children()[slot_index], values=item_values)
        with open(char.file_path, "r+b") as f:
            f.seek(quantity_offset)
            f.write(struct.pack("<H", new_quantity))
        messagebox.showinfo("Success", "Quantity updated successfully!")
    except IndexError:
        messagebox.showerror("Error", "Invalid slot index.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update quantity: {e}")

def confirm_edit_item(new_name, tree, row_id, slot_index, shared_db, edit_window):
    char = tree.character
    inv_type = tree.inventory_type
    if inv_type == "bag":
        offset_tuple = char.bag_offsets[slot_index]
    elif inv_type == "item":
        offset_tuple = char.item_chest_offsets[slot_index]
    else:
        messagebox.showerror("Error", "Invalid inventory type for item update.")
        edit_window.destroy()
        return

    slot_offset = int(offset_tuple[0], 16) if isinstance(offset_tuple[0], str) else offset_tuple[0]
    item_id = next((key for key, value in shared_db["items"].items() if value == new_name), None)
    if not item_id:
        messagebox.showerror("Error", "Invalid item selected.")
        edit_window.destroy()
        return
    try:
        item_values = list(tree.item(row_id, "values"))
        item_values[1] = new_name
        tree.item(row_id, values=item_values)
        with open(char.file_path, "r+b") as f:
            f.seek(slot_offset)
            f.write(struct.pack("<H", int(item_id)))
        messagebox.showinfo("Success", f"Item updated to {new_name}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update item: {e}")
    edit_window.destroy()

def confirm_edit_type(new_type, tree, row_id, slot_index, shared_db, edit_window):
    char = tree.character
    if tree.inventory_type != "equip":
        messagebox.showerror("Error", "Invalid inventory type for type update.")
        edit_window.destroy()
        return

    offset_tuple = char.equip_chest_offsets[slot_index]
    slot_offset = int(offset_tuple[0], 16) if isinstance(offset_tuple[0], str) else offset_tuple[0]
    
    hex_value = offsets.all_equip_index.get(new_type)
    if not hex_value:
        messagebox.showerror("Error", "Invalid equipment type selected.")
        edit_window.destroy()
        return

    try:
        item_values = list(tree.item(row_id, "values"))
        item_values[1] = new_type
        tree.item(row_id, values=item_values)
        
        with open(char.file_path, "r+b") as f:
            f.seek(slot_offset)
            f.write(bytes.fromhex(hex_value))
            
        messagebox.showinfo("Success", f"Type updated to {new_type}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update type: {e}")
    finally:
        edit_window.destroy()

def confirm_edit_name(new_name, current_type, tree, row_id, slot_index, shared_db, edit_window):
    char = tree.character
    if tree.inventory_type != "equip":
        messagebox.showerror("Error", "Invalid inventory type for name update.")
        edit_window.destroy()
        return
    offset_tuple = char.equip_chest_offsets[slot_index]
    name_offset = int(offset_tuple[1], 16) if isinstance(offset_tuple[1], str) else offset_tuple[1]
    equip_id = next((key for key, value in shared_db[current_type].items() if value == new_name), None)
    if equip_id is None:
        messagebox.showerror("Error", "Invalid equipment name selected.")
        edit_window.destroy()
        return
    try:
        item_values = list(tree.item(row_id, "values"))
        item_values[2] = new_name
        tree.item(row_id, values=item_values)
        with open(char.file_path, "r+b") as f:
            f.seek(name_offset)
            f.write(struct.pack("<H", int(equip_id)))
        messagebox.showinfo("Success", f"Name updated to {new_name} (Type: {current_type}).")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update name: {e}")
    edit_window.destroy()

def add_max_money(save_path, money_offset, money_label):
    try:
        with open(save_path, "r+b") as f:
            f.seek(money_offset)
            f.write(struct.pack("<L", 9999999))
        money_label.config(text="Money: 9999999z")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add money: {e}")

def save_changes_action():
    response = messagebox.askyesno("Confirm", "Do you want to save changes?")
    if response:
        try:
            with open(os.path.join(cwd, "modifications_done.flag"), "w") as file:
                file.write("done")
            messagebox.showinfo("Success", "Changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")
        root.destroy()

def main():
    root.title("MHP3rd Savefile Editor")
    root.iconbitmap(os.path.join(cwd, "data/icon.ico"))
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    tk.Label(scrollable_frame, text="MHP3rd Savefile Editor", font=("Arial", 20, "bold")).pack(pady=10)
    tk.Button(scrollable_frame, text="Save Changes", command=save_changes_action).pack(pady=10)
    for character_data in loaded_characters:
        create_character_frame(character_data, scrollable_frame)
    root.update_idletasks()
    canvas_width = scrollable_frame.winfo_reqwidth() + scrollbar.winfo_width() + 5
    root.geometry(f"{canvas_width}x800")
    root.mainloop()
