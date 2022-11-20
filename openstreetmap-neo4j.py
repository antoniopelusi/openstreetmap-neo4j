from py2neo import Graph
from py2neo import Node
import os
import re

#-------------------------------#
#--------Initialization---------#
#-------------------------------#

#initialize connection to the database
osm = Graph("bolt://localhost:7687", auth=("neo4j", "openstreetmap"))

#create index on name only at the first start
try:
    osm.run("CREATE INDEX ON:PointOfInterest(Name)")
except:
    pass

#-------------------------------#
#-----------Functions-----------#
#-------------------------------#

#print logo (only at the start)
def print_logo():
    print("""
   ___  ____  __  __                        _  _   _ 
  / _ \/ ___||  \/  |      _ __   ___  ___ | || | (_)
 | | | \___ \| |\/| |_____| '_ \ / _ \/ _ \| || |_| |
 | |_| |___) | |  | |_____| | | |  __/ (_) |__   _| |
  \___/|____/|_|  |_|     |_| |_|\___|\___/   |_|_/ |
                                                |__/ 
""")

#print menu (after every command)
def print_menu():
    print("""
_________________________________________________________________
|  0  | Exit
|  1  | Add a new Point Of Interest
|  2  | Remove an existing Point Of Interest
|  3  | Add a new Route
|  4  | Remove an existing Route
|  5  | Find Points of Interest near a place
|  6  | Search and locate a Point Of Interest by name
|  7  | Filter Points of interest by type
|  8  | Find Shortest Path between two Point Of Interest
|  9  | List all the Routes available from a Point
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
""")

#clear the terminal for a clean view (platform indipendent)
def clear_terminal():
    os.system('cls||clear')

#1 - Add a new Point Of Interest
def add_POI():
    print(osm.run("""
    CREATE (p:PointOfInterest:OSMNode {name: $name, type: $type, location: point({srid: 4326, x: $lon, y: $lat}), lon: $lon, lat: $lat})
    RETURN p.name AS name,  p.type AS type, p.location.x AS X, p.location.y AS Y
    """, parameters={'name': name, 'type':type, 'lon': lon, 'lat': lat}).to_table())
    
#2 - Remove an existing Point Of Interest
def remove_POI():
    osm.run("""
    MATCH (p:PointOfInterest)
    WHERE p.name = $name
    DELETE p
    """, parameters={'name': name})

#3 - Add a new Route
def add_Route():
    osm.run("""
    MATCH (source:PointOfInterest), (dest:PointOfInterest)
    WHERE source.name = $source
    AND dest.name = $dest
    CREATE (source)-[:ROUTE{distance: $dist}]->(dest)
    CREATE (source)<-[:ROUTE{distance: $dist}]-(dest)
    """, parameters={'source': source, 'dest': dest, 'dist': dist})

#4 - Remove an existing Route
def remove_Route():
    osm.run("""
    MATCH (source:PointOfInterest)<-[r:ROUTE]->(dest:PointOfInterest)
    WHERE source.name = $source
    AND dest.name = $dest
    DELETE r
    """, parameters={'source': source, 'dest': dest})

#5 - Find Points of Interest near a place
def list_POI():
    print(osm.run("""
    MATCH (source:PointOfInterest), (dest:PointOfInterest)
    WHERE source<>dest
    AND source.name = $name
    AND dest.name <> "pitch"
    AND point.distance(source.location, dest.location) <= $dist
    CALL apoc.algo.dijkstra(source, dest, 'ROUTE', 'distance') YIELD weight
    RETURN dest.name AS name, dest.type AS type, round(weight) AS distance
    ORDER BY distance ASC
    LIMIT 10
    """, parameters={'name': name, 'dist': dist}).to_table())

#6 - Search and locate a Point Of Interest by name
def locate_POI():
    print(osm.run("""
    MATCH (p:PointOfInterest)
    WHERE p.name = $name
    RETURN p.name AS name, p.type AS type, p.location.x AS X, p.location.y AS Y
    """, parameters={'name': name}).to_table())

#7 - Filter Points of interest by type
def filter_POI():
    print(osm.run("""
    MATCH (p1:PointOfInterest), (p2:PointOfInterest)
    WHERE p2.type = $type
    AND p1.name = $name
    AND p2.name <> "pitch"
    AND point.distance(p1.location, p2.location) <= $dist
    RETURN p2.name AS name, p2.type AS type, p2.location.x AS X, p2.location.y AS Y
    LIMIT 10
    """, parameters={'name': name, 'type': type, 'dist': dist}).to_table())

