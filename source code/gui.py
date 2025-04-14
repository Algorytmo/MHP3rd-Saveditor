import os
import struct
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import offsets


cwd = os.getcwd()
root = tk.Tk()

# Characters offset
characters_data = [
    {"name_offset": offsets.name_char1, "sex_offset": offsets.sex_char1, "money_offset": offsets.money_char1, "bag_offsets": offsets.bag_char1},
    {"name_offset": offsets.name_char2, "sex_offset": offsets.sex_char2, "money_offset": offsets.money_char2, "bag_offsets": offsets.bag_char2},
    {"name_offset": offsets.name_char3, "sex_offset": offsets.sex_char3, "money_offset": offsets.money_char3, "bag_offsets": offsets.bag_char3},
]

characters = [
    offsets.Character(offsets.save_path, char_data["bag_offsets"], offsets.id_file)
    for char_data in characters_data
]

# Loading characters data
loaded_characters = []
for idx, (char, char_data) in enumerate(zip(characters, characters_data), start=1):
    char.load_file()
    name = char.read_name(char_data["name_offset"], 16)
    if name:
        sex = char.read_2byte(char_data["sex_offset"], 2)
        inventory = char.read_bag()
        money = char.read_4byte(char_data["money_offset"], 4)
        loaded_characters.append({
            "character": char,
            "name": name,
            "sex": sex,
            "money": money,
            "money_offset": char_data["money_offset"],
            "inventory": inventory
        })

# Character frame function
def create_character_frame(character_data, parent_frame):
    frame = tk.Frame(parent_frame, borderwidth=2, relief="solid")
    frame.pack(side="top", pady=10, fill="x")

    tk.Label(frame, text=f"Name: {character_data['name']}", font=("Arial", 14)).pack(pady=2)
    tk.Label(frame, text=f"Sex: {'Male' if character_data['sex'] == 1 else 'Female'}", font=("Arial", 14)).pack(pady=2)
    money_label = tk.Label(frame, text=f"Money: {character_data['money']}z", font=("Arial", 14))
    money_label.pack(pady=2)
    tk.Button(
        frame,
        text="Add Max Money",
        command=lambda: add_max_money(character_data["character"].file_path, character_data["money_offset"], money_label)
    ).pack(pady=5)

    tree = ttk.Treeview(frame, columns=("Slot", "Name", "Quantity"), show="headings", height=8)
    tree.heading("Slot", text="Slot")
    tree.heading("Name", text="Name")
    tree.heading("Quantity", text="Quantity")
    tree.pack(pady=5)

    for item in character_data["inventory"]:
        tree.insert("", "end", values=(item["Slot"], item["Name"], item["Quantity"]))

    tree.bind("<Double-1>", lambda event: handle_double_click(event, tree, character_data["character"], offsets.Character.shared_db))

# Double click function
def handle_double_click(event, tree, character, db):
    item_id = tree.identify_row(event.y)
    column_id = tree.identify_column(event.x)

    if not item_id:
        return

    if column_id == "#2":  # Edit item
        current_values = tree.item(item_id, "values")
        slot_index = int(current_values[0]) - 1
        edit_window = create_edit_window()
        tk.Label(edit_window, text="Choose new item:").pack(pady=5)

        selected_id = tk.StringVar()
        dropdown = create_dropdown(db, edit_window, selected_id)
        dropdown.bind("<KeyRelease>", lambda event: update_dropdown(event, dropdown, db))

        tk.Button(
            edit_window,
            text="Confirm",
            command=lambda: confirm_edit_item(dropdown, db, character, slot_index, tree, edit_window)
        ).pack(pady=10)
    elif column_id == "#3":  # Edit quantity
        current_values = tree.item(item_id, "values")
        slot_index = int(current_values[0]) - 1
        new_quantity = simpledialog.askinteger("Edit Quantity", "Enter new quantity (1-99):", minvalue=1, maxvalue=99)
        if new_quantity is not None:
            update_quantity_in_table(tree, character, db, slot_index, new_quantity)

# Support functions
def create_edit_window():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Item")
    edit_window.iconbitmap(os.path.join(cwd, "data/icon.ico"))
    return edit_window

def create_dropdown(db, parent, selected_id):
    dropdown = ttk.Combobox(parent, textvariable=selected_id, values=list(db.values()), state="normal")
    dropdown.config(width=50)
    dropdown.pack(pady=5)
    return dropdown

def update_dropdown(event, dropdown, db):
    value = dropdown.get().lower()
    filtered_items = [item for item in db.values() if value in item.lower()]
    dropdown.config(values=filtered_items)

def confirm_edit_item(dropdown, db, character, slot_index, tree, edit_window):
    chosen_item = dropdown.get()
    if chosen_item:
        item_id = next((key for key, value in db.items() if value == chosen_item), None)
        slot_offset, _ = character.offsets[slot_index]
        try:
            with open(character.file_path, "r+b") as char_file:
                char_file.seek(slot_offset)
                char_file.write(struct.pack("<H", int(item_id)))
            tree.item(tree.get_children()[slot_index], values=(slot_index + 1, db[item_id], tree.item(tree.get_children()[slot_index], "values")[2]))
            messagebox.showinfo("Success", "Item updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {e}")
        finally:
            edit_window.destroy()

def update_quantity_in_table(tree, character, db, slot_index, new_quantity):
    new_quantity = min(new_quantity, 99)
    _, quantity_offset = character.offsets[slot_index]
    try:
        with open(character.file_path, "r+b") as char_file:
            char_file.seek(quantity_offset)
            char_file.write(struct.pack("<H", new_quantity))
        item_values = list(tree.item(tree.get_children()[slot_index], "values"))
        item_values[2] = new_quantity
        tree.item(tree.get_children()[slot_index], values=item_values)
        messagebox.showinfo("Success", "Quantity updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update quantity: {e}")

def add_max_money(save_path, money_offset, money_label):
    try:
        with open(save_path, "r+b") as character:
            character.seek(money_offset)
            character.write(struct.pack("<L", 9999999))
        money_label.config(text="Money: 9999999z")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add money: {e}")

def save_changes_action():
    response = messagebox.askyesno("Confirm", "Do you want to save changes?")
    if response:
        open(os.path.join(cwd, "modifications_done.flag"), "w").write("done")
        root.destroy()

# Main tab with scrollbar
def main():
    root.title("MHP3rd Savefile Editor")

    # Icon tab
    root.iconbitmap(os.path.join(cwd, "data/icon.ico"))

    # Main tab
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title and Save Changes button
    tk.Label(scrollable_frame, text="MHP3rd Savefile Editor", font=("Arial", 20, "bold")).pack(pady=10)
    tk.Button(scrollable_frame, text="Save Changes", command=save_changes_action).pack(pady=10)

    for character_data in loaded_characters:
        create_character_frame(character_data, scrollable_frame)

    root.update_idletasks()
    canvas_width = scrollable_frame.winfo_reqwidth() + scrollbar.winfo_width() + 20
    root.geometry(f"{canvas_width}x800")

    root.mainloop()
