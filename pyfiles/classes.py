import math
from datetime import datetime, timedelta
from os import getenv

import requests
from astroquery.jplsbdb import SBDB
from dotenv import load_dotenv

# CURRENT VERSION: 1.0 RELEASE

"""
Future plans:
- v 1.0.1: Link AOS to ASTROINFO
"""


class Asteroid:
    def __new__(cls, identifier):
        """Detects if the asteroid is a NEO and changes the class to NearEarthObject if it is."""
        instance = super().__new__(cls)
        try:
            instance.SBDB = SBDB.query(identifier, phys=True)  # Main data source
            instance.IAU = instance.SBDB['object']['des']
            spkid = instance.SBDB['object']['spkid']
            try:
                if int(spkid) - int(instance.IAU) == 20_000_000:  # This means the SPK-ID is represented inaccurately.
                    spkid = str(int(instance.IAU) + 2_000_000)
            except ValueError:
                pass

            if int(spkid) > 3_000_000:  # Temporary-designated asteroids follow different SPKID patterns
                instance.SPKID = spkid
            else:
                instance.SPKID = str(int(instance.IAU) + 2_000_000)  # Adjust SPKID

            if instance.SBDB['object']['neo']:
                load_dotenv('api_key.env')
                url = f"https://api.nasa.gov/neo/rest/v1/neo/{instance.SPKID}?api_key{getenv('api_key')}"
                print(getenv('api_key'))
                main_response = requests.get(url)
                if main_response.status_code == 200:
                    instance.NEOWS = main_response.json()  # Define the NEOWS database before moving to the next class
                    instance.__class__ = NearEarthObject  # Change the class dynamically
            return instance
        except ValueError:
            pass
        except (KeyError, AttributeError):
            pass
        except Exception as e:
            pass

    def __init__(self, identifier):
        """Represents any asteroid. If it is a NEO, move it to the NearEarthObject class."""
        pass

    @property
    def physical_properties(self):
        """Retrieves the asteroid's physical properties. The only possible source is JPL's SBDB database."""
        try:
            rotational_period = {'hrs': round(self.SBDB['phys_par']['rot_per'].value, 3)}
        except KeyError:
            rotational_period = 'Unavailable'
        except AttributeError:
            try:
                rotational_period = {'hrs': round(self.SBDB['phys_par']['rot_per'], 3)}
            except KeyError:
                rotational_period = 'Unavailable'

        # albedo
        try:
            albedo = float(self.SBDB['phys_par']['albedo'].value)
        except KeyError:
            albedo = 'Unavailable'
        except AttributeError:
            try:
                albedo = float(self.SBDB['phys_par']['albedo'])
            except KeyError:
                albedo = 'Unavailable'

        # spectral type (can be estimated with albedo)
        try:
            spectral_type = self.SBDB['phys_par']['spec_B']
        except KeyError:
            try:
                spectral_type = self.SBDB['phys_par']['spec_T']
            except KeyError:
                if albedo != 'Unavailable':
                    if albedo < 0.1:
                        spectral_type = 'C'
                    elif 0.1 < albedo < 0.2:
                        spectral_type = "M"
                    elif 0.2 < albedo:
                        spectral_type = "S"
                else:
                    spectral_type = 'Unavailable'

        # absolute magnitude
        try:
            absolute_magnitude = round(self.SBDB['phys_par']['H'], 3)
        except KeyError:
            absolute_magnitude = 'Unavailable'
        except AttributeError:
            try:
                absolute_magnitude = round(self.SBDB['phys_par']['H'].value, 3)
            except KeyError:
                absolute_magnitude = 'Unavailable'

        # diameter (can be estimated with albedo and absolute magnitude)
        try:
            diameter_km = self.SBDB['phys_par']['diameter'].value
            diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                        'mi': round(diameter_km * 0.62137119, 3)}
        except KeyError:
            if albedo != 'Unavailable' and absolute_magnitude != 'Unavailable':
                diameter_km = (1.329 * (10 ** 6) * (albedo ** -1 / 2) * (10 ** (-0.2 * absolute_magnitude))) / 1000
                diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                            'mi': round(diameter_km * 0.62137119, 3)}
            else:
                diameter_km = 'Unavailable'
                diameter = {'km': 'Unavailable', 'm': 'Unavailable', 'mi': 'Unavailable'}
        except AttributeError:
            try:
                diameter_km = float(self.SBDB['phys_par']['diameter'])
                diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                            'mi': round(diameter_km * 0.62137119, 3)}
            except KeyError:
                if albedo != 'Unavailable' and absolute_magnitude != 'Unavailable':
                    diameter_km = (1.329 * (10 ** 6) * (albedo ** -1 / 2) * (10 ** (-0.2 * absolute_magnitude))) / 1000
                    diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                                'mi': round(diameter_km * 0.62137119, 3)}
                else:
                    diameter_km = 'Unavailable'
                    diameter = {'km': 'Unavailable', 'm': 'Unavailable', 'mi': 'Unavailable'}

        # density (can be estimated with spectral type)
        try:
            density_g = float(self.SBDB['phys_par']['density'].value)
            density = {'g/cm^3': density_g,
                       'kg/m^3': density_g / 1000}
        except KeyError:
            if spectral_type != 'Unavailable':
                if spectral_type == 'C':
                    density = {'g/cm^3': 1.7, 'kg/m^3': 0.0017}
                elif spectral_type == 'M':
                    density = {'g/cm^3': 5.32, 'kg/m^3': 0.00532}
                else:
                    density = {'g/cm^3': 6.71, 'kg/m^3': 0.00671}
            else:
                density = {'g/cm^3': 'Unavailable', 'kg/m^3': 'Unavailable'}
        except AttributeError:
            try:
                density_g = float(self.SBDB['phys_par']['density'])
                density = {'g/cm^3': density_g,
                           'kg/m^3': density_g / 1000}
            except KeyError:
                if spectral_type != 'Unavailable':
                    if spectral_type == 'C':
                        density = {'g/cm^3': 1.7, 'kg/m^3': 0.0017}
                    elif spectral_type == 'M':
                        density = {'g/cm^3': 5.32, 'kg/m^3': 0.00532}
                    else:
                        density = {'g/cm^3': 6.71, 'kg/m^3': 0.00671}
                else:
                    density = {'g/cm^3': 'Unavailable', 'kg/m^3': 'Unavailable'}

        # mass
        if density['kg/m^3'] != 'Unavailable' and diameter_km != 'Unavailable':
            radius = diameter_km * 2000
            volume = (4 / 3 * math.pi) * (radius ** 3) / 1000
            mass = {'kg': round(radius * volume, 3),
                    'g': round(radius * volume * 1000, 3)}
        else:
            mass = {'kg': 'Unavailable', 'g': 'Unavailable'}

        # surface gravity
        if mass['kg'] != 'Unavailable' and diameter_km != 'Unavailable':
            surface_gravity = {'m/s^2': round(6.67430e-11 * (float(mass['kg']) / (diameter_km * 500) ** 2), 3)}
        else:
            surface_gravity = 'Unavailable'

        # escape velocity
        if mass['kg'] != 'Unavailable' and diameter_km != 'Unavailable':
            radius = diameter_km * 500
            escape_vel_km = round(math.sqrt(2 * 6.67430e-11 * float(mass['kg']) / radius), 3)
            escape_velocity = {'m/s': escape_vel_km * 1000, 'km/s': escape_vel_km,
                               'mi/s': round(escape_vel_km * 0.62137119, 3)}
        else:
            escape_velocity = 'Unavailable'

        # volume
        if diameter_km != 'Unavailable':
            radius = diameter_km * 500
            volume_m = (4 / 3 * math.pi) * (radius ** 3)
            volume = {'m^3': round(volume_m, 3), 'km^3': round(volume_m / 1_000_000, 3)}
        else:
            volume = 'Unavailable'

        # return statement
        return {'rotational period': rotational_period, 'spectral type': spectral_type, 'absolute magnitude':
            absolute_magnitude, 'diameter': diameter, 'density': density, 'surface gravity': surface_gravity,
                'escape velocity': escape_velocity, 'mass': mass, 'albedo': albedo, 'volume': volume}

    @property
    def orbital_properties(self):
        """Gets the orbital properties of the asteroid."""
        # Note: Some orbital properties have multiple keys that can be used.
        try:
            perihelion_distance_AU = self.SBDB['orbit']['elements']['q'].value
        except KeyError:
            perihelion_distance_AU = 'Unavailable'
        except AttributeError:
            try:
                perihelion_distance_AU = self.SBDB['orbit']['elements']['q']
            except KeyError:
                perihelion_distance_AU = 'Unavailable'

        if perihelion_distance_AU != 'Unavailable':
            perihelion_distance_km = perihelion_distance_AU * 149597871
            perihelion_distance_mi = perihelion_distance_km * 0.62137119
            perihelion_distance = {'AU': round(perihelion_distance_AU, 3), 'mi': round(perihelion_distance_mi, 3),
                                   'km': round(perihelion_distance_km, 3)}
        else:
            perihelion_distance = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # aphelion distance
        try:
            aphelion_distance_AU = self.SBDB['orbit']['elements']['Q'].value
        except KeyError:
            try:
                aphelion_distance_AU = self.SBDB['orbit']['elements']['ad'].value
            except KeyError:
                aphelion_distance_AU = 'Unavailable'
        except AttributeError:
            try:
                aphelion_distance_AU = float(self.SBDB['orbit']['elements']['Q'])
            except KeyError:
                try:
                    aphelion_distance_AU = self.SBDB['orbit']['elements']['ad'].value
                except KeyError:
                    aphelion_distance_AU = 'Unavailable'
                except AttributeError:
                    try:
                        aphelion_distance_AU = float(self.SBDB['orbit']['elements']['ad'])
                    except KeyError:
                        aphelion_distance_AU = 'Unavailable'
        if aphelion_distance_AU != 'Unavailable':
            aphelion_distance_km = aphelion_distance_AU * 149597871
            aphelion_distance_mi = aphelion_distance_km * 0.62137119
            aphelion_distance = {'AU': round(aphelion_distance_AU, 3), 'mi': round(aphelion_distance_mi, 3),
                                 'km': round(aphelion_distance_km, 3)}
        else:
            aphelion_distance = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # semi-major axis (can be estimated with perihelion and aphelion distance)
        try:
            semi_major_axis_AU = float(self.SBDB['orbit']['elements']['a'].value)
        except KeyError:
            if perihelion_distance_AU != 'Unavailable' and aphelion_distance_AU != 'Unavailable':
                semi_major_axis_AU = (perihelion_distance_AU + aphelion_distance_AU) / 2
            else:
                semi_major_axis_AU = 'Unavailable'
        except AttributeError:
            try:
                semi_major_axis_AU = float(self.SBDB['orbit']['elements']['a'])
            except KeyError:
                if perihelion_distance_AU != 'Unavailable' and aphelion_distance_AU != 'Unavailable':
                    semi_major_axis_AU = (perihelion_distance_AU + aphelion_distance_AU) / 2
                else:
                    semi_major_axis_AU = 'Unavailable'

        if semi_major_axis_AU != 'Unavailable':
            semi_major_axis_km = semi_major_axis_AU * 149597871
            semi_major_axis_mi = semi_major_axis_km * 0.62137119
            semi_major_axis = {'AU': round(semi_major_axis_AU, 3), 'mi': round(semi_major_axis_mi, 3),
                               'km': round(semi_major_axis_km, 3)}
        else:
            semi_major_axis = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # eccentricity
        try:
            eccentricity = round(float(self.SBDB['orbit']['elements']['e']), 3)
        except KeyError:
            eccentricity = 'Unavailable'
        except AttributeError:
            try:
                eccentricity = round(float(self.SBDB['orbit']['elements']['e'].value), 3)
            except KeyError:
                eccentricity = 'Unavailable'

        # mean anomaly
        try:
            mean_anomaly_deg = float(self.SBDB['orbit']['elements']['M'].value)
        except KeyError:
            try:
                mean_anomaly_deg = float(self.SBDB['orbit']['elements']['ma'].value)
            except KeyError:
                mean_anomaly_deg = 'Unavailable'
            except AttributeError:
                try:
                    mean_anomaly_deg = float(self.SBDB['orbit']['elements']['ma'])
                except KeyError:
                    mean_anomaly_deg = 'Unavailable'
        except AttributeError:
            try:
                mean_anomaly_deg = float(self.SBDB['orbit']['elements']['M'])
            except KeyError:
                try:
                    mean_anomaly_deg = float(self.SBDB['orbit']['elements']['ma'].value)
                except KeyError:
                    mean_anomaly_deg = 'Unavailable'
                except AttributeError:
                    try:
                        mean_anomaly_deg = float(self.SBDB['orbit']['elements']['ma'])
                    except KeyError:
                        mean_anomaly_deg = 'Unavailable'

        if mean_anomaly_deg != 'Unavailable':
            mean_anomaly_rad = math.radians(mean_anomaly_deg)
            mean_anomaly = {'deg': round(mean_anomaly_deg, 3), 'rad': round(mean_anomaly_rad, 3)}
        else:
            mean_anomaly = {'deg': 'Unavailable', 'rad': 'Unavailable'}

        # orbital period
        try:
            orbital_period_days = float(self.SBDB['orbit']['elements']['period'].value)
        except KeyError:
            try:
                orbital_period_days = float(self.SBDB['orbit']['elements']['per'].value)
            except KeyError:
                orbital_period_days = 'Unavailable'
            except AttributeError:
                try:
                    orbital_period_days = float(self.SBDB['orbit']['elements']['per'])
                except KeyError:
                    orbital_period_days = 'Unavailable'
        except AttributeError:
            try:
                orbital_period_days = float(self.SBDB['orbit']['elements']['period'])
            except KeyError:
                try:
                    orbital_period_days = float(self.SBDB['orbit']['elements']['per'].value)
                except KeyError:
                    orbital_period_days = 'Unavailable'
                except AttributeError:
                    try:
                        orbital_period_days = float(self.SBDB['orbit']['elements']['per'])
                    except KeyError:
                        orbital_period_days = 'Unavailable'

        if orbital_period_days != 'Unavailable':
            orbital_period_hours = orbital_period_days * 24
            orbital_period = {'hrs': round(orbital_period_hours, 3), 'days': round(orbital_period_days, 3)}
        else:
            orbital_period = {'hrs': 'Unavailable', 'days': 'Unavailable'}

        # orbit class
        try:
            orbit_class = self.SBDB['object']['orbit_class']['name']
            if orbit_class == 'Aten':
                orbit_class = 'Near Earth Object'
        except KeyError:
            orbit_class = 'Unavailable'

        # orbit ID
        try:
            orbit_ID = str(self.SBDB['object']['orbit_id'])
        except KeyError:
            orbit_ID = 'Unavailable'
        except AttributeError:
            try:
                orbit_ID = str(self.SBDB['object']['orbit_id'].value)
            except KeyError:
                orbit_ID = 'Unavailable'

        # return statement
        return {'perihelion distance': perihelion_distance, 'aphelion distance': aphelion_distance,
                'semi-major axis': semi_major_axis, 'eccentricity': eccentricity, 'mean anomaly': mean_anomaly,
                'orbital period': orbital_period, 'orbit class': orbit_class, 'orbit id': orbit_ID}

    @property
    def identifiers(self):
        """Returns the identifiers of the asteroid."""
        return {'full name': self.SBDB['object']['fullname'], 'SPKID': self.SPKID, 'IAU': self.IAU}

    @property
    def close_approach_data(self):
        """Returns close approach data for the asteroid, starting 100 years ago and ending 100 years in the future."""
        base_url = "https://ssd-api.jpl.nasa.gov/cad.api"
        params = {
            "des": self.IAU,
            "date-min": (datetime.today() - timedelta(days=36525)).strftime('%Y-%m-%d'),
            "date-max": (datetime.today() + timedelta(days=36525)).strftime('%Y-%m-%d'),
            "dist-max": 0.5
        }
        approaches = {}
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            try:
                if data['data']:
                    for approach in data['data']:
                        approach_date = datetime.strptime(approach[3], "%Y-%b-%d %H:%M").strftime("%Y-%m-%d %H:%M")
                        dist_au = float(approach[4])
                        dist_km = dist_au * 149597871
                        dist_mi = dist_km * 0.62137119
                        vel_km = float(approach[7])
                        vel_mi = vel_km * 0.62137119
                        approaches[approach_date] = {'distance': {'mi': round(dist_mi, 3), 'km': round(dist_km, 3), 'au': round(dist_au, 3)},
                                                     'velocity': {'km/s': round(vel_km, 3), 'mi/s': round(vel_mi, 3)}}
                    return approaches
                else:
                    return None
            except KeyError:
                return None
        else:
            return None


