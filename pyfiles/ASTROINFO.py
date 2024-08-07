import customtkinter as ctk

from classes import Asteroid, search_by_date

class AStROINFO(ctk.CTk):
    def __init__(self):
        """The main ASTROINFO program."""
        super().__init__()
        self.asteroid = None
        self.title("AStROINFO Database")
        self.resizable(False, False)

        # <editor-fold desc="Labels">
        # Title label
        ctk.CTkLabel(self, text="AStROINFO Database", font=('Roboto', 30, 'bold'), corner_radius=8).grid(
            row=0, column=0, sticky='w', padx=6, pady=6, columnspan=2)
        # Asteroid entry
        self.asteroid_entry = ctk.CTkEntry(self, placeholder_text="Enter an asteroid ID...", font=('Roboto', 30), width=600)
        self.asteroid_entry.grid(row=0, column=2, columnspan=3, sticky='nsew', padx=6, pady=6)
        # Asteroid submit
        self.asteroid_submit = ctk.CTkButton(self, text='GO', font=('Roboto', 30), command=lambda: self.submit_asteroid(self.asteroid_entry.get()))
        self.asteroid_submit.grid(row=0, column=5, sticky='nsew', padx=6, pady=6)
        # Asteroid name
        self.asteroid_name = ctk.CTkLabel(self, text='Name', font=('Roboto', 30), fg_color='#3b3b3b', corner_radius=8)
        self.asteroid_name.grid(row=1, column=0, sticky='nsw', padx=6, pady=6, columnspan=3)
        # </editor-fold>
        # <editor-fold desc="Asteroid Identifiers">
        identifiers = ['IAU', 'SPKID']
        self.identifier_labels = dict()
        for identifier in identifiers:
            self.identifier_labels[identifier] = ctk.CTkLabel(self, text=identifier, font=('Roboto', 15), fg_color='#3b3b3b', corner_radius=8)
            self.identifier_labels[identifier].grid(row=2, column=0+identifiers.index(identifier), sticky='nsw', padx=6, pady=6)
        self.bind('<Return>', lambda e: self.submit_asteroid(self.asteroid_entry.get()))
        # </editor-fold>
        # <editor-fold desc="Physical Properties">
        pp_keys = ['rotational period', 'spectral type', 'absolute magnitude', 'diameter', 'density', 'surface gravity', 'escape velocity', 'mass', 'albedo', 'volume']
        self.pp_labels = dict()
        for pp in pp_keys:
            if pp_keys.index(pp) == 0:
                ctk.CTkLabel(self, text=pp.title(), font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=3+pp_keys.index(pp), column=0, sticky='nsew', pady=(6, 0), padx=(6, 0))
                self.pp_labels[pp] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.pp_labels[pp].grid(row=3+pp_keys.index(pp), column=1, sticky='nsew', columnspan=2, pady=(6, 0), padx=(0, 6))
            elif pp_keys[pp_keys.index(pp)] == pp_keys[-1]:
                ctk.CTkLabel(self, text=pp.title(), font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=3 + pp_keys.index(pp), column=0, sticky='nsew', pady=(0, 6), padx=(6, 0))
                self.pp_labels[pp] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.pp_labels[pp].grid(row=3 + pp_keys.index(pp), column=1, sticky='nsew', columnspan=2, pady=(0, 6), padx=(0, 6))
            else:
                ctk.CTkLabel(self, text=pp.title(), font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=3 + pp_keys.index(pp), column=0, sticky='nsew', padx=(6, 0))
                self.pp_labels[pp] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.pp_labels[pp].grid(row=3 + pp_keys.index(pp), column=1, sticky='nsew', columnspan=2, padx=(0, 6))
        # </editor-fold>
        # <editor-fold desc="Orbital Properties">
        op_keys = ['perihelion distance', 'aphelion distance', 'semi-major axis', 'eccentricity', 'mean anomaly', 'orbital period', 'orbit class', 'orbit id']
        self.op_labels = dict()
        for op in op_keys:
            if op_keys.index(op) == 0:
                ctk.CTkLabel(self, text=op.title(), font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=13+op_keys.index(op), column=0, sticky='nsew', pady=(6, 0), padx=(6, 0))
                self.op_labels[op] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.op_labels[op].grid(row=13 + op_keys.index(op), column=1, sticky='nsew', columnspan=2, pady=(6, 0), padx=(0, 6))
            elif op_keys[op_keys.index(op)] == op_keys[-1]:
                ctk.CTkLabel(self, text='Orbit ID', font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=13 + op_keys.index(op), column=0, sticky='nsew', pady=(0, 6), padx=(6, 0))
                self.op_labels[op] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.op_labels[op].grid(row=13 + op_keys.index(op), column=1, sticky='nsew', columnspan=2, pady=(0, 6), padx=(0, 6))
            else:
                ctk.CTkLabel(self, text=op.title(), font=('Roboto', 15), fg_color='#5D6E79', corner_radius=5).grid(
                    row=13 + op_keys.index(op), column=0, sticky='nsew', padx=(6, 0))
                self.op_labels[op] = ctk.CTkLabel(self, text='', font=('Roboto', 15), fg_color='#6D8391', corner_radius=5)
                self.op_labels[op].grid(row=13 + op_keys.index(op), column=1, sticky='nsew', columnspan=2, padx=(0, 6))
        # </editor-fold>
        # <editor-fold desc="Approaches">
        self.approaches_frame = ctk.CTkScrollableFrame(self, label_font=('Roboto', 20), label_text='Close Approach Data')
        self.approaches_frame.grid(row=1, column=3, sticky='nsew', columnspan=4, rowspan=9, padx=6, pady=6)
        placeholder = ctk.CTkLabel(self.approaches_frame, font=('Roboto', 15), text='Enter an asteroid ID to retrieve approaches.')
        placeholder.grid(row=0, column=0, columnspan=2, sticky='nsew')
        # </editor-fold>
        # <editor-fold desc="Search for Approaches">
        self.date_frame = ctk.CTkFrame(self)
        self.date_frame.grid(row=10, column=3, columnspan=4, rowspan=16, sticky='nsew', padx=6, pady=6)
        ctk.CTkLabel(self.date_frame, text='Find Close Approaches by Date Range', font=('Roboto', 20), fg_color='#3b3b3b', corner_radius=8).grid(
            row=0, column=0, columnspan=4, padx=6, pady=6, sticky='nsew')
        ctk.CTkLabel(self.date_frame, text='-', font=('Roboto', 20)).grid(row=1, column=1, padx=6, pady=6, sticky='nsew')
        self.date_search = ctk.CTkButton(self.date_frame, text='SEARCH', font=('Roboto', 20), command=lambda: self.search_approach())
        self.date_search.grid(row=1, column=3, sticky='nsew', padx=6, pady=6)
        self.approach_results = ctk.CTkScrollableFrame(self.date_frame)
        self.approach_results.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=6, pady=6)
        placeholder2 = ctk.CTkLabel(self.approach_results, font=('Roboto', 20), text='Enter a start date and end date to get approaches.')
        placeholder2.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        # </editor-fold>
        # <editor-fold desc="Start Date">
        self.start_date_frame = ctk.CTkFrame(self.date_frame, height=45, width=275)
        self.start_date_frame.grid(row=1, column=0, sticky='nsew', padx=6, pady=6)
        self.start_date_y = ctk.CTkEntry(self.start_date_frame, placeholder_text='YYYY', font=('Roboto', 20), height=33, width=65)
        self.start_date_y.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        self.start_date_m = ctk.CTkEntry(self.start_date_frame, placeholder_text='MM', font=('Roboto', 20), height=33, width=50)
        self.start_date_m.grid(row=0, column=1, sticky='nsew', padx=6, pady=6)
        self.start_date_d = ctk.CTkEntry(self.start_date_frame, placeholder_text='DD', font=('Roboto', 20), height=33, width=40)
        self.start_date_d.grid(row=0, column=2, sticky='nsew', padx=6, pady=6)
        # </editor-fold>
        # <editor-fold desc="End Date">
        self.end_date_frame = ctk.CTkFrame(self.date_frame, height=45, width=275)
        self.end_date_frame.grid(row=1, column=2, sticky='nsew', padx=6, pady=6)
        self.end_date_y = ctk.CTkEntry(self.end_date_frame, placeholder_text='YYYY', font=('Roboto', 20), height=33, width=65)
        self.end_date_y.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        self.end_date_m = ctk.CTkEntry(self.end_date_frame, placeholder_text='MM', font=('Roboto', 20), height=33, width=50)
        self.end_date_m.grid(row=0, column=1, sticky='nsew', padx=6, pady=6)
        self.end_date_d = ctk.CTkEntry(self.end_date_frame, placeholder_text='DD', font=('Roboto', 20), height=33, width=40)
        self.end_date_d.grid(row=0, column=2, sticky='nsew', padx=6, pady=6)
        # </editor-fold>

    def submit_asteroid(self, id):
        """Whenever the 'go' button is pressed, an asteroid is submitted, and label values change accordingly."""
        # initial asteroid change
        try:
            self.asteroid = Asteroid(id)
            try:
                physical_properties = self.asteroid.physical_properties
                orbital_properties = self.asteroid.orbital_properties
            except AttributeError:
                try:
                    physical_properties = self.asteroid.physical_properties
                    orbital_properties = self.asteroid.orbital_properties
                except AttributeError:
                    physical_properties = self.asteroid.physical_properties
                    orbital_properties = self.asteroid.orbital_properties

            approaches = self.asteroid.close_approach_data
            identifiers = self.asteroid.identifiers
            # physical properties
            for pp, data in physical_properties.items():
                value_str = ""
                if isinstance(data, dict):
                    for pp_unit, pp_value in data.items():
                        if isinstance(pp_value, str):
                            # This means that the value is 'Unavailable.'
                            value_str = 'Unavailable___'
                        else:
                            float_value_str = ""
                            if len(f"{pp_value:,}") >= 7:
                                # This indicates that the value can be converted to scientific notation.
                                float_value_str = f"{round(pp_value, 3):.1e}"
                            else:
                                float_value_str = f"{pp_value:,}"

                            value_str += f"{float_value_str} {pp_unit} / "
                    value_str = value_str[:-3]
                else:
                    # This means that the value is either a string or a float, as opposed to a dictionary.
                    if isinstance(data, str):
                        if data == 'Unavailable':
                            value_str = 'Unavailable'
                        else:
                            value_str = data
                    else:
                        # This means the value is a float.
                        float_value_str = ""
                        if len(f"{data:,}") > 9:
                            # This indicates that the value can be converted to scientific notation.
                            float_value_str = f"{round(data, 2):.1e}"
                        else:
                            float_value_str = f"{data:,}"

                        value_str = float_value_str

                self.pp_labels[pp].configure(text=value_str)

            # orbital properties
            for op, data in orbital_properties.items():
                value_str = ""
                if isinstance(data, dict):
                    for op_unit, op_value in data.items():
                        if isinstance(op_value, str):
                            # This means that the value is 'Unavailable.'
                            value_str = 'Unavailable___'
                        else:
                            float_value_str = ""
                            if len(f"{op_value:,}") > 9:
                                # This indicates that the value can be converted to scientific notation.
                                float_value_str = f"{round(op_value, 2):.1e}"
                            else:
                                float_value_str = f"{op_value:,}"

                            value_str += f"{float_value_str} {op_unit} / "
                    value_str = value_str[:-3]
                else:
                    # This means that the value is either a string or a float, as opposed to a dictionary.
                    if isinstance(data, str):
                        if data == 'Unavailable':
                            value_str = 'Unavailable'
                        else:
                            value_str = data
                    else:
                        # This means the value is a float.
                        float_value_str = ""
                        if len(f"{data:,}") > 9:
                            # This indicates that the value can be converted to scientific notation.
                            float_value_str = f"{round(data, 2):.1e}"
                        else:
                            float_value_str = f"{data:,}"
                            value_str = float_value_str
                self.op_labels[op].configure(text=value_str)
            # approaches
            for widget in self.approaches_frame.winfo_children():  # Start by removing all old approach data.
                widget.destroy()
            if approaches is not None:
                """
                YYYY-MM-DD HH:MM
                Relative Velocity: ...
                Distance: ...
                """
                counter = 0
                for date, data in approaches.items():
                    distance = data['distance']
                    velocity = data['velocity']
                    for unit, dist in distance.items():
                        if len(f'{dist:,}') >= 7:
                            distance[unit] = f'{float(dist):.1e}'
                        else:
                            distance[unit] = f'{float(dist):,}'
                    for unit, vel in velocity.items():
                        if len(f'{vel:,}') >= 7:
                            velocity[unit] = f'{float(vel):.1e}'
                        else:
                            velocity[unit] = f'{float(vel):.1e}'

                    dist_str = f"{distance['au']} au / {distance['km']} km / {distance['mi']} mi"  # Create a string for the approach distance.
                    vel_str = f"{velocity['km/s']} km/s / {velocity['mi/s']} mi/s"  # Create a string for the approach velocity.
                    ctk.CTkLabel(self.approaches_frame, font=('Roboto', 25), text=date).grid(row=counter, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approaches_frame, font=('Roboto', 20), text=dist_str).grid(row=counter+1, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approaches_frame, font=('Roboto', 20), text=vel_str).grid(row=counter+2, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approaches_frame, font=('Roboto', 25), text="---------------------------------------------------------------------------------").grid(
                        row=counter + 3, column=0, sticky='nsw')
                    counter += 4
                self.approaches_frame.winfo_children()[-1].destroy()  # Remove the last seperator
            else:
                ctk.CTkLabel(self.approaches_frame, font=('Roboto', 20), text='No close approaches found.').grid(row=0, column=0, sticky='nsw')
            # name labels
            self.asteroid_name.configure(text=identifiers['full name'])
            self.identifier_labels['IAU'].configure(text='IAU: ' + identifiers['IAU'])
            self.identifier_labels['SPKID'].configure(text='SPK-ID: ' + identifiers['SPKID'])
        except AttributeError:
            self.asteroid_name.configure(text=f'Invalid asteroid identifier: {id}')
    def search_approach(self):
        """Searches for close approaches of asteroids between two dates."""
        for widget in self.approach_results.winfo_children():
            widget.destroy()
        start_date_str = f"{self.start_date_y.get()}-{self.start_date_m.get()}-{self.start_date_d.get()}".replace('-1-', '-01-').replace(
            '-2-', '-02-').replace('-3-', '-03-').replace('-4-', '-04-').replace(
            '-5-', '-05-').replace('-6-', '-06-').replace('-7-', '-07-').replace(
            '-8-', '-08-').replace('-9-', '-09-')
        end_date_str = f"{self.end_date_y.get()}-{self.end_date_m.get()}-{self.end_date_d.get()}".replace('-1-', '-01-').replace(
            '-2-', '-02-').replace('-3-', '-03-').replace('-4-', '-04-').replace(
            '-5-', '-05-').replace('-6-', '-06-').replace('-7-', '-07-').replace(
            '-8-', '-08-').replace('-9-', '-09-')
        try:
            approaches = search_by_date(start_date=start_date_str, end_date=end_date_str)
            if approaches is not None:
                """
                Designation: YYYY-MM-DD HH:MM
                Relative Velocity: ...
                Distance: ...
                """
                counter = 0
                for date, data in approaches.items():
                    distance = data['distance']
                    velocity = data['velocity']
                    for unit, dist in distance.items():
                        if len(f'{dist:,}') >= 7:
                            distance[unit] = f'{float(dist):.1e}'
                        else:
                            distance[unit] = f'{float(dist):,}'
                    for unit, vel in velocity.items():
                        if len(f'{vel:,}') >= 7:
                            velocity[unit] = f'{float(vel):.1e}'
                        else:
                            velocity[unit] = f'{float(vel):.1e}'

                    dist_str = f"{distance['au']} au / {distance['km']} km / {distance['mi']} mi"  # Create a string for the approach distance.
                    vel_str = f"{velocity['km/s']} km/s / {velocity['mi/s']} mi/s"  # Create a string for the approach velocity.
                    ctk.CTkLabel(self.approach_results, font=('Roboto', 25), text=f'{data["designation"]} - {date}').grid(row=counter, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approach_results, font=('Roboto', 20), text=dist_str).grid(row=counter + 1, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approach_results, font=('Roboto', 20), text=vel_str).grid(row=counter + 2, column=0, sticky='nsw')
                    ctk.CTkLabel(self.approach_results, font=('Roboto', 25), text="---------------------------------------------------------------------------------").grid(
                        row=counter + 3, column=0, sticky='nsw')
                    counter += 4
                self.approach_results.winfo_children()[-1].destroy()  # Remove the last seperator
            else:
                ctk.CTkLabel(self.approach_results, font=('Roboto', 20), text='No close approaches found within the date range.').grid(row=0, column=0, sticky='nsw')
        except ConnectionError:
            ctk.CTkLabel(self.approach_results, font=('Roboto', 20), text=f'Invalid date range given: {start_date_str} - {end_date_str}').grid(row=0, column=0, sticky='nsw')
if __name__ == '__main__':
    main = AStROINFO()
    main.mainloop()
