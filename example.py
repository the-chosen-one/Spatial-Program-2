import sys
sys.path.append('./gpxpy/')
import gpxpy
import gpxpy.gpx
import pygmaps 
import random

#Configuration settings:
#Stop Threshold
stop_threshold = 1

def htmlcolor(r, g, b):
    def _chkarg(a):
        if isinstance(a, int): # clamp to range 0--255
            if a < 0:
                a = 0
            elif a > 255:
                a = 255
        elif isinstance(a, float): # clamp to range 0.0--1.0 and convert to integer 0--255
            if a < 0.0:
                a = 0
            elif a > 1.0:
                a = 255
            else:
                a = int(round(a*255))
        else:
            raise ValueError('Arguments must be integers or floats.')
        return a
    r = _chkarg(r)
    g = _chkarg(g)
    b = _chkarg(b)
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)

def SatColor(num_sats):
	if num_sats <= 3:
		return '#FF0000'
	elif num_sats <= 6:
		return '#0000FF'
	else:
		return '#00FF00'

	
#mymap.addradpoint(37.429 , -122.145 , 95 , "#FF0000" )
#path = [(37.429, -122.145),(37.428, -122.145),(37.427, -122.145),(37.427, -122.146),(37.427, -122.146)]
#mymap.addpath(path,"#00FF00")



gpx_file = open('sample.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

print gpx.get_bounds()

middle_lat = (gpx.get_bounds()[0]+gpx.get_bounds()[1])/2
middle_lon = (gpx.get_bounds()[2]+gpx.get_bounds()[3])/2

mymap = pygmaps.maps(middle_lat,middle_lon, 8)

mymap.addradpoint(middle_lat , middle_lon , 95 , "#000000" )

stop = False


for track in gpx.tracks:
	for segment in track.segments:
		path = []
		#avg_strength = 0
		for point in segment.points:
			if point.speed < stop_threshold and stop == False:
				stop = True
				#mymap.addradpoint(point.latitude , point.longitude , 50 , "#000000" )				
			else:
				stop = False
				path.append((point.latitude, point.longitude))
				#avg_strength += point.sat
		color = htmlcolor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
		#print color
		#print len(path)
		#avg_strength /= len(path)
		mymap.addpath(path,color)	
mymap.draw('./mymap.html')