class NearEarthObject(Asteroid):
    def __init__(self, identifier):
        """Initializes a new database source for any asteroid that is a NEO."""
        super().__init__(identifier)

    @property
    def physical_properties(self):
        """With the added NeoWs capability, there is now a new data source, which is used in case the SBDB info is not available."""
        try:
            rotational_period = {'hrs': round(float(self.SBDB['phys_par']['rot_per'].value), 3)}
        except KeyError:
            rotational_period = 'Unavailable'

        # albedo
        try:
            albedo = float(self.SBDB['phys_par']['albedo'])
        except KeyError:
            albedo = 'Unavailable'

        # spectral type (can be estimated with albedo)
        try:
            spectral_type = self.SBDB['phys_par']['spec_B']
        except KeyError:
            try:
                spectral_type = self.SBDB['phys_par']['spec_T']
            except KeyError:
                if albedo != 'Unavailable':
                    if albedo < 0.1:
                        spectral_type = 'C'
                    elif 0.1 < albedo < 0.2:
                        spectral_type = "M"
                    elif 0.2 < albedo:
                        spectral_type = "S"
                else:
                    spectral_type = 'Unavailable'

        # absolute magnitude
        try:
            absolute_magnitude = round(float(self.SBDB['phys_par']['H']), 3)
        except KeyError:
            try:
                absolute_magnitude = round(float(self.NEOWS['absolute_magnitude_h']), 3)
            except KeyError:
                absolute_magnitude = 'Unavailable'

        # diameter (can be estimated with albedo and absolute magnitude)
        try:
            diameter_km = float(self.SBDB['phys_par']['diameter'].value)
            diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                        'mi': round(diameter_km * 0.62137119, 3)}
        except KeyError:
            try:
                diameter_km = float(self.NEOWS['estimated_diameter']['kilometers']['estimated_diameter_min'])
                diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                            'mi': round(diameter_km * 0.62137119, 3)}
            except KeyError:
                if albedo != 'Unavailable' and absolute_magnitude != 'Unavailable':
                    diameter_km = (1.329 * (10 ** 6) * (albedo ** -1 / 2) * (10 ** (-0.2 * absolute_magnitude))) / 1000
                    diameter = {'km': round(diameter_km, 3), 'm': round(diameter_km * 1000, 3),
                                'mi': round(diameter_km * 0.62137119, 3)}
                else:
                    diameter_km = 'Unavailable'
                    diameter = {'km': 'Unavailable', 'm': 'Unavailable', 'mi': 'Unavailable'}

        # density (can be estimated with spectral type)
        try:
            density_g = float(self.SBDB['phys_par']['density'].value)
            density = {'g/cm^3': density_g,
                       'kg/m^3': density_g / 1000}
        except KeyError:
            if spectral_type != 'Unavailable':
                if spectral_type == 'C':
                    density = {'g/cm^3': 1.7, 'kg/m^3': 0.0017}
                elif spectral_type == 'M':
                    density = {'g/cm^3': 5.32, 'kg/m^3': 0.00532}
                else:
                    density = {'g/cm^3': 6.71, 'kg/m^3': 0.00671}
            else:
                density = {'g/cm^3': 'Unavailable', 'kg/m^3': 'Unavailable'}

        # mass
        if density['kg/m^3'] and diameter_km != 'Unavailable':
            radius = diameter_km * 2000
            volume = (4 / 3 * math.pi) * (radius ** 3) / 1000
            mass = {'kg': round(radius * volume, 3),
                    'g': round(radius * volume * 1000, 3)}
        else:
            mass = {'kg': 'Unavailable', 'g': 'Unavailable'}

        # surface gravity
        if mass['kg'] != 'Unavailable' and diameter_km != 'Unavailable':
            surface_gravity = {'m/s^2': round(6.67430e-11 * (float(mass['kg']) / (diameter_km * 500) ** 2), 3)}
        else:
            surface_gravity = 'Unavailable'

        # escape velocity
        if mass['kg'] != 'Unavailable' and diameter_km != 'Unavailable':
            radius = diameter_km * 500
            escape_vel_km = round(math.sqrt(2 * 6.67430e-11 * float(mass['kg']) / radius), 3)
            escape_velocity = {'m/s': escape_vel_km * 1000, 'km/s': escape_vel_km,
                               'mi/s': round(escape_vel_km * 0.62137119, 3)}
        else:
            escape_velocity = 'Unavailable'

        # volume
        if diameter_km != 'Unavailable':
            radius = diameter_km * 500
            volume_m = (4 / 3 * math.pi) * (radius ** 3)
            volume = {'m^3': round(volume_m, 3), 'km^3': round(volume_m / 1_000_000, 3)}
        else:
            volume = 'Unavailable'

        # return statement
        return {'rotational period': rotational_period, 'spectral type': spectral_type, 'absolute magnitude':
            absolute_magnitude, 'diameter': diameter, 'density': density, 'surface gravity': surface_gravity,
                'escape velocity': escape_velocity, 'mass': mass, 'albedo': albedo, 'volume': volume}

    @property
    def orbital_properties(self):
        try:
            perihelion_distance_AU = float(self.SBDB['orbit']['elements']['q'].value)
        except KeyError:
            try:
                perihelion_distance_AU = float(self.NEOWS['orbital_data']['perihelion_distance'])
            except KeyError:
                perihelion_distance_AU = 'Unavailable'

        if perihelion_distance_AU != 'Unavailable':
            perihelion_distance_km = perihelion_distance_AU * 149597871
            perihelion_distance_mi = perihelion_distance_km * 0.62137119
            perihelion_distance = {'AU': round(perihelion_distance_AU, 3), 'mi': round(perihelion_distance_mi, 3),
                                   'km': round(perihelion_distance_km, 3)}
        else:
            perihelion_distance = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # aphelion distance
        try:
            aphelion_distance_AU = float(self.SBDB['orbit']['elements']['Q'].value)
        except KeyError:
            try:
                aphelion_distance_AU = float(self.SBDB['orbit']['elements']['ad'].value)
            except KeyError:
                try:
                    aphelion_distance_AU = float(self.NEOWS['orbital_data']['aphelion_distance'])
                except KeyError:
                    aphelion_distance_AU = 'Unavailable'

        if aphelion_distance_AU != 'Unavailable':
            aphelion_distance_km = aphelion_distance_AU * 149597871
            aphelion_distance_mi = aphelion_distance_km * 0.62137119
            aphelion_distance = {'AU': round(aphelion_distance_AU, 3), 'mi': round(aphelion_distance_mi, 3),
                                 'km': round(aphelion_distance_km, 3)}
        else:
            aphelion_distance = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # semi-major axis (can be estimated with perihelion and aphelion distance)
        try:
            semi_major_axis_AU = float(self.SBDB['orbit']['elements']['a'].value)
        except KeyError:
            try:
                semi_major_axis_AU = float(self.SBDB['orbit']['elements']['ad'].value)
            except KeyError:
                try:
                    semi_major_axis_AU = float(self.NEOWS['orbital_data']['semi_major_axis'])
                except KeyError:
                    if perihelion_distance_AU and aphelion_distance_AU != 'Unavailable':
                        semi_major_axis_AU = (perihelion_distance_AU + aphelion_distance_AU) / 2
                    else:
                        semi_major_axis_AU = 'Unavailable'

        if semi_major_axis_AU != 'Unavailable':
            semi_major_axis_km = semi_major_axis_AU * 149597871
            semi_major_axis_mi = semi_major_axis_km * 0.62137119
            semi_major_axis = {'AU': round(semi_major_axis_AU, 3), 'mi': round(semi_major_axis_mi, 3),
                               'km': round(semi_major_axis_km, 3)}
        else:
            semi_major_axis = {'AU': 'Unavailable', 'mi': 'Unavailable', 'km': 'Unavailable'}

        # eccentricity
        try:
            eccentricity = round(float(self.SBDB['orbit']['elements']['e']), 3)
        except KeyError:
            try:
                eccentricity = round(float(self.NEOWS['orbital_data']['eccentricity']), 3)
            except KeyError:
                eccentricity = 'Unavailable'

        # mean anomaly
        try:
            mean_anomaly_deg = float(self.SBDB['orbit']['elements']['M'].value)
        except KeyError:
            try:
                mean_anomaly_deg = float(self.SBDB['orbit']['elements']['ma'].value)
            except KeyError:
                try:
                    mean_anomaly_deg = float(self.NEOWS['orbital_data']['mean_anomaly'])
                except KeyError:
                    mean_anomaly_deg = 'Unavailable'

        if mean_anomaly_deg != 'Unavailable':
            mean_anomaly_rad = math.radians(mean_anomaly_deg)
            mean_anomaly = {'deg': round(mean_anomaly_deg, 3), 'rad': round(mean_anomaly_rad, 3)}
        else:
            mean_anomaly = {'deg': 'Unavailable', 'rad': 'Unavailable'}

        # orbital period
        try:
            orbital_period_days = float(self.SBDB['orbit']['elements']['period'].value)
        except KeyError:
            try:
                orbital_period_days = float(self.SBDB['orbit']['elements']['per'].value)
            except KeyError:
                try:
                    orbital_period_days = float(self.NEOWS['orbital_data']['orbital_period'])
                except KeyError:
                    orbital_period_days = 'Unavailable'

        if orbital_period_days != 'Unavailable':
            orbital_period_hours = orbital_period_days * 24
            orbital_period = {'hrs': round(orbital_period_hours, 3), 'days': round(orbital_period_days, 3)}
        else:
            orbital_period = {'hrs': 'Unavailable', 'days': 'Unavailable'}

        # orbit class
        try:
            orbit_class = self.SBDB['object']['orbit_class']['name']
            if orbit_class == 'Aten':
                orbit_class = 'Near Earth Object'
        except KeyError:
            orbit_class = 'Unavailable'

        try:
            orbit_ID = self.SBDB['object']['orbit_id']
        except KeyError:
            try:
                orbit_ID = self.NEOWS['orbital_data']['orbit_id']
            except KeyError:
                orbit_ID = 'Unavailable'

        # return statement
        return {'perihelion distance': perihelion_distance, 'aphelion distance': aphelion_distance,
                'semi-major axis': semi_major_axis, 'eccentricity': eccentricity, 'mean anomaly': mean_anomaly,
                'orbital period': orbital_period, 'orbit class': orbit_class, 'orbit id': orbit_ID}


