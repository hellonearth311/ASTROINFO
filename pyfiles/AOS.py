from datetime import datetime, timedelta
from re import sub
from warnings import filterwarnings

import astropy.units as u
import customtkinter as ctk
import matplotlib.pyplot as plt
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from matplotlib import use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from pyfiles.classes import Asteroid
use('TkAgg')

# Create a coords function to get heliocentric coordinates of an object
def coords(horizons_id, time, id_type=None):
    """
    Returns the heliocentric coordinates of an object from JPL Horizons.
    :param time: The time of the calculation in YYYY-MM-DD HH:MM:SS
    :param horizons_id: The Horizons ID of the object in question.
    :param id_type: Optional id-type for JPL Horizons.
    :return: Tuple (X, Y) coordinates in AU.
    """
    result = Horizons(id=horizons_id, location='500@0', epochs=Time(time).tdb.jd, id_type=id_type).vectors(refplane='earth')
    x_coord, y_coord = result['x'].quantity.to(u.AU).value[0], result['y'].quantity.to(u.AU).value[0]
    return float(x_coord), float(y_coord)
# Create a celestial body class
class CelestialBody:
    def __init__(self, plot: plt.subplots, start_time: str, color: str, name: str, fig_canvas: FigureCanvasTkAgg, horizons_id: str | float, radius_km: float = 695700.0, id_type=None):
        """
        A class representing a celestial body made for simplicity.
        :param plot: A matplotlib subplot for the body to be graphed on.
        :param start_time: The time of the object at the time of creation (used for getting heliocentric coordinates).
        :param color: The color of the object.
        :param fig_canvas: The FigureCanvasTkAgg that the planet will be plotted on.
        :param horizons_id: The horizons ID of the object.
        :param id_type: The ID type of the object; is usually either None or 'smallbody'.
        :param radius_km: The radius in km of the object (used for scale).
        """
        self.horizons_id = horizons_id
        self.color = color
        self.radius_au = radius_km / 1.4960e+8
        self.x, self.y = coords(horizons_id, id_type=id_type, time=start_time)
        self.obj = plt.Circle((self.x, self.y), radius=self.radius_au, color=color)
        self.plot = plot
        self.plot.add_artist(self.obj)
        self.name = name
        self.plot.text(self.x + 2 * self.radius_au, self.y, name, fontsize=10, ha='center', va='center', color='white')
        self.fig_canvas = fig_canvas
        self.id_type = id_type
    def __eq__(self, other):
        return (
            self.horizons_id == other.horizons_id
        )
    def upd(self, time):
        """Updates the object's position according to the current time and date."""
        try:
            self.obj.remove()  # First, remove the object.
            # Remove texts in the global function.
            self.x, self.y = coords(self.horizons_id, id_type=self.id_type, time=time)  # Update the time accordingly, and get new coordinates.
            self.obj = plt.Circle((self.x, self.y), radius=self.radius_au, color=self.color)  # Redraw the circle.
            self.plot.add_artist(self.obj)  # Adds the circle to the plot.
            self.plot.text(self.x + 2 * self.radius_au, self.y, self.name, fontsize=10, ha='center', va='center')  # Readds the text.
        except ValueError:
            pass
# Create a placeholdertext class for the large text box where objects are inputted
class PlaceholderText(ctk.CTkTextbox):
    def __init__(self, master=None, placeholder="Enter an asteroid ID here...", **kwargs):
        """
        A class representing a text box that has a placeholder when it is empty.
        :param master: The master window of the text box.
        :param placeholder: The placeholder text for the text box.
        """
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.insert("1.0", self.placeholder)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        if self.get("1.0", "end-1c") == self.placeholder:
            self.delete("1.0", "end")
            self.tag_remove("placeholder", "1.0", "end")

    def on_focus_out(self, event):
        if not self.get("1.0", "end-1c"):
            self.insert("1.0", self.placeholder)
            self.tag_add("placeholder", "1.0", "end")

