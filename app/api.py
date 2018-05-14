import flask
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, mapping
from descartes import PolygonPatch

from app import app

@app.route('/')
def start():
    return flask.render_template('face.html')


@app.route('/find_area', methods=['GET'])
def find_area():
    request = flask.request.args
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    type = 'drive'

    trip_times = request.get('trip_times').split(',')
    ox.config(log_console=True, use_cache=True)
    G = ox.load_graphml('network.graphml')
    f = open("network_type.yml", "r")
    network_type = f.read()
    f.close()
    travel_speed = 60.0 if network_type == 'drive' else 4.5
    center_node = ox.get_nearest_node(G, (lat, lng))
    G = ox.load_graphml('project.graphml')
    meters_per_minute = travel_speed * 1000 / 60
    for u, v, k, data in G.edges(data=True, keys=True):
        data['time'] = data['length'] / meters_per_minute
    iso_colors = ox.get_colors(n=len(trip_times), cmap='Reds', start=0.3,
                               return_hex=True)

    isochrone_polys = []
    for trip_time in sorted(trip_times, reverse=True):
        subgraph = nx.ego_graph(G, center_node, radius=float(trip_time),
                                distance='time')

        node_points = [Point((float(data['lat']), float(data['lon']))) for
                             node, data in
                       subgraph.nodes(data=True)]
        bounding_poly = gpd.GeoSeries(node_points).unary_union.convex_hull
        isochrone_polys.append(bounding_poly)
    polygons_array = []
    for polygon, fc in zip(isochrone_polys, iso_colors):
        patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6,
                             zorder=-1)
        geojson = {
            "type": "Feature",
            "properties": {"timeline": trip_time},
            "geometry":
                {
                    "type": "Polygon",
                    "coordinates": [
                        list(
                            ([list(x)[0], list(x)[1]]
                             for x
                             in list(patch._path.vertices)
                             )
                        )
                        ]
                }
        }
        polygons_array.append(geojson)
    return flask.jsonify(polygons_array)