def search_by_date(start_date, end_date):
    """
    Searches for asteroids that have a close approach to Earth in a provided date range.
    :param start_date: The start date, in YYYY-MM-DD.
    :param end_date: The end date, in YYYY-MM-DD.
    :return: A dictionary containing IDs and approach info of each asteroid mentioned.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date().strftime("%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date().strftime("%Y-%m-%d")
    timedelta = (datetime.strptime(end_date, "%Y-%m-%d").date() - datetime.strptime(start_date, "%Y-%m-%d").date()).days
    if 60 > timedelta >= 0:
        url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date}&date-max={end_date}&dist-max=0.5"
    elif 90 > timedelta >= 60:
        url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date}&date-max={end_date}&dist-max=0.25"
    elif 120 > timedelta >= 90:
        url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date}&date-max={end_date}&dist-max=0.1"
    elif 200 > timedelta > 120:
        url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date}&date-max={end_date}&dist-max=0.05"
    else:
        url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date}&date-max={end_date}&dist-max=0.025"
    main_response = requests.get(url)
    if main_response.status_code == 200:
        data = main_response.json()
        approaches = dict()
        for approach_data in data['data']:
            approaches[approach_data[3]] = {'designation': approach_data[0], 'distance': {'au': round(float(approach_data[4]), 3), 'km': round(float(approach_data[4]) * 1.460e+8, 3),
                                                                                          'mi': round(float(approach_data[4]) * 9.2956e+07, 3)}, 'velocity': {'km/s': round(float(approach_data[
                                                                                                                                                                                      7]), 3),
                                                                                                                                                              'mi/s': round(
                                                                                                                                                                  float(approach_data[7]) * 0.621371192,
                                                                                                                                                                  3)}}
        return approaches
    else:
        return None
