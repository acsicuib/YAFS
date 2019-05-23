import trackanimation
from trackanimation.animation import AnimationTrack
import numpy as np
# Simple example

from trackanimation.tracking import DFTrack
from trackanimation.utils import TrackException
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

import smopy
import matplotlib as mpl
from itertools import izip_longest as zip_longest
from tqdm import tqdm
import scipy
#runfile('/Users/isaaclera/PycharmProjects/YAFS/src/examples/mobileTutorial/testAnimationVoroni.py', wdir='/Users/isaaclera/PycharmProjects/YAFS/src/')

# Coloring tracks by their speed
#input_directory = "exp/example-routes/ibiza.csv"
input_directory = "examples/mobileTutorial/exp/example-routes/ibiza.csv"
ibiza_trk = trackanimation.read_track(input_directory)
ibiza_trk = ibiza_trk.time_video_normalize(time=10, framerate=5)
ibiza_trk = ibiza_trk.set_colors('Speed', individual_tracks=True)

df = ibiza_trk.df
tt = df[df.VideoFrame==10]
tt.columns

coordinates = {}
for row in tt.iterrows():
    code = row[1]["CodeRoute"]
    lat = row[1]["Latitude"]
    lng = row[1]["Longitude"]
    coordinates[code]=[lat,lng]    
    
points = ibiza_trk.df.to_dict()

for point, next_point in zip_longest(tqdm(points, desc='Video generation process'), points[1:], fillvalue=None):
    track_code = str(point['CodeRoute']) + "_" + str(point['Axes'])
    print track_code


fixed_points_or = np.array([[38.914409,1.291472],[39.010489,1.359833],[38.952876,1.427421],[39.001689,1.517648],[39.076888,1.503921]])
mobile_code_points = ["6197472"] #coderoute

mobile_points = [[38.914409,1.291472],[39.010489,1.359833]]
#mobile_points = [[38.914409,1.291472]]





 
fixed_points = dict(zip([10,11,12,13,14],fixed_points_or))
mobile_points= dict(zip([2909,2345],mobile_points))

result ={}
for k in mobile_points:
    point = mobile_points[k]
    print point
    idx = np.argmin(np.sum((np.array(fixed_points.values()) - point) ** 2, axis=1))
    print idx
    result[k]=list(fixed_points)[idx]
    
print result
   

#fig = AnimationTrack(df_points=ibiza_trk, dpi=250, bg_map=True, map_transparency=0.5,voronoi_points=fixed_points,mobile_code_points=mobile_code_points)
#fig.make_video(output_file='coloring-map-by-sVor', framerate=10, linewidth=1.0)


