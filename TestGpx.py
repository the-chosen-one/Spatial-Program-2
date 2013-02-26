import sys
sys.path.append('./gpxpy/')
import gpxpy
import gpxpy.gpx

# Parsing an existing file:
# -------------------------


# // GeoJSON LineString
# {
#     "type": "LineString",
#     "coordinates": [
#         [-80.661983228058659, 35.042968081213758],
#         [-80.662076494242413, 35.042749414542243],
#         [-80.662196794397431, 35.042626481357232],
#         [-80.664238981504525, 35.041175532632963]
#     ]
# }

def StartJson():
	string = 'PolyLines=[\n'
	return string
def StartLineString():
	string = '    {\n'
	string +='        "type": "LineString",\n'
	string +='        "coordinates": [\n'
	return string
def EndLineString():
	string = '        ]\n'
	string +='    }\n'
	return string
def EndJson():
	string =']\n'
	return string

gpx_file = open('sample.gpx', 'r')
json_file = open('sample.json','w')

json_file.write(StartJson())

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
    	json_file.write(StartLineString())
    	length = len(segment.points)
        for point in segment.points:
            #print '{0},{1},{2},{3}'.format(point.latitude, point.longitude, point.speed, point.time)
            #json_file.write('{0},{1},{2},{3}'.format(point.latitude, point.longitude, point.speed, point.time))
            json_file.write('		[{1},{0}]'.format(point.latitude, point.longitude))
            length -= 1
            if length >= 1:
            	json_file.write(',\n')
            else:
            	json_file.write('\n')
            	json_file.write(EndLineString())


json_file.write(EndJson())
json_file.close()

