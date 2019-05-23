# -*- coding: utf-8 -*-


# THIS VERSION IS MODIFIED TO ANIMATE THE SIMULATION
# by Isaac Lera and Carlos Guerrero
#
# Copyright 2017 Juan José Martín Miralles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Python modules
import io
import subprocess
import warnings
import networkx as nx
from matplotlib.collections import PatchCollection

try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

# Third party modules
import matplotlib

# matplotlib.use('Agg')
import matplotlib.pyplot as plt  # Attention: include the .use('agg') before importing pyplot: DISPLAY issues
import mplleaflet
import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib as mpl
import copy
import smopy
import matplotlib.patches as patches
import os

# Own modules
from trackanimation.tracking import DFTrack
from trackanimation.utils import TrackException
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from collections import defaultdict



class AnimationTrack:
    def __init__(self, sim, dpi=100, bg_map=True, aspect='equal',map_transparency=0.5):
        # type: (Sim, int, boolean, String, float) -> AnimationTrack

        ## Combining endpoints with mobile
        self.track_code_last_position = {}
        self.connection = defaultdict(int)

        self.fig = plt.figure(figsize=(10, 8), dpi=dpi)
        self.axarr = self.fig.add_subplot(111)

        self.axarr.set_facecolor('0.05')
        self.axarr.tick_params(color='0.05', labelcolor='0.05')
        for spine in self.axarr.spines.values():
            spine.set_edgecolor('white')

        df = sim.user_tracks.get_tracks()
        df.df['Axes'] = 0
        self.track_df = DFTrack()
        self.track_df = self.track_df.concat(df)

        if 'VideoFrame' in self.track_df.df:
            self.track_df = self.track_df.sort(['VideoFrame', 'Axes', 'CodeRoute'])
        else:
            self.track_df = self.track_df.sort(['Axes', 'Date'])

        self.track_df.df = self.track_df.df.reset_index(drop=True)
        self.sim = sim
        self.name_mobile = copy.copy(self.sim.name_endpoints)
        last = len(self.name_mobile)
        for ix, code_mobile in enumerate(self.sim.mobile_fog_entities.keys()):
            self.name_mobile[last+ix] = code_mobile



        self.car_icon = self.getImage(os.path.dirname(__file__)+'/icon/car.png',0.2)
        self.endpoint_icon = self.getImage(os.path.dirname(__file__)+'/icon/endpoint.png',0.2)
        self.car_endpoint_icon= self.getImage(os.path.dirname(__file__)+'/icon/car_endpoint.png',0.2)


    def getImage(self,path, zoom=10):
        return OffsetImage(plt.imread(path), zoom=zoom)

    #TODO update proportions according to the image size
    def update_coverage_regions(self):
        point_mobiles = []

        for ix,code_mobile in enumerate(self.sim.mobile_fog_entities.keys()):
            if code_mobile in self.track_code_last_position.keys():
                (lng, lat) = self.track_code_last_position[code_mobile]
                point_mobiles.append(np.array([lng, lat]))

        point_mobiles = np.array(point_mobiles)

        if len(point_mobiles)==0:
            self.pointsVOR = self.sim.endpoints
        else:
            self.pointsVOR = np.concatenate((self.sim.endpoints, point_mobiles), axis=0)

        self.sim.coverage.update_coverage_of_endpoints(self.sim.map, self.pointsVOR)
        self.axarr.clear()

        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.xlim(0, self.sim.map.w)
        plt.ylim(self.sim.map.h, 0)
        plt.axis('off')
        plt.tight_layout()

        self.axarr.imshow(self.sim.map.img)

        # self.axarr.add_collection(
        #     mpl.collections.PolyCollection(
        #         self.sim.coverage.cells, facecolors=self.sim.coverage.colors_cells,
        #         edgecolors='k', alpha=.25))

        # p = PatchCollection(self.sim.coverage.get_polygon_to_map(),facecolors=self.sim.coverage.get_polygon_colors(),alpha=.25)
        # p.set_array(self.sim.coverage.colors_cells)

        self.axarr.add_collection(self.sim.coverage.get_polygons_on_map())


        # self.ppix = [self.sim.map.to_pixels(vp[0], vp[1]) for vp in self.pointsVOR]
        # self.ppix = np.array(self.ppix)
        # for point in self.ppix:
        #     ab = AnnotationBbox(self.car_icon, (point[0], point[1]),frameon=False)
        #     self.axarr.add_artist(ab)

        # Endpoints of the network
        self.ppix = [self.sim.map.to_pixels(vp[0], vp[1]) for vp in self.sim.endpoints]
        for point in self.ppix:
            ab = AnnotationBbox(self.endpoint_icon, (point[0], point[1]), frameon=False)
            self.axarr.add_artist(ab)

        # self.axarr.scatter(self.ppix[:, 0], self.ppix[:, 1])


    def show_frequency(self,draw_connection_line=False):
        self.axarr.texts = []

        # Draw names
        for ix, vp in enumerate(self.ppix):
            t = plt.text(vp[0] - 3, vp[1] - 8, self.name_mobile[ix], dict(size=6, color='b'))

        # Draw last movement
        for code in self.track_code_last_position:

            (lng, lat) = self.track_code_last_position[code]
            new_point=[lng,lat]

            if code not in self.sim.mobile_fog_entities.keys():
                point_index = self.sim.coverage.connection(new_point)
                self.connection[point_index] += 1
                icon = self.car_icon
            else:
                icon = self.car_endpoint_icon

            lng, lat = self.sim.map.to_pixels(lng, lat)

            plt.annotate(str(code).replace("_0.0",""),
                        xy=(lng, lat),  # theta, radius
                        xytext=(lng-1, lat-5),  # fraction, fraction
                        # arrowprops=dict(facecolor='black', arrowstyle="-|>"),
                        horizontalalignment='center',
                        verticalalignment='bottom', size= 6)

            ab = AnnotationBbox(icon, (lng,lat), frameon=False)
            self.axarr.add_artist(ab)

            # if code not in self.sim.mobile_fog_entities and \
            #         draw_connection_line:
            #     pointA = self.ppix[point_index]
            #     pointB = [lng,lat]
            #
            #     plt.plot([pointA[0], pointB[0]], [pointA[1], pointB[1]], color="gray")

        # draw number of connections by node
        # for k in self.connection:
            # plt.text(20, 20 + (k * 30), "%s : %i" % (self.name_mobile[k], self.connection[k]), dict(size=10, color='black'))


    def clear_frequency(self):
        for val in self.connection:
            self.connection[val] = 0

    def compute_points(self, track_df=None, linewidth=0.5):
        track_points = {}

        if track_df is None:
            points = self.track_df.to_dict()
        else:
            points = track_df.to_dict()

        for point, next_point in zip_longest(tqdm(points, desc='Video generation process'), points[1:], fillvalue=None):
            track_code = str(point['CodeRoute']) + "_" + str(point['Axes'])

            # Check if the track is in the data structure
            if track_code in track_points:
                position = track_points[track_code]

                if len(position['lat']) > 1 and len(position['lng']) > 1:
                    del position['lat'][0]
                    del position['lng'][0]

            else:
                position = {'lat': [], 'lng': []}

            lat = point['Latitude']
            lng = point['Longitude']

            self.track_code_last_position[str(track_code).replace("_0.0","")]=(lat,lng)

            yield point, next_point


    def get_all_points_from_videoframe(self,step, track_df=None, linewidth=0.5):

        df = self.track_df.df
        tt = df[df.VideoFrame == step]

        coordinates = {}
        for row in tt.iterrows():
            code = str(row[1]["CodeRoute"])
            lat = row[1]["Latitude"]
            lng = row[1]["Longitude"]
            coordinates[code] = (lat, lng)

        return coordinates

    def compute_tracks(self, linewidth=0.5):
        df = self.track_df.get_tracks().df

        df['track_code'] = df['CodeRoute'].map(str) + '_' + df['Axes'].map(str)
        grouped = df['track_code'].unique()

        for name in tqdm(grouped, desc='Groups'):
            df_slice = df[df['track_code'] == name]
            lat = df_slice['Latitude'].values
            lng = df_slice['Longitude'].values
            lng, lat = self.sim.map[int(df_slice['Axes'].unique())].to_pixels(lat, lng)
            self.axarr[int(df_slice['Axes'].unique())].plot(lng, lat, color='deepskyblue', lw=linewidth, alpha=1)

    def make_video(self, linewidth=0.5, output_file='video', framerate=5,G=None):
        cmdstring = ('ffmpeg',
                     '-y',
                     '-loglevel', 'quiet',
                     '-framerate', str(framerate),
                     '-f', 'image2pipe',
                     '-i', 'pipe:',
                     '-r', '25',
                     '-s', '1280x960',
                     '-pix_fmt', 'yuv420p',
                     output_file + '.mp4'
                     )

        pipe = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)


        for point, next_point in self.compute_points(linewidth=linewidth):
            if self.is_new_frame(point, next_point):
                self.axarr.texts = []
                self.clear_frequency()
                self.update_coverage_regions()
                self.show_frequency()

                if G != None:
                    pos = nx.spring_layout(G, seed=1)
                    # pos = map_endpoints
                    pos = [[pos[x][0], pos[x][1]] for x in G.nodes()]
                    pos = np.array(pos)
                    pos[:, 0] = (pos[:, 0] - pos[:, 0].min()) / (pos[:, 0].max() - pos[:, 0].min())
                    pos[:, 1] = (pos[:, 1] - pos[:, 1].min()) / (pos[:, 1].max() - pos[:, 1].min())
                    size = self.fig.get_size_inches() * self.fig.dpi * 1.5
                    pos = [self.point_network_map(x, size) for x in pos]
                    pos = dict(zip(G.nodes(), pos))

                    nx.draw(G, pos, with_labels=False, node_size=100, nodelist=self.sim.name_endpoints.values(),
                            node_color="#1260A0", node_shape="o")
                    # rest_nodes = [e for e in G.nodes() if e not in self.sim.name_endpoints.values()]
                    nodes_level_mobile = self.get_nodes_by_level(G, -1)
                    nobes_upper_level = self.get_nodes_by_upper_level(G, 1)
                    nx.draw(G, pos, with_labels=False, node_size=100, nodelist=nodes_level_mobile, node_shape="^",
                            node_color="orange")
                    nx.draw(G, pos, with_labels=True, node_size=100, nodelist=nobes_upper_level, node_shape="s",
                            node_color="red", font_size=8)


                buffer = io.BytesIO()
                canvas = plt.get_current_fig_manager().canvas
                canvas.draw()
                pil_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
                pil_image.save(buffer, 'PNG')
                buffer.seek(0)
                pipe.stdin.write(buffer.read())

        pipe.stdin.close()


    def make_snap(self, step, output_file="None",draw_connection_line=False,G=None):
        self.track_code_last_position = self.get_all_points_from_videoframe(step)

        self.axarr.texts = []
        self.clear_frequency()
        self.update_coverage_regions()
        self.show_frequency(draw_connection_line=draw_connection_line)

        # showing the STEP in the upper left corner of the figure
        size = self.fig.get_size_inches() * self.fig.dpi
        plt.text(size[0]*0.02, size[1]*0.05,"Step: %i"%step, dict(size=10, color='b'))

        # showing the GRAPH
        if G !=None:
            pos = nx.spring_layout(G,seed=1)
            # pos = map_endpoints
            pos = [[pos[x][0], pos[x][1]] for x in G.nodes()]
            pos = np.array(pos)
            pos[:, 0] = (pos[:, 0] - pos[:, 0].min()) / (pos[:, 0].max() - pos[:, 0].min())
            pos[:, 1] = (pos[:, 1] - pos[:, 1].min()) / (pos[:, 1].max() - pos[:, 1].min())
            size = self.fig.get_size_inches() * self.fig.dpi * 1.5
            pos = [self.point_network_map(x, size) for x in pos]
            pos = dict(zip(G.nodes(),pos))

            nx.draw(G, pos,with_labels=False,node_size=100,nodelist=self.sim.name_endpoints.values(),node_color="#1260A0",node_shape="o")
            # rest_nodes = [e for e in G.nodes() if e not in self.sim.name_endpoints.values()]
            nodes_level_mobile = self.get_nodes_by_level(G,-1)
            nobes_upper_level = self.get_nodes_by_upper_level(G,1)
            nx.draw(G, pos,with_labels=False,node_size=100,nodelist=nodes_level_mobile,node_shape="^",node_color="orange")
            nx.draw(G, pos,with_labels=True,node_size=100,nodelist=nobes_upper_level,node_shape="s",node_color="red",font_size=8)
            # labels = nx.draw_networkx_labels(G, pos)



        canvas = plt.get_current_fig_manager().canvas
        canvas.draw()
        pil_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
        pil_image.save(output_file+".png")
        plt.close('all')



    def get_nodes_by_level(self,G,value):
        labels = nx.get_node_attributes(G,"level")
        nodes = [x for x in labels if labels[x]==value]
        return nodes

    def get_nodes_by_upper_level(self, G, value):
        labels = nx.get_node_attributes(G, "level")
        nodes = [x for x in labels if labels[x] > value]
        return nodes

    def point_network_map(self,position, size):
        zx_pos = size[0] * 0.02
        zy_pos = size[1] * 0.05
        aspectx = size[0] * 0.20
        aspecty = size[1] * 0.20
        x = zx_pos + position[0] * aspectx
        y = zy_pos + position[1] * aspecty
        return [x, y]

    def is_new_frame(self, point, next_point):
        if next_point is not None:
            if 'VideoFrame' in point:
                new_frame = point['VideoFrame'] != next_point['VideoFrame']
            else:
                new_frame = point['Date'] != next_point['Date']
        else:
            new_frame = False

        return new_frame





