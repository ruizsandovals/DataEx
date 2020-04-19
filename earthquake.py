import urllib.request  # instead of urllib2 like in Python 2.7
import json
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pickle import *


#
# Author: Sergio Ruiz Sandoval
# Date  : 04/10/2020
#

class EarthquakeInfo:

    def __init__(self, master):
        self.root = master
        self.w_quake = Toplevel(self.root)
        self.right_menu = None

        # Create quake tree view
        self.tv_quake = ttk.Treeview(self.w_quake)
        self.tv_quake.grid(row=3, column=2, rowspan=20, padx=(25, 0))
        self.tv_quake.config(height=20)

        # Create scroll bar for the treeview
        self.scrollbar = ttk.Scrollbar(self.w_quake, orient="vertical", command=self.tv_quake.yview)
        self.scrollbar.grid(row=3, column=2, rowspan=20, sticky="sen")
        self.tv_quake.configure(yscrollcommand=self.scrollbar.set)

        # bind right click to tv popup
        self.tv_quake.bind('<Button-3>', self.quake_popup)

        # create a popup menu
        self.popup_menu = Menu(self.w_quake, tearoff=0)
        self.popup_menu.add_command(label='Delete', command=self.delete_quake_item)

        # Insert save button
        self.save_button = ttk.Button(self.w_quake, text="Save Info")
        self.save_button.grid(row=3, column=4, padx=25)
        self.save_button.config(command=self.save_tv)

        # Insert read button
        self.save_button = ttk.Button(self.w_quake, text="Read Info")
        self.save_button.grid(row=4, column=4, padx=25, pady=25)
        self.save_button.config(command=self.read_tv)

        # Labels
        # Window Header
        ttk.Label(self.w_quake, text="USGS Magnitude 2.5+ Earthquakes", style='Header.TLabel').grid(row=0, column=0,
                                                                                                    columnspan=6,
                                                                                                    pady=25)

        # selected tree view item
        self.tree_item = ''

        # Show earthquake info
        self.show_earthquake_info()

    # Read tree view content
    def read_tv(self):
        # Dictionary
        root_dict = {}

        filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                              filetypes=(("eq files", "*.eq"), ("all files", "*.*")))
        self.w_quake.focus()

        # Open and read input file
        if filename != "":
            try:
                binary_file = open(filename, "rb")
                root_dict = load(binary_file)
                binary_file.close()
                del binary_file
            except Exception as e:
                messagebox.showinfo(title="Error reading the content", message=e)

            # Delete current tree
            for item in self.tv_quake.get_children():
                self.tv_quake.delete(item)

            # Insert root item
            self.tv_quake.insert('', '0', 'root', text=root_dict["root"]["text"], open=True)

            # Insert all locations and details
            for root in root_dict:
                for location in root_dict[root]["children"]:
                    if not self.tv_quake.exists(location):
                        self.tv_quake.insert('root', "end", location, text=location)

                    for details in root_dict[root]["children"][location]["children"]:
                        self.tv_quake.insert(location, "end", details,
                                             text=root_dict[root]["children"][location]["children"][details]["text"])
                        self.tv_quake.item(details,
                                           tags=root_dict[root]["children"][location]["children"][details]["tags"])
                        self.tv_quake.set(details, 'magnitude',
                                          root_dict[root]["children"][location]["children"][details]["values"][0])
                        self.tv_quake.set(details, 'felt',
                                          root_dict[root]["children"][location]["children"][details]["values"][1])

    # Save Treeview content
    def save_tv(self):
        # Num of items to save
        num_items = 0

        # Dictionaries to get all treeview data
        root_dict = {}

        for root_id in self.tv_quake.get_children():

            # Get root item
            root_item = self.tv_quake.item(root_id)
            location_dict = {}

            for location_id in self.tv_quake.get_children(root_id):

                # Get location item
                location_item = self.tv_quake.item(location_id)
                details_dict = {}

                for details_id in self.tv_quake.get_children(location_id):
                    # Get earthquake details
                    details_item = self.tv_quake.item(details_id)
                    details_dict.update({details_id: details_item})
                    num_items += 1

                # Add details item to the location dictionary
                location_item.update({"children": details_dict})
                location_dict.update({location_id: location_item})

            # Add locations dictionary to root dictionary
            root_item.update({"children": location_dict})
            root_dict.update({"root": root_item})

        # If there are element to save, ask for location
        if num_items > 0:
            filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                    filetypes=(("eq files", "*.eq"), ("all files", "*.*")))
            if filename != "":
                try:
                    if filename.find(".") == -1:
                        filename = filename + ".eq"
                    binary_file = open(filename, "wb")
                    dump(root_dict, binary_file)
                    binary_file.close()
                    del binary_file
                except Exception as e:
                    messagebox.showinfo(title="Error saving the content", message=e)
        self.w_quake.focus()

    # Delete selected tree branch
    def delete_quake_item(self):
        if self.tree_item:
            # if messagebox.askyesno(title='Delete Item', message='Do you want delete: ' + self.tv_quake.item(self.tree_item, option='text') + "? "):
            self.tv_quake.delete(self.tree_item)
        self.w_quake.focus()

    # Popup menu for the tree view
    def quake_popup(self, event):
        self.popup_menu.post(event.x_root, event.y_root)
        self.tree_item = self.tv_quake.focus()

    # Shows earthquake info, it gets the information from a website
    def show_earthquake_info(self):
        # Connect to the data source
        url_data = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"

        # Open the URL and read the data
        web_url = urllib.request.urlopen(url_data)

        # Check if the page is available
        if web_url.getcode() == 200:
            # Use the json module to load the string data into a dictionary
            data = web_url.read()
            earthquake_data = json.loads(data)

        else:
            messagebox.showinfo(title="Receive an error from server",
                                message="Cannot retrieve results " + str(web_url.getcode()))
            return

        # Create a new window to show the information in a treeview
        self.w_quake.focus()
        self.w_quake.title("USGS Magnitude 2.5+ Earthquakes, Past Day")
        self.w_quake.geometry("1050x550")
        self.w_quake.resizable(False, False)
        self.w_quake.config(background="white")

        # Create root
        self.tv_quake.insert('', '0', 'root', text=earthquake_data["metadata"]["title"], open=True)

        # Create additional columns and reformat them
        self.tv_quake.config(columns=('magnitude', 'felt'))
        self.tv_quake.column('magnitude', width=100, anchor='center')
        self.tv_quake.column('felt', width=190, anchor='center')
        self.tv_quake.column('#0', width=570, anchor="w")
        self.tv_quake.heading('#0', text="Location", anchor="w")
        self.tv_quake.heading('magnitude', text="Magnitude")
        self.tv_quake.heading('felt', text="felt (#People)")

        # Configure tree view tag properties
        self.tv_quake.tag_configure('weak_earthquake', font=('consolas', 12, "italic"))
        self.tv_quake.tag_configure('regular_earthquake', font=('consolas', 12))
        self.tv_quake.tag_configure('strong_earthquake', font=('consolas', 12, "bold"))

        # Add locations
        for i in earthquake_data["features"]:
            place = i["properties"]["place"][i["properties"]["place"].find(",") + 1:].strip()
            if not self.tv_quake.exists(place):
                self.tv_quake.insert('root', "end", place, text=place)

        # Add earthquakes
        for i in earthquake_data["features"]:

            # Get the place (parent) and location
            place = i["properties"]["place"][i["properties"]["place"].find(",") + 1:].strip()
            location = i["properties"]["place"][:i["properties"]["place"].find(",")]
            item = i["id"]
            self.tv_quake.insert(place, "end", item, text=location, tags="regular_earthquake")

            # Get the magnitude and felt properties
            self.tv_quake.set(item, 'magnitude', "{0:,.1f}".format(i["properties"]["mag"]))
            self.tv_quake.set(item, 'felt', i["properties"]["felt"])

            # Tag according to magnitude
            if i["properties"]["mag"] <= 2.0:
                self.tv_quake.item(item, tags='weak_earthquake')
            elif i["properties"]["mag"] <= 4.0:
                self.tv_quake.item(item, tags='regular_earthquake')
            else:
                self.tv_quake.item(item, tags='strong_earthquake')
