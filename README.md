# ASTROINFO

<p>
ASTROINFO is a program built to convey information 
on asteroids and other smallbodies. It sources data from 
NASA's Smallbody Database, NeoWs API, and CAD API to get
information on properties, orbital info, and approach dates.
</p>
<h2>
ASTROINFO.py
</h2>
<p>
The main file, ASTROINFO.py, uses customtkinter as a geometry manager, 
which gives it a modern feel. How it works is that whenever you enter an
asteroid ID and press the GO button, the asteroid ID is put in as an argument
for an Asteroid class in the classes.py file. If the asteroid is a Near Earth Object
(it comes close to Earth often), then it is moved to the NearEarthObject class.
The classes have properties that contain info on their physical properties,
orbital properties, identifiers, and close approaches.
</p>

<h2>
AOS.py
</h2>
<p>
AOS (ASTROINFO Orbital Simulation) is an orbital simulation made using customtkinter.
It uses a matplotlib graph as a surface for the planets to be displayed in a 2D manner.
You can control the simulation by stepping forward a certain amount of hours (set by the user
at the bottom) OR you can skip to a certain date (at the top). You can add small body objects
using the large text box in the middle. To add Apophis, for example, you can type in 99942 and
click "ADD OBJECTS" to add it.
</p>
<h2>
classes.py
</h2>
<p>
The classes file is the backbone of the program. It contains the two classes that are used for 
getting information on the asteroids that the user inputs. Whenever an object is made a member
of the Asteroid class, it gets new properties that can be used to get data on the asteroid that
the user put in.
</p>
<h2>
API Keys with NASA
</h2>
This program uses NASA APIs, which means it requires an API key to use. I don't want to leak my
own API key out, so you should get your own. Use the link <a href="https://api.nasa.gov/">here</a>
to go to NASA's website and generate an API key that will be emailed directly to you. After that,
you're going to need to go into the <b>api_key.env</b> file and replace DEMO_KEY with your own API key. 
You don't have to do this process and can just run the code as it is because DEMO_KEY still works as an API key
, but I wouldn't reccomend this because you can only use it 40 times per hour, whereas using an actual
API key you can use it 1,000 times per hour.

## Usage Examples
ASTROINFO could be used for anything related to asteroids. If you want to see just how close an asteroid gets
during a close approach to Earth, you can do that in AOS. If you want to get physical properties, then you could
use ASTROINFO. If you want to make your own custom code, you can use the classes file as long as you follow the rules
associated with the Creative Commons Attribution 4.0 International License. See the link under 'License' for more information.

##  License
This work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

<p>
<b>Current version of ASTROINFO: 1.1.1</b>
</p>
