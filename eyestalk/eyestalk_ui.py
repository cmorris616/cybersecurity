import tkinter as tk
from tkinter import ttk


def start_ui(profiles={}):
    window = tk.Tk()
    window.title('EyeStalk')

    window_width = 1000
    window_height = 600
    window_left = int(window.winfo_screenwidth() / 2 - window_width / 2)
    window_top = int(window.winfo_screenheight() / 2 - window_height / 2)
    window.geometry(f"{window_width}x{window_height}+{window_left}+{window_top}")

    frm_profile = tk.Frame()
    frm_search = tk.Frame(master=frm_profile)
    lbl_search = tk.Label(master=frm_search, text='Search:')
    ent_search = tk.Entry(master=frm_search)
    tv_profiles = ttk.Treeview(master=frm_profile)

    frm_profile.grid(row=0, column=0)
    lbl_search.grid(row=0, column=0)
    ent_search.grid(row=0, column=1)
    frm_search.pack(fill=tk.X)
    tv_profiles.pack(fill=tk.BOTH, expand=True)

    frm_details = tk.Frame()
    lbl_details = tk.Label(master=frm_details, text="Test")

    frm_details.grid(row=0, column=1)
    lbl_details.pack(fill=tk.BOTH, expand=True)

    frm_buttons = tk.Frame()
    btn_close = tk.Button(master=frm_buttons, text="Close", command=window.destroy)

    frm_buttons.grid(row=1, column=1)
    btn_close.grid(row=0, column=1)

    populate_profiles(tv_profiles, profiles)

    window.mainloop()


def populate_profiles(tree_view, profiles={}, parent=""):
    keys = [key for key in profiles.keys()]
    keys.sort(key=str.casefold)

    for key in keys:

        if type(profiles[key]) is dict:
            if parent == "":
                item_text = profiles.get(key).get("Name")
            else:
                item_text = key

            current_parent = tree_view.insert(parent, len(tree_view.get_children()) + 1, None, text=item_text)
            populate_profiles(tree_view, profiles.get(key), current_parent)
        elif type(profiles[key]) is list:
            new_node = tree_view.insert(parent, "end", None, text=key)
            for item in profiles[key]:
                tree_view.insert(new_node, "end", None, text=item)
        # else:
        #     new_node = tree_view.insert(parent, "end", None, text=key)
        #     print(type(new_node))
        #     tree_view.insert(new_node, "end", None, text=profiles[key])

# def get_selected_node_value(tree_view, profiles={}):