class ORBITALSIM(ctk.CTk):
    def __init__(self, time: None | str = None):
        """
        The new and improved orbital simulation class.
        :param time: The time of the simulation at the start. If nothing is entered, then it automatically becomes
        the current date and time of the initialization. If it is an invalid string, it is reset to the default.
        """
        # <editor-fold desc="Super Call and Root Settings">
        super().__init__()
        self.title("ASTROINFO Orbital Simulation")
        self.tk_setPalette(activeBackground='#4b4b4b', foreground='white', activeForeground='white', background='#3b3b3b')
        filterwarnings(action='ignore')  # Ignore erfa warnings
        # </editor-fold>
        # <editor-fold desc="Fig and Ax settings"
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.fig.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)
        self.ax.set_aspect('equal')
        self.ax.axes.format_coord = lambda x, y: ""
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        # </editor-fold>
        # <editor-fold desc="Canvas and Toolbar Settings">
        self.canvas_frame = ctk.CTkFrame(self, border_width=1)
        self.canvas_frame.grid(row=0, column=0, sticky='nsew', padx=6, pady=6, rowspan=20)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().config(bg='#2b2b2b', relief='flat', borderwidth=0)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        self.toolbarframe = ctk.CTkFrame(self.canvas_frame, fg_color='#3b3b3b', corner_radius=8, bg_color='#2b2b2b')
        self.toolbarframe.grid(row=1, column=0, sticky='nsew', padx=6, pady=6)
        self.nested_frame = ctk.CTkFrame(self.toolbarframe, fg_color='#3b3b3b')
        self.nested_frame.grid(row=0, column=0, sticky='nsew', pady=0, padx=(110, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.nested_frame)
        self.toolbar.config(bg='#3b3b3b')
        for button in self.toolbar.winfo_children():
            button.config(background='#3b3b3b')
        self.toolbar.update()
        # </editor-fold>
        # <editor-fold desc="Widgets">
        # <editor-fold desc="Date Entries">
        self.date_entries = dict()
        self.date_entries['frame'] = ctk.CTkFrame(self, height=40)
        self.date_entries['frame'].grid(row=0, column=1, columnspan=11, padx=6, sticky='new', pady=6)
        self.date_entries['year'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="YYYY", font=('Roboto', 30), width=90)
        self.date_entries['year'].grid(row=0, column=1, sticky='nsew', pady=6, padx=(6, 0))
        self.date_entries['month'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['month'].grid(row=0, column=3, sticky='nsew', pady=6)
        self.date_entries['day'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="DD", font=('Roboto', 30), width=55)
        self.date_entries['day'].grid(row=0, column=5, padx=(0, 3), sticky='nsew', pady=6)

        self.date_entries['hour'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="HH", font=('Roboto', 30), width=58)
        self.date_entries['hour'].grid(row=0, column=6, padx=(3, 0), sticky='nsew', pady=6)
        self.date_entries['minute'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['minute'].grid(row=0, column=8, sticky='nsew', pady=6)
        self.date_entries['second'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="SS", font=('Roboto', 30), width=55)
        self.date_entries['second'].grid(row=0, column=10, padx=(0, 3), sticky='nsew', pady=6)
        self.date_entries['submit'] = ctk.CTkButton(self.date_entries['frame'], text='GO', font=('Roboto', 30), command=lambda: self.set_date_time())
        self.date_entries['submit'].grid(row=0, column=11, padx=(3, 6), sticky='nsew', columnspan=2, pady=6)
        # </editor-fold>
        # <editor-fold desc="Object Input">
        self.object_input = PlaceholderText(self, font=('Roboto', 20), placeholder='Enter object identifiers here, line by line...')
        self.object_input.grid(row=1, column=1, rowspan=17, columnspan=11, sticky='nsew', padx=6, pady=6)
        self.object_set = ctk.CTkButton(self, font=('Roboto', 30), text='ADD OBJECTS', command=lambda: self.add_inputted_objects())
        self.object_set.grid(row=18, column=1, columnspan=11, sticky='nsew', padx=6, pady=6)
        # </editor-fold>
        # <editor-fold desc="Time Travel"
        self.time_travel_frame = ctk.CTkFrame(self)
        self.time_travel_frame.grid(row=19, column=1, sticky='sew', columnspan=11, padx=6, pady=6)
        self.backward_button = ctk.CTkButton(self.time_travel_frame, text='<<', font=('Roboto', 20), command=lambda: self.time_backward())
        self.backward_button.grid(row=0, column=0, sticky='nsew', columnspan=3, padx=6, pady=6)
        self.step_entry = ctk.CTkEntry(self.time_travel_frame, font=('Roboto', 20), placeholder_text='Enter step length (hrs)...', width=250)
        self.step_entry.grid(row=0, column=4, sticky='nsew', padx=6, pady=6)
        self.forward_button = ctk.CTkButton(self.time_travel_frame, text='>>', font=('Roboto', 20), command=lambda: self.time_forward())
        self.forward_button.grid(row=0, column=5, sticky='nsew', columnspan=3, padx=6, pady=6)
        # </editor-fold>
        # </editor-fold>
        # <editor-fold desc="Global Variables">
        if time is not None:
            try:
                self.time = (datetime.strptime(time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bodies = list()
        # </editor-fold>
        self.create_defaults()
    def update_sim(self, hours=0):
        """Updates the simulation."""
        if hours > 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif hours < 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=(hours * -1))).strftime("%Y-%m-%d %H:%M:%S")
        for text in self.ax.texts:  # First, remove the texts.
            text.set_visible(False)
            del text
        for body in self.bodies:  # Then, update the bodies accordingly.
            body.upd(self.time)
        self.canvas.draw()
    def add_body(self, horizons_id: str, color: str, name: str, radius_km: float, id_type: str | None = None):
        """Adds a celestial body to the simulation."""
        if CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time) in self.bodies:
            # This means the object already exists
            del obj
            return None
        else:  # This means the object doesn't exist
            obj = CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time)
            self.bodies.append(obj)
            self.update_sim()
    def remove_body(self, horizons_id: str, color: str, name: str, radius_km: float):
        """Removes an object from the simulation."""
        if obj := CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, start_time=self.time) in self.bodies:
            # This means the object exists
            self.bodies.remove(self.bodies.index(obj))
            del obj
            self.update_sim()
        else:
            pass
    def create_defaults(self):
        """Creates the default bodies (the inner solar system + Jupiter, more planets coming soon)"""
        self.add_body(horizons_id='10', color='orange', name='Sun', radius_km=695700)  # The sun
        self.add_body(horizons_id='199', radius_km=2440, color='grey', name='Mercury')  # Mercury
        self.add_body(horizons_id='299', radius_km=6052, color='orange', name='Venus')  # Venus
        self.add_body(horizons_id='399', radius_km=6378, color='blue', name='Earth')  # Earth
        self.add_body(horizons_id='301', radius_km=1737.5, color='silver', name='Moon')  # The moon
        self.add_body(horizons_id='499', radius_km=2110.29, color='red', name='Mars')  # Mars
        self.add_body(horizons_id='599', radius_km=69911, color='navajowhite', name='Jupiter')  # Jupiter
        self.canvas.draw()
    def set_date_time(self):
        """Sets the date and time according to the user's input."""
        initial_time = self.time
        try:
            self.time = (
            (f"{self.date_entries['year'].get()}-{self.date_entries['month'].get()}-{self.date_entries['day'].get()} {self.date_entries['hour'].get()}:{self.date_entries['minute'].get()}:"
             f"{self.date_entries['second'].get()}").replace("Jan", '01').replace("Feb", '02').replace("Mar", '03').replace("Apr", '04').replace(
                "May", '05').replace("Jun", '06').replace("Jul", '07').replace("Aug", '08').replace("Sep", '09').replace(
                "Oct", "10").replace("Nov", "11").replace("Dec", "12").replace("SS", f"{datetime.now().second}").replace(
                ":MM:", f":{datetime.now().minute}:").replace("HH", f"{datetime.now().hour}").replace("DD", f"{datetime.now().date().day}").replace(
                "-MM-", f"-{datetime.now().date().month}-").replace("YYYY", f"{datetime.now().date().year}"))
            formatted_time = sub(r'(....)-(\d{1, 2})-(\d{1, 2})', r'\1-0\2-0\3', self.time)
            formatted_time = sub(r' (\d):', r' 0\1:', formatted_time)
            self.time = sub(r':(\d):', r':0\1:', formatted_time)
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")  # Check if the time string is valid
            self.update_sim()
        except ValueError:
            self.time = initial_time
            self.update_sim()
    def time_forward(self):
        """Moves the time forward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=step)
        except (ValueError, AttributeError, KeyError):
            pass
    def time_backward(self):
        """Moves the time backward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=-step)
        except (ValueError, AttributeError, KeyError):
            pass
    def add_inputted_objects(self):
        """Adds the objects that were put into the text box by the user."""
        obj_str = self.object_input.get("1.0", ctk.END)
        object_data = dict()
        invalid_objs = list()
        self.bodies.clear()
        self.create_defaults()
        for id in obj_str.splitlines():
            try:
                if id == "" or id.isspace():
                    pass
                else:
                    asteroid = Asteroid(id)
                    # Assume the asteroid has a nickname (e.g. 4 VESTA, or 99942 APOPHIS)
                    IAU = asteroid.identifiers['SPKID']
                    full_name = asteroid.identifiers['full name']
                    first_space_index = full_name.index(' ')
                    if int(IAU) <= 4_000_000:
                        try:
                            second_space_index = full_name.index(' ', first_space_index + 1)
                            third_space_index = full_name.index(' ', second_space_index + 1)
                        except Exception:
                            second_space_index = None

                        if second_space_index is not None:
                            name = full_name[first_space_index + 1:second_space_index]
                        else:
                            name = full_name[:first_space_index]
                    else:
                        name = asteroid.identifiers['full name']
                    try:
                        if asteroid.physical_properties['diameter']['km'] != 'Unavailable':
                            radius_km = float(asteroid.physical_properties['diameter']['km']) / 2
                        else:
                            radius_km = 1  # Average
                    except KeyError:
                        radius_km = 1  # Average

                    if radius_km is not None:
                        object_data[str(IAU)] = {'radius': float(radius_km), 'name': name, 'fullname': full_name}
                    else:
                        object_data[str(IAU)] = {'radius': None, 'name': name, 'fullname': full_name}

            except (AttributeError, KeyError, ValueError):
                pass

        for iau, dictionary in object_data.items():
            if dictionary['radius'] is not None:
                try:
                    self.add_body(horizons_id=dictionary['name'], color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                except ValueError:
                    try:
                        self.add_body(horizons_id=iau, color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                    except ValueError:
                        pass
class TOPLEVELORBITALSIM(ctk.CTkToplevel):
    def __init__(self, time: None | str = None):
        """
        The new and improved orbital simulation class, but for a toplevel window.
        :param time: The time of the simulation at the start. If nothing is entered, then it automatically becomes
        the current date and time of the initialization. If it is an invalid string, it is reset to the default.
        """
        # <editor-fold desc="Super Call and Root Settings">
        super().__init__()
        self.title("ASTROINFO Orbital Simulation")
        self.tk_setPalette(activeBackground='#4b4b4b', foreground='white', activeForeground='white', background='#3b3b3b')
        filterwarnings(action='ignore')  # Ignore erfa warnings
        # </editor-fold>
        # <editor-fold desc="Fig and Ax settings"
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.fig.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)
        self.ax.set_aspect('equal')
        self.ax.axes.format_coord = lambda x, y: ""
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        # </editor-fold>
        # <editor-fold desc="Canvas and Toolbar Settings">
        self.canvas_frame = ctk.CTkFrame(self, border_width=1)
        self.canvas_frame.grid(row=0, column=0, sticky='nsew', padx=6, pady=6, rowspan=20)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().config(bg='#2b2b2b', relief='flat', borderwidth=0)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        self.toolbarframe = ctk.CTkFrame(self.canvas_frame, fg_color='#3b3b3b', corner_radius=8, bg_color='#2b2b2b')
        self.toolbarframe.grid(row=1, column=0, sticky='nsew', padx=6, pady=6)
        self.nested_frame = ctk.CTkFrame(self.toolbarframe, fg_color='#3b3b3b')
        self.nested_frame.grid(row=0, column=0, sticky='nsew', pady=0, padx=(110, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.nested_frame)
        self.toolbar.config(bg='#3b3b3b')
        for button in self.toolbar.winfo_children():
            button.config(background='#3b3b3b')
        self.toolbar.update()
        # </editor-fold>
        # <editor-fold desc="Widgets">
        # <editor-fold desc="Date Entries">
        self.date_entries = dict()
        self.date_entries['frame'] = ctk.CTkFrame(self, height=40)
        self.date_entries['frame'].grid(row=0, column=1, columnspan=11, padx=6, sticky='new', pady=6)
        self.date_entries['year'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="YYYY", font=('Roboto', 30), width=90)
        self.date_entries['year'].grid(row=0, column=1, sticky='nsew', pady=6, padx=(6, 0))
        self.date_entries['month'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['month'].grid(row=0, column=3, sticky='nsew', pady=6)
        self.date_entries['day'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="DD", font=('Roboto', 30), width=55)
        self.date_entries['day'].grid(row=0, column=5, padx=(0, 3), sticky='nsew', pady=6)

        self.date_entries['hour'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="HH", font=('Roboto', 30), width=58)
        self.date_entries['hour'].grid(row=0, column=6, padx=(3, 0), sticky='nsew', pady=6)
        self.date_entries['minute'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['minute'].grid(row=0, column=8, sticky='nsew', pady=6)
        self.date_entries['second'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="SS", font=('Roboto', 30), width=55)
        self.date_entries['second'].grid(row=0, column=10, padx=(0, 3), sticky='nsew', pady=6)
        self.date_entries['submit'] = ctk.CTkButton(self.date_entries['frame'], text='GO', font=('Roboto', 30), command=lambda: self.set_date_time())
        self.date_entries['submit'].grid(row=0, column=11, padx=(3, 6), sticky='nsew', columnspan=2, pady=6)
        # </editor-fold>
        # <editor-fold desc="Object Input">
        self.object_input = PlaceholderText(self, font=('Roboto', 20), placeholder='Enter object identifiers here, line by line...')
        self.object_input.grid(row=1, column=1, rowspan=17, columnspan=11, sticky='nsew', padx=6, pady=6)
        self.object_set = ctk.CTkButton(self, font=('Roboto', 30), text='ADD OBJECTS', command=lambda: self.add_inputted_objects())
        self.object_set.grid(row=18, column=1, columnspan=11, sticky='nsew', padx=6, pady=6)
        # </editor-fold>
        # <editor-fold desc="Time Travel"
        self.time_travel_frame = ctk.CTkFrame(self)
        self.time_travel_frame.grid(row=19, column=1, sticky='sew', columnspan=11, padx=6, pady=6)
        self.backward_button = ctk.CTkButton(self.time_travel_frame, text='<<', font=('Roboto', 20), command=lambda: self.time_backward())
        self.backward_button.grid(row=0, column=0, sticky='nsew', columnspan=3, padx=6, pady=6)
        self.step_entry = ctk.CTkEntry(self.time_travel_frame, font=('Roboto', 20), placeholder_text='Enter step length (hrs)...', width=250)
        self.step_entry.grid(row=0, column=4, sticky='nsew', padx=6, pady=6)
        self.forward_button = ctk.CTkButton(self.time_travel_frame, text='>>', font=('Roboto', 20), command=lambda: self.time_forward())
        self.forward_button.grid(row=0, column=5, sticky='nsew', columnspan=3, padx=6, pady=6)
        # </editor-fold>
        # </editor-fold>
        # <editor-fold desc="Global Variables">
        if time is not None:
            try:
                self.time = (datetime.strptime(time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bodies = list()
        # </editor-fold>
        self.create_defaults()
    def update_sim(self, hours=0):
        """Updates the simulation."""
        if hours > 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif hours < 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=(hours * -1))).strftime("%Y-%m-%d %H:%M:%S")
        for text in self.ax.texts:  # First, remove the texts.
            text.set_visible(False)
            del text
        for body in self.bodies:  # Then, update the bodies accordingly.
            body.upd(self.time)
        self.canvas.draw()
    def add_body(self, horizons_id: str, color: str, name: str, radius_km: float, id_type: str | None = None):
        """Adds a celestial body to the simulation."""
        if CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time) in self.bodies:
            # This means the object already exists
            del obj
            return None
        else:  # This means the object doesn't exist
            obj = CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time)
            self.bodies.append(obj)
            self.update_sim()
    def remove_body(self, horizons_id: str, color: str, name: str, radius_km: float):
        """Removes an object from the simulation."""
        if obj := CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, start_time=self.time) in self.bodies:
            # This means the object exists
            self.bodies.remove(self.bodies.index(obj))
            del obj
            self.update_sim()
        else:
            pass
    def create_defaults(self):
        """Creates the default bodies (the inner solar system + Jupiter, more planets coming soon)"""
        self.add_body(horizons_id='10', color='orange', name='Sun', radius_km=695700)  # The sun
        self.add_body(horizons_id='199', radius_km=2440, color='grey', name='Mercury')  # Mercury
        self.add_body(horizons_id='299', radius_km=6052, color='orange', name='Venus')  # Venus
        self.add_body(horizons_id='399', radius_km=6378, color='blue', name='Earth')  # Earth
        self.add_body(horizons_id='301', radius_km=1737.5, color='silver', name='Moon')  # The moon
        self.add_body(horizons_id='499', radius_km=2110.29, color='red', name='Mars')  # Mars
        self.add_body(horizons_id='599', radius_km=69911, color='navajowhite', name='Jupiter')  # Jupiter
        self.canvas.draw()
    def set_date_time(self):
        """Sets the date and time according to the user's input."""
        initial_time = self.time
        try:
            self.time = (
            (f"{self.date_entries['year'].get()}-{self.date_entries['month'].get()}-{self.date_entries['day'].get()} {self.date_entries['hour'].get()}:{self.date_entries['minute'].get()}:"
             f"{self.date_entries['second'].get()}").replace("Jan", '01').replace("Feb", '02').replace("Mar", '03').replace("Apr", '04').replace(
                "May", '05').replace("Jun", '06').replace("Jul", '07').replace("Aug", '08').replace("Sep", '09').replace(
                "Oct", "10").replace("Nov", "11").replace("Dec", "12").replace("SS", f"{datetime.now().second}").replace(
                ":MM:", f":{datetime.now().minute}:").replace("HH", f"{datetime.now().hour}").replace("DD", f"{datetime.now().date().day}").replace(
                "-MM-", f"-{datetime.now().date().month}-").replace("YYYY", f"{datetime.now().date().year}"))
            formatted_time = sub(r'(....)-(\d{1, 2})-(\d{1, 2})', r'\1-0\2-0\3', self.time)
            formatted_time = sub(r' (\d):', r' 0\1:', formatted_time)
            self.time = sub(r':(\d):', r':0\1:', formatted_time)
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")  # Check if the time string is valid
            self.update_sim()
        except ValueError:
            self.time = initial_time
            self.update_sim()
    def time_forward(self):
        """Moves the time forward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=step)
        except (ValueError, AttributeError, KeyError):
            pass
    def time_backward(self):
        """Moves the time backward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=-step)
        except (ValueError, AttributeError, KeyError):
            pass
    def add_inputted_objects(self):
        """Adds the objects that were put into the text box by the user."""
        obj_str = self.object_input.get("1.0", ctk.END)
        object_data = dict()
        invalid_objs = list()
        self.bodies.clear()
        self.create_defaults()
        for id in obj_str.splitlines():
            try:
                if id == "" or id.isspace():
                    pass
                else:
                    asteroid = Asteroid(id)
                    # Assume the asteroid has a nickname (e.g. 4 VESTA, or 99942 APOPHIS)
                    IAU = asteroid.identifiers['SPKID']
                    full_name = asteroid.identifiers['full name']
                    first_space_index = full_name.index(' ')
                    if int(IAU) <= 4_000_000:
                        try:
                            second_space_index = full_name.index(' ', first_space_index + 1)
                            third_space_index = full_name.index(' ', second_space_index + 1)
                        except Exception:
                            second_space_index = None

                        if second_space_index is not None:
                            name = full_name[first_space_index + 1:second_space_index]
                        else:
                            name = full_name[:first_space_index]
                    else:
                        name = asteroid.identifiers['full name']
                    try:
                        if asteroid.physical_properties['diameter']['km'] != 'Unavailable':
                            radius_km = float(asteroid.physical_properties['diameter']['km']) / 2
                        else:
                            radius_km = 1  # Average
                    except KeyError:
                        radius_km = 1  # Average

                    if radius_km is not None:
                        object_data[str(IAU)] = {'radius': float(radius_km), 'name': name, 'fullname': full_name}
                    else:
                        object_data[str(IAU)] = {'radius': None, 'name': name, 'fullname': full_name}

            except (AttributeError, KeyError, ValueError):
                pass

        for iau, dictionary in object_data.items():
            if dictionary['radius'] is not None:
                try:
                    self.add_body(horizons_id=dictionary['name'], color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                except ValueError:
                    try:
                        self.add_body(horizons_id=iau, color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                    except ValueError:
                        pass
class FRAMEORBITALSIM(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, time: None | str = None):
        """
        The new and improved orbital simulation class, except it's for a frame.
        :param time: The time of the simulation at the start. If nothing is entered, then it automatically becomes
        the current date and time of the initialization. If it is an invalid string, it is reset to the default.
        """
        # <editor-fold desc="Super Call and Root Settings">
        super().__init__(master=master)
        self.title("ASTROINFO Orbital Simulation")
        self.tk_setPalette(activeBackground='#4b4b4b', foreground='white', activeForeground='white', background='#3b3b3b')
        filterwarnings(action='ignore')  # Ignore erfa warnings
        # </editor-fold>
        # <editor-fold desc="Fig and Ax settings"
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.fig.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)
        self.ax.set_aspect('equal')
        self.ax.axes.format_coord = lambda x, y: ""
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        # </editor-fold>
        # <editor-fold desc="Canvas and Toolbar Settings">
        self.canvas_frame = ctk.CTkFrame(self, border_width=1)
        self.canvas_frame.grid(row=0, column=0, sticky='nsew', padx=6, pady=6, rowspan=20)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().config(bg='#2b2b2b', relief='flat', borderwidth=0)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        self.toolbarframe = ctk.CTkFrame(self.canvas_frame, fg_color='#3b3b3b', corner_radius=8, bg_color='#2b2b2b')
        self.toolbarframe.grid(row=1, column=0, sticky='nsew', padx=6, pady=6)
        self.nested_frame = ctk.CTkFrame(self.toolbarframe, fg_color='#3b3b3b')
        self.nested_frame.grid(row=0, column=0, sticky='nsew', pady=0, padx=(110, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.nested_frame)
        self.toolbar.config(bg='#3b3b3b')
        for button in self.toolbar.winfo_children():
            button.config(background='#3b3b3b')
        self.toolbar.update()
        # </editor-fold>
        # <editor-fold desc="Widgets">
        # <editor-fold desc="Date Entries">
        self.date_entries = dict()
        self.date_entries['frame'] = ctk.CTkFrame(self, height=40)
        self.date_entries['frame'].grid(row=0, column=1, columnspan=11, padx=6, sticky='new', pady=6)
        self.date_entries['year'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="YYYY", font=('Roboto', 30), width=90)
        self.date_entries['year'].grid(row=0, column=1, sticky='nsew', pady=6, padx=(6, 0))
        self.date_entries['month'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['month'].grid(row=0, column=3, sticky='nsew', pady=6)
        self.date_entries['day'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="DD", font=('Roboto', 30), width=55)
        self.date_entries['day'].grid(row=0, column=5, padx=(0, 3), sticky='nsew', pady=6)

        self.date_entries['hour'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="HH", font=('Roboto', 30), width=58)
        self.date_entries['hour'].grid(row=0, column=6, padx=(3, 0), sticky='nsew', pady=6)
        self.date_entries['minute'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="MM", font=('Roboto', 30), width=70)
        self.date_entries['minute'].grid(row=0, column=8, sticky='nsew', pady=6)
        self.date_entries['second'] = ctk.CTkEntry(self.date_entries['frame'], placeholder_text="SS", font=('Roboto', 30), width=55)
        self.date_entries['second'].grid(row=0, column=10, padx=(0, 3), sticky='nsew', pady=6)
        self.date_entries['submit'] = ctk.CTkButton(self.date_entries['frame'], text='GO', font=('Roboto', 30), command=lambda: self.set_date_time())
        self.date_entries['submit'].grid(row=0, column=11, padx=(3, 6), sticky='nsew', columnspan=2, pady=6)
        # </editor-fold>
        # <editor-fold desc="Object Input">
        self.object_input = PlaceholderText(self, font=('Roboto', 20), placeholder='Enter object identifiers here, line by line...')
        self.object_input.grid(row=1, column=1, rowspan=17, columnspan=11, sticky='nsew', padx=6, pady=6)
        self.object_set = ctk.CTkButton(self, font=('Roboto', 30), text='ADD OBJECTS', command=lambda: self.add_inputted_objects())
        self.object_set.grid(row=18, column=1, columnspan=11, sticky='nsew', padx=6, pady=6)
        # </editor-fold>
        # <editor-fold desc="Time Travel"
        self.time_travel_frame = ctk.CTkFrame(self)
        self.time_travel_frame.grid(row=19, column=1, sticky='sew', columnspan=11, padx=6, pady=6)
        self.backward_button = ctk.CTkButton(self.time_travel_frame, text='<<', font=('Roboto', 20), command=lambda: self.time_backward())
        self.backward_button.grid(row=0, column=0, sticky='nsew', columnspan=3, padx=6, pady=6)
        self.step_entry = ctk.CTkEntry(self.time_travel_frame, font=('Roboto', 20), placeholder_text='Enter step length (hrs)...', width=250)
        self.step_entry.grid(row=0, column=4, sticky='nsew', padx=6, pady=6)
        self.forward_button = ctk.CTkButton(self.time_travel_frame, text='>>', font=('Roboto', 20), command=lambda: self.time_forward())
        self.forward_button.grid(row=0, column=5, sticky='nsew', columnspan=3, padx=6, pady=6)
        # </editor-fold>
        # </editor-fold>
        # <editor-fold desc="Global Variables">
        if time is not None:
            try:
                self.time = (datetime.strptime(time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bodies = list()
        # </editor-fold>
        self.create_defaults()
    def update_sim(self, hours=0):
        """Updates the simulation."""
        if hours > 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif hours < 0:
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=(hours * -1))).strftime("%Y-%m-%d %H:%M:%S")
        for text in self.ax.texts:  # First, remove the texts.
            text.set_visible(False)
            del text
        for body in self.bodies:  # Then, update the bodies accordingly.
            body.upd(self.time)
        self.canvas.draw()
    def add_body(self, horizons_id: str, color: str, name: str, radius_km: float, id_type: str | None = None):
        """Adds a celestial body to the simulation."""
        if CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time) in self.bodies:
            # This means the object already exists
            del obj
            return None
        else:  # This means the object doesn't exist
            obj = CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, id_type=id_type, start_time=self.time)
            self.bodies.append(obj)
            self.update_sim()
    def remove_body(self, horizons_id: str, color: str, name: str, radius_km: float):
        """Removes an object from the simulation."""
        if obj := CelestialBody(horizons_id=horizons_id, name=name, fig_canvas=self.canvas, radius_km=radius_km, color=color, plot=self.ax, start_time=self.time) in self.bodies:
            # This means the object exists
            self.bodies.remove(self.bodies.index(obj))
            del obj
            self.update_sim()
        else:
            pass
    def create_defaults(self):
        """Creates the default bodies (the inner solar system + Jupiter, more planets coming soon)"""
        self.add_body(horizons_id='10', color='orange', name='Sun', radius_km=695700)  # The sun
        self.add_body(horizons_id='199', radius_km=2440, color='grey', name='Mercury')  # Mercury
        self.add_body(horizons_id='299', radius_km=6052, color='orange', name='Venus')  # Venus
        self.add_body(horizons_id='399', radius_km=6378, color='blue', name='Earth')  # Earth
        self.add_body(horizons_id='301', radius_km=1737.5, color='silver', name='Moon')  # The moon
        self.add_body(horizons_id='499', radius_km=2110.29, color='red', name='Mars')  # Mars
        self.add_body(horizons_id='599', radius_km=69911, color='navajowhite', name='Jupiter')  # Jupiter
        self.canvas.draw()
    def set_date_time(self):
        """Sets the date and time according to the user's input."""
        initial_time = self.time
        try:
            self.time = (
            (f"{self.date_entries['year'].get()}-{self.date_entries['month'].get()}-{self.date_entries['day'].get()} {self.date_entries['hour'].get()}:{self.date_entries['minute'].get()}:"
             f"{self.date_entries['second'].get()}").replace("Jan", '01').replace("Feb", '02').replace("Mar", '03').replace("Apr", '04').replace(
                "May", '05').replace("Jun", '06').replace("Jul", '07').replace("Aug", '08').replace("Sep", '09').replace(
                "Oct", "10").replace("Nov", "11").replace("Dec", "12").replace("SS", f"{datetime.now().second}").replace(
                ":MM:", f":{datetime.now().minute}:").replace("HH", f"{datetime.now().hour}").replace("DD", f"{datetime.now().date().day}").replace(
                "-MM-", f"-{datetime.now().date().month}-").replace("YYYY", f"{datetime.now().date().year}"))
            formatted_time = sub(r'(....)-(\d{1, 2})-(\d{1, 2})', r'\1-0\2-0\3', self.time)
            formatted_time = sub(r' (\d):', r' 0\1:', formatted_time)
            self.time = sub(r':(\d):', r':0\1:', formatted_time)
            self.time = (datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")  # Check if the time string is valid
            self.update_sim()
        except ValueError:
            self.time = initial_time
            self.update_sim()
    def time_forward(self):
        """Moves the time forward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=step)
        except (ValueError, AttributeError, KeyError):
            pass
    def time_backward(self):
        """Moves the time backward according to the step set by the user."""
        try:
            step = round(float(self.step_entry.get()))
            self.update_sim(hours=-step)
        except (ValueError, AttributeError, KeyError):
            pass
    def add_inputted_objects(self):
        """Adds the objects that were put into the text box by the user."""
        obj_str = self.object_input.get("1.0", ctk.END)
        object_data = dict()
        invalid_objs = list()
        self.bodies.clear()
        self.create_defaults()
        for id in obj_str.splitlines():
            try:
                if id == "" or id.isspace():
                    pass
                else:
                    asteroid = Asteroid(id)
                    # Assume the asteroid has a nickname (e.g. 4 VESTA, or 99942 APOPHIS)
                    IAU = asteroid.identifiers['SPKID']
                    full_name = asteroid.identifiers['full name']
                    first_space_index = full_name.index(' ')
                    if int(IAU) <= 4_000_000:
                        try:
                            second_space_index = full_name.index(' ', first_space_index + 1)
                            third_space_index = full_name.index(' ', second_space_index + 1)
                        except Exception:
                            second_space_index = None

                        if second_space_index is not None:
                            name = full_name[first_space_index + 1:second_space_index]
                        else:
                            name = full_name[:first_space_index]
                    else:
                        name = asteroid.identifiers['full name']
                    try:
                        if asteroid.physical_properties['diameter']['km'] != 'Unavailable':
                            radius_km = float(asteroid.physical_properties['diameter']['km']) / 2
                        else:
                            radius_km = 1  # Average
                    except KeyError:
                        radius_km = 1  # Average

                    if radius_km is not None:
                        object_data[str(IAU)] = {'radius': float(radius_km), 'name': name, 'fullname': full_name}
                    else:
                        object_data[str(IAU)] = {'radius': None, 'name': name, 'fullname': full_name}

            except (AttributeError, KeyError, ValueError):
                pass

        for iau, dictionary in object_data.items():
            if dictionary['radius'] is not None:
                try:
                    self.add_body(horizons_id=dictionary['name'], color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                except ValueError:
                    try:
                        self.add_body(horizons_id=iau, color='grey', name=dictionary['fullname'], radius_km=dictionary['radius'], id_type='smallbody')
                    except ValueError:
                        pass

if __name__ == '__main__':
    main = ORBITALSIM()
    main.mainloop()
