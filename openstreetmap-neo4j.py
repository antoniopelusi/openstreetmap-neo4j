from py2neo import Graph
import os

#-------------------------------#
#--------Initialization---------#
#-------------------------------#

##initialize connection to the database
osm = Graph("bolt://localhost:7687", auth=("neo4j", "openstreetmap"))

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
|  1  | Search and locate a Point Of Interest by name
|  2  | Add a new Point Of Interest
|  3  | Remove an existing Point Of Interest
|  4  | List all the POI near another POI
|  5  | 
|  6  | 
|  7  | 
|  8  | 
|  9  | 
| 10  | 
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
""")

#clear the terminal for a clean view (platform indipendent)
def clear_terminal():
    os.system('cls||clear')

#1 - 
def locate_POI():
    print(osm.run("""
    MATCH (p1:PointOfInterest)
    WHERE p1.name = $name
    AND p1.name <> "pitch"
    RETURN p1.name as name, p1.location.x as X, p1.location.y as Y
    """, parameters={'name': name}).to_table())
#4 - List all the POI near another POI
def list_POI():
    print(osm.run("""
    MATCH (p1:PointOfInterest), (p2:PointOfInterest)
    WHERE p1<>p2
    AND p1.name = $name
    AND p2.name <> "pitch"
    AND distance(p1.location, p2.location) < $distance
    RETURN p2.name as name, distance(p1.location, p2.location) as distance
    
    """, parameters={'name': name, 'distance': distance}).to_table())

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

    if choice == "1": #1 - 
        clear_terminal()
        print("| Insert the name of the POI:")
        name = input("| >> ")
        locate_POI()


    elif choice == "4": #4 - List all the POI near another POI
        clear_terminal()
        print("| Insert the name of the POI:")
        name = input("| >> ")
        print("| Insert the max distance (in km):")
        distance = int(input("| >> "))*1000
        list_POI()

    else: #Any other character - Wrong input
        clear_terminal()

        print("\n| No command associated with key " + str(choice) + ".")