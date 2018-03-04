#! /usr/bin/python
import sys
sys.path.append('../src')
import pyschedule
import math, sys

cities = '\
Aachen 50.45 6.06\n\
Aalen 48.51 10.06\n\
Aller 52.56 09.12\n\
Amberg 49.26 11.52\n\
Amper 48.29 11.55\n\
Ansbach 49.28 10.34\n\
Arnsberg 51.24 08.05\n\
Aschaffenburg 49.58 09.06\n\
Aschersleben 51.45 11.29\n\
Augsburg 48.25 20.20\n\
Aurich 53.28 07.28\n\
BadKissingen 50.11 10.04\n\
BadenBaden 48.44 08.13\n\
BadenWurttemberg 48.20 08.40\n\
Bamberg 49.54 10.54\n\
Bautzen 51.10 14.26\n\
Bavaria/Bayern 48.50 12.00\n\
Bayern 48.50 12.00\n\
Bayreuth 49.56 11.35\n\
BergischGladbach 50.59 07.08\n\
Berlin 52.30 13.25\n\
Bernburg 51.47 11.44\n\
Biberach 48.05 09.47\n\
Beilefeld 52.01 08.33\n\
BlackForest/Schwarzwald 48.30 08.20\n\
Bochum 51.28 07.13\n\
BohemianForest/Bohmerwald 49.08 13.14\n\
Bohmerwald 49.08 13.14\n\
Bonn 50.46 07.06\n\
Borkum 53.34 06.40\n\
Bottrop 51.31 06.58\n\
Brandenburg/Neubrandenburg 53.33 13.1\n\
Brandenburg 52.25 12.33\n\
Brandenburg 52.50 13.00\n\
Braunschweig 52.15 10.31\n\
Bremen 53.04 08.47\n\
Bremerhaven 53.33 08.36\n\
Brocken 51.47 10.37\n\
Brunswick/Braunschweig 52.15 10.31\n\
Buxtehude 53.28 09.39\n\
Celle 52.37 10.04\n\
Chemnitz 50.51 12.54\n\
Chiemsee 47.53 12.28\n\
Coburg 50.15 10.58\n\
Cologne/Koln 50.56 06.57\n\
Constance/Konstanz 47.40 09.10\n\
Cottbus 51.45 14.20\n\
Crailsheim 49.08 10.05\n\
Cuxhaven 53.51 08.41\n\
Dachau 48.15 11.26\n\
Darmstadt 49.51 08.39\n\
Deggendorf 48.50 12.57\n\
Dessau 51.51 12.14\n\
Detmold 51.56 08.52\n\
DeutshceBucht 54.15 08.00\n\
Donauworth 48.43 10.47\n\
Dortmund 51.30 07.28\n\
Dresden 51.03 13.44\n\
Duisburg 51.26 06.45\n\
Duren 50.48 06.29\n\
Dusseldorf 51.14 06.47\n\
Eberswalde-Finow 52.50 13.49\n\
Eder 51.12 09.28\n\
Eifel 50.15 06.50\n\
Eisenach 50.58 10.19\n\
Elde 53.07 11.15\n\
Elmshorn 53.43 09.40\n\
Emden 53.21 07.12\n\
Ems 53.20 07.12\n\
Erfurt 50.58 11.02\n\
Erlangen 49.36 11.00\n\
Erzgebirge 50.27 12.55\n\
Essen 51.28 07.02\n\
Esslingen 48.44 09.18\n\
Fehmarn 54.27 11.07\n\
Flensburg 54.47 09.27\n\
Fohr 54.43 08.30\n\
Forst 51.45 14.37\n\
Frankfurt,Brandenburg 52.20 14.32\n\
Frankfurt,Hessen 50.07 08.41\n\
FrankischeAlb 49.10 11.23\n\
Freiburg 47.59 07.51\n\
Freising 48.24 11.45\n\
Friedrichshafen 47.39 09.30\n\
Fulda 50.32 09.40\n\
Fulda 51.25 09.39\n\
Furstenwalde 52.22 14.03\n\
Furth 49.28 10.59\n\
Garmisch-Patenkirchen 47.30 11.06\n\
Geesthacht 53.26 10.22\n\
Gelsenkirchen 51.32 07.06\n\
Gera 50.53 12.04\n\
Giessen 50.34 08.41\n\
Goppingen 48.42 09.39\n\
Gorlitz 51.09 14.58\n\
Gosalr 51.54 10.25\n\
Gotha 50.56 10.42\n\
Gottingen 51.31 09.55\n\
Greifswald 54.05 13.23\n\
Greiz 50.59 12.10\n\
GrosserArber 49.06 13.08\n\
Gustrow 53.47 12.10\n\
Gutersloh 51.54 08.24\n\
Hagen 51.21 07.27\n\
Halberstadt 51.54 11.03\n\
Halle 51.30 11.56\n\
Hamburg 53.33 09.59\n\
Hameln 52.06 09.21\n\
Hamlin/Hamein 52.06 09.21\n\
Hamm 51.40 07.50\n\
Hanau 50.07 08.56\n\
Hannover 52.22 09.46\n\
Hanover/Hannover 52.22 09.46\n\
Harz 51.38 10.44\n\
Havel 52.50 12.03\n\
Heidelberg 49.24 08.42\n\
Heilbronn 49.09 09.13\n\
Helgoland 54.10 07.53\n\
Heligoland/Helgoland 54.10 07.53\n\
HeligolandB/DeutscheBucht 54.15 08.00\n\
Herford 52.07 08.39\n\
Herne 51.32 07.14\n\
Hesse/Hessen 50.30 09.00\n\
Hessen 50.30 09.00\n\
Hildesheim 52.09 09.56\n\
Hof 50.19 11.55\n\
HoherRhon/Rhon 50.24 09.58\n\
Hoxter 51.46 09.22\n\
Hoyerswerda 51.26 14.14\n\
Hunsruck 49.56 07.27\n\
Idar-Oberstein 49.43 07.16\n\
Iller 48.23 09.58\n\
Ingolstadt 48.46 11.26\n\
Isar 48.48 12.57\n\
Itzehoe 53.55 09.31\n\
Jena 50.54 11.35\n\
Jura/SchwabischeAlb 48.20 09.30\n\
kaiserslautern 49.26 07.45\n\
Karl-Marx-stadt/Chemnitz 50.51 12.54\n\
Karlsruhe 49.00 08.23\n\
Kassel 51.18 09.26\n\
Kempten 47.45 10.17\n\
Kiel 54.19 10.08\n\
KielCanal/Nord-Ostsee-Kanal 54.12 09.32\n\
KielerBucht 54.35 10.25\n\
Koblenz 50.21 07.36\n\
Koln 50.56 06.57\n\
Konstanz 47.40 09.10\n\
Krefeld 51.20 06.33\n\
Lahn 50.19 07.37\n\
Landshut 48.34 12.08\n\
Lauchhammer 51.29 13.47\n\
Lech 48.43 10.56\n\
Leer 53.13 07.26\n\
Leine 52.43 09.36\n\
Leipzig 51.18 12.22\n\
Limburg 50.22 08.04\n\
Lingen 52.31 07.19\n\
Lippe 51.39 06.36\n\
LowerSaxony=Niedersachsen 52.50 09.0\n\
Lubeck 53.52 10.40\n\
Luckenwalde 52.05 13.10\n\
Ludwigsburg 48.53 09.11\n\
Ludwigshafen 49.29 08.26\n\
Luneburg 53.15 10.24\n\
LuneburgHeath=LuneburgerHeide 53.10 10.12\n\
LuneburgerHeide 53.10 10.12\n\
LutherssstadtWittenberg 51.53 12.39\n\
Magdeburg 52.07 11.38\n\
Main 50.0 08.18\n\
Mainz 50.01 08.14\n\
MannheiM 49.29 08.29\n\
Marburg 50.47 08.46\n\
Mecklenburg 53.33 11.40\n\
MeckelenburgerBucht 54.20 11.40\n\
Meissen 51.09 13.29\n\
Memmingen 47.58 10.10\n\
Merseburg 51.22 11.59\n\
Minden 52.17 0\n\
Monchegladbach 51.11 06.27\n\
Muhlhausen 51.12 10.27\n\
Mulde 51.53 12.15\n\
Mulheim 51.52 06.54\n\
Munchen 48.08 11.34\n\
Munchen-Gladbach/Monchengladbach 51.11 06.27\n\
Muden 51.25 09.38\n\
Munich/Munchen 48.08 11.31\n\
Munster 51.58 07.37\n\
Muritz 53.25 12.42\n\
Naab 49.01 12.2\n\
Naumburg 51.09 11.47\n\
Neckar 49.27 08.29\n\
Neumunster 54.04 09.58\n\
Neunkirchen 49.20 07.09\n\
Neuruppin 52.55 12.48\n\
Neustrelitz 53.21 13.04\n\
Niedersachsen 52.50 09.0\n\
Nienburg 52.39 09.13\n\
Nord-Ostsee-Kanal 54.12 09.32\n\
Norderney 53.42 07.09\n\
Norderstedt 53.42 10.01\n\
NordfriesischeInsein 54.40 08.20\n\
Nordhausen 51.30 10.47\n\
Nordrhein-Westfalen 51.45 07.30\n\
NorthFrisianIs./NordfriesischeInseln 54.40 08.20\n\
NorthRhineWestphalia/Nordrhein-Westfalen 51.45 07.30\n\
Nuremberg/Nurnberg 49.27 11.03\n\
Nurnberg 49.27 11.03\n\
Oberhausen 51.28 06.51\n\
Offenbach 50.06 08.44\n\
Offenburg 48.28 07.56\n\
Oldenburg 53.09 08.13\n\
Oranienburg 52.45 13.14\n\
OreMts/Erzgebirge 50.27 12.55\n\
Osnabruck 52.17 08.03\n\
OstfriesischeInsein 53.42 07.0\n\
Paderborn 51.42 08.45\n\
Parchim 53.26 11.52\n\
Passau 48.34 13.28\n\
Peine 52.19 10.14\n\
Pforzheim 48.52 08.41\n\
Pirmasens 49.12 07.36\n\
Plauen 50.30 12.08\n\
Plockenstein 48.46 13.51\n\
Potsdam 52.25 13.04\n\
Puttgarden 54.30 11.10\n\
Rathenow 52.37 12.19\n\
Ravensburg 47.46 09.36\n\
Recklinghausen 51.7 07.12\n\
Regensburg 49.01 12.06\n\
Reichenbach 50.37 12.17\n\
Remscheid 51.11 07.12\n\
Rendsburg 54.17 09.39\n\
Reutlingen 48.29 09.12\n\
Rhein-Main-Donau-Kanal 52.17 07.26\n\
Rheine 52.17 07.26\n\
Rheinland-Pfalz 50.0 07.0\n\
Rhineland-Palatinate=Rheinland-Pfalz 50.0 07.0\n\
Rhon 50.24 09.58\n\
Riesa 51.17 13.17\n\
Rostock 54.5 12.8\n\
Rugen 54.22 13.24\n\
Saale 51.56 11.54\n\
Sachsen 50.55 13.10\n\
Salzgitter 52.9 10.19\n\
Salzwedel 52.52 11.10\n\
Sassnitz 54.29 13.39\n\
Sauerland 51.12 7.59\n\
Saxony/Sachsen 50.55 13.10\n\
Scjhleswig 54.31 9.34\n\
SchwabischeAlb 48.20 9.30\n\
Schwedt 53.3 14.16\n\
Schweinfurt 50.3 10.14\n\
Schwerin 53.36 11.22\n\
Speyer 49.29 8.25\n\
Stade 53.35 9.29\n\
Trier 49.45 6.38\n\
Tubingen 48.31 9.4\n\
Tuttlingen 47.58 8.48\n\
Uelzen 52.57 10.32\n\
Ulm 48.23 9.58\n\
Villingen-Schwenningen 48.3 8.26\n\
Vgogelsberg 50.31 9.12\n\
Wangerooge 53.47 7.54\n\
Wasserkuppe 50.29 9.55\n\
Weiden 49.41 12.10\n\
Weimar 50.58 11.19\n\
Werra 51.24 9.39\n\
Weser 53.36 8.28\n\
Wetzlar 50.32 8.31\n\
Wismar 53.54 11.29\n\
Wittenberge 53.0 11.45\n\
Worms 49.37 8.21\n\
Wuppertal 51.16 7.12\n\
Wurzburg 49.46 9.55'

# euclidean distance computation
def eucl_dist(orig,dest) :
	return math.sqrt( (orig[0]-dest[0])**2 + (orig[1]-dest[1])**2 )

# get cities table
cities_table = [ row.split(' ') for row in cities.split('\n') ]
cities_table = [ (city,float(lon),float(lat)) for city,lon,lat in cities_table ]
n = 10 # use only few cities to test, more cities take a lone time #len(cities_table)
capacity = int(n/2) # each vehicle can visit half of the cities
coords = { cities_table[i][0] : (cities_table[i][2],cities_table[i][1]) for i in range(n) }
cities = list(coords)

# add coordinates of vitual start and end at the first city in list
orig_city = cities_table[0][0]
coords['orig'] = coords[orig_city]
coords['dest'] = coords[orig_city]

# create scenario, city visit tasks, and start and end tasks of blue and red vehicle
S = pyschedule.Scenario('VRP_Germany',horizon=30)
T = { city : S.Task(city) for city in cities }

# resources
# capacity + 2 to include start and end task
R_blue, R_red = S.Resource('blue'), S.Resource('red')

# tasks
T['orig'] = S.Task('orig')
T['dest'] = S.Task('dest')

# precedences
S += T['orig'] < { T[city] for city in cities if city != 'orig' }
S += T['dest'] > { T[city] for city in cities if city != 'dest' }

# resource assignments
T['orig'] += [ R_blue, R_red ]
T['dest'] += [ R_blue, R_red ]
for city in cities :
	T[city] += R_blue|R_red

# distances
S += [ T[city] + int(eucl_dist(coords[city],coords[city_])) << T[city_] \
       for city in cities for city_ in cities if city != city_ ]
S += [ T['orig'] + int(eucl_dist(coords['orig'],coords[city])) << T[city] for city in cities ]
S += [ T[city] + int(eucl_dist(coords['orig'],coords[city])) << T['orig'] for city in cities ]

# capacities (+2 because start and end)
S += R_blue['length'] <= capacity+2
S += R_red['length'] <= capacity+2

# objective
S += T['dest']*1

if not pyschedule.solvers.mip.solve_bigm(S,kind='CBC',time_limit=60,msg=1):
	print('no solution found')
	sys.exit()

pyschedule.plotters.matplotlib.plot(S,resource_height=1.0,)

# plot tours
import pylab
sol = S.solution()

blue_tour = [ coords[str(city)] for (city,resource,orig,dest) in sol if str(city) in coords and str(resource) == 'blue' ]
pylab.plot([ x for x,y in blue_tour ],[ y for x,y in blue_tour],linewidth=2.0,color='blue')
red_tour = [ coords[str(city)] for (city,resource,orig,dest) in sol if str(city) in coords if str(resource) == 'red' ]
pylab.plot([ x for x,y in red_tour ],[ y for x,y in red_tour],linewidth=2.0,color='red')

# plot city names
for city in cities : pylab.text(coords[str(city)][0], coords[str(city)][1], city,color='black',fontsize=10)

pylab.title('VRP Germany')
pylab.show()


