#8 - Find Shortest Path between two Point Of Interest
def sp_POI():
    print(osm.run("""
    MATCH (source:PointOfInterest),(dest:PointOfInterest)
    WHERE source.name = $source
    AND dest.name = $dest
    CALL apoc.algo.dijkstra(source, dest, 'ROUTE', 'distance') YIELD weight
    RETURN source.name, dest.name, round(weight) AS distance;
    """, parameters={'source': source, 'dest': dest}).to_table())

    path = str(osm.run("""
    MATCH (source:PointOfInterest),(dest:PointOfInterest)
    WHERE source.name = $source
    AND dest.name = $dest
    CALL apoc.algo.dijkstra(source, dest, 'ROUTE', 'distance') YIELD path
    RETURN path;
    """, parameters={'source': source, 'dest': dest}).to_subgraph())

    #regular expression to remove all the node properties from the path
    path = re.sub(r'({[^}]*)?[{}]', '', path)
    print(path)

#9 - List all the Routes available from a Point
def list_Route():
    print(osm.run("""
    MATCH routes=(source:PointOfInterest{name: $name})-[:ROUTE]-()
    RETURN routes
    """, parameters={'name': name}).to_table())

#-------------------------------#
#-------------Start-------------#
#-------------------------------#

choice = -1

clear_terminal()
print_logo()

while choice != 0:
    print_menu()
    choice = input(">> ")

    if choice == "0": #0 - Exit
        clear_terminal()
        print_logo()
        print("\n| Closing OSM database...\n")
        break

    elif choice == "1": #1 - Add a new Point of Interest
        clear_terminal()
        print("| Insert the name of the POI to create:")
        name = input("| >> ")
        print("| Insert the type of the POI to create:")
        type = input("| >> ")
        print("| Insert the latitude (X):")
        lon = float(input("| >> "))
        print("| Insert the longitude (Y):")
        lat = float(input("| >> "))
        add_POI()
        print("| Point of Interest added")

    elif choice == "2": #2 - Remove an existing Point Of Interest
        clear_terminal()
        print("| Insert the name of the POI to delete:")
        name = input("| >> ")
        remove_POI()
        print("| Point of Interest removed")

    elif choice == "3": #3 - Add a new Route
        clear_terminal()
        print("| Insert the name of the first Point Of Interest:")
        source = input("| >> ")
        print("| Insert the name of the second Point Of Interest:")
        dest = input("| >> ")
        print("| Insert the distance between the Points Of Interest:")
        dist = float(input("| >> "))
        add_Route()
        print("| Route added")

    elif choice == "4": #4 - Remove an existing Route
        clear_terminal()
        print("| Insert the name of the first Point Of Interest:")
        source = input("| >> ")
        print("| Insert the name of the second Point Of Interest:")
        dest = input("| >> ")
        remove_Route()
        print("| Route removed")

    elif choice == "5": #5 - Find Points of Interest near a place
        clear_terminal()
        print("| Insert the name of the place:")
        name = input("| >> ")
        print("| Insert the max distance (in meters):")
        dist = float(input("| >> "))
        print('\n')
        list_POI()

    elif choice == "6": #6 - Search and locate a Point Of Interest by name
        clear_terminal()
        print("| Insert the name:")
        name = input("| >> ")
        print('\n')
        locate_POI()

    elif choice == "7": #7 - Filter Points of interest by type
        clear_terminal()
        print("| Insert the name of the Point of Interest:")
        name = input("| >> ")
        print("| Insert the type:")
        type = input("| >> ")
        print("| Insert the max distance (in meters):")
        dist = float(input("| >> "))
        print('\n')
        filter_POI()

    elif choice == "8": #8 - Find Shortest Path between two Point Of Interest
        clear_terminal()
        print("| Insert the start Point:")
        source = input("| >> ")
        print("| Insert the destination Point:")
        dest = input("| >> ")
        print('\n')
        sp_POI()

    elif choice == "9": #9 - List all the Routes available from a Point
        clear_terminal()
        print("| Insert the name of the Point of Interest:")
        name = input("| >> ")
        print('\n')
        list_Route()

    else: #Any other character - Wrong input
        clear_terminal()
        print("\n| No command associated with key " + str(choice) + ".")