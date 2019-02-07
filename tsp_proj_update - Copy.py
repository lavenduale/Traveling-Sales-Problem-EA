import math
import random
import time
import matplotlib.pyplot as plt

city_name = "TSP_WesternSahara_29.txt"
#city_name = "TSP_Uruguay_734.txt"
#city_name = "TSP_Canada_4663.txt"
generations = 200
sizeOfPopulation = 200

#Test
sqrtCalculations = 0

class City:
   def __init__(self, x=None, y=None):
      self.x = None
      self.y = None
      if x is not None:
         self.x = x
      else:
         self.x = int(random.random() * 200)
      if y is not None:
         self.y = y
      else:
         self.y = int(random.random() * 200)
   
   def getX(self):
      return self.x
   
   def getY(self):
      return self.y
   
   def distanceTo(self, city):
      xDistance = abs(self.getX() - city.getX())
      yDistance = abs(self.getY() - city.getY())
      distance = math.sqrt( (xDistance*xDistance) + (yDistance*yDistance) )
      global sqrtCalculations
      sqrtCalculations = sqrtCalculations + 1
      return distance
   
   def __repr__(self):
      return str(self.getX()) + ", " + str(self.getY())

# """NEW"""   
   def __eq__(self, other):
      if (isinstance(other, City)):
         return self.x == other.x and self.y == other.y
      return False

#"""NEW"""      
   def __ne__(self, other):
      return not self.__eq__(other)

class TourManager:
   destinationCities = []
   
   def addCity(self, city):
      self.destinationCities.append(city)
   
   def getCity(self, index):
      return self.destinationCities[index]
   
   def numberOfCities(self):
      return len(self.destinationCities)


class Tour:
   def __init__(self, tourmanager, tour=None):
      self.tourmanager = tourmanager
      self.tour = []
      self.fitness = 0.0
      self.distance = 0
      if tour is not None:
         self.tour = tour
      else:
         for i in range(0, self.tourmanager.numberOfCities()):
            self.tour.append(None)
   
   def __len__(self):
      return len(self.tour)
   
   def __getitem__(self, index):
      return self.tour[index]
   
   def __setitem__(self, key, value):
      self.tour[key] = value
   
   def __repr__(self):
      geneString = "|"
      for i in range(0, self.tourSize()):
         geneString += str(self.getCity(i)) + "|"
      return geneString
   
   def generateIndividual(self):
      for cityIndex in range(0, self.tourmanager.numberOfCities()):
         self.setCity(cityIndex, self.tourmanager.getCity(cityIndex))
      random.shuffle(self.tour)
   
   def getCity(self, tourPosition):
      return self.tour[tourPosition]
   
   def setCity(self, tourPosition, city):
      self.tour[tourPosition] = city
      self.fitness = 0.0
      self.distance = 0
   
   #""" NEW """  
   def popCity(self, tourPosition):
      return self.tour.pop(tourPosition)
   
   def getFitness(self):
      if self.fitness == 0:
         self.fitness = 1/float(self.getDistance())
      return self.fitness
   
   #""" NEW """   
   def insertCity(self, tourPosition, city):
      self.tour.insert(tourPosition, city)
   
   #""" NEW """
   def getCityIndex(self, city):
      for i in range(len(self.tour)):
         if self.tour[i] == city:
            return i
      return -1

   def getDistance(self):
      if self.distance == 0:
         tourDistance = 0
         for cityIndex in range(0, self.tourSize()):
            fromCity = self.getCity(cityIndex)
            destinationCity = None
            destinationCity = self.getCity((cityIndex + 1) % self.tourSize())
            tourDistance += fromCity.distanceTo(destinationCity)
         self.distance = tourDistance
      return self.distance
   
   def tourSize(self):
      return len(self.tour)
   
   def containsCity(self, city):
      return city in self.tour


class Population:
   def __init__(self, tourmanager, populationSize, initialise):
      self.tours = []
      for i in range(0, populationSize):
         self.tours.append(None)
      
      if initialise:
         for i in range(0, populationSize):
            newTour = Tour(tourmanager)
            newTour.generateIndividual()
            self.saveTour(i, newTour)
      
   def __setitem__(self, key, value):
      self.tours[key] = value
   
   def __getitem__(self, index):
      return self.tours[index]
   
   def saveTour(self, index, tour):
      self.tours[index] = tour
   
   def getTour(self, index):
      return self.tours[index]
   
   def getFittest(self):
      fittest = self.tours[0]
      for i in range(0, self.populationSize()):
         if fittest.getFitness() <= self.getTour(i).getFitness():
            fittest = self.getTour(i)
      return fittest
   
   def populationSize(self):
      return len(self.tours)


class GA:
   def __init__(self, tourmanager):
      self.tourmanager = tourmanager
      self.mutationRate = 0.015
      self.tournamentSize = 5
      self.elitism = True
   
   def evolvePopulation(self, pop, cur_generation, generation_size):
      newPopulation = Population(self.tourmanager, pop.populationSize(), False)
      elitismOffset = 0
      if self.elitism:
         newPopulation.saveTour(0, pop.getFittest())
         elitismOffset = 1
      
      for i in range(elitismOffset, newPopulation.populationSize()):
         parent1 = self.tournamentSelection(pop)
         parent2 = self.tournamentSelection(pop)
         child = self.crossover(parent1, parent2)
         newPopulation.saveTour(i, child)
      
      for i in range(elitismOffset, newPopulation.populationSize()):
         self.improvedMutate(newPopulation.getTour(i), cur_generation, generation_size)
      
      return newPopulation
   
   def crossover(self, parent1, parent2):
      child = Tour(self.tourmanager)
      
      startPos = int(random.random() * parent1.tourSize())
      endPos = int(random.random() * parent1.tourSize())
      
      for i in range(0, child.tourSize()):
         if startPos < endPos and i > startPos and i < endPos:
            child.setCity(i, parent1.getCity(i))
         elif startPos > endPos:
            if not (i < startPos and i > endPos):
               child.setCity(i, parent1.getCity(i))
      
      for i in range(0, parent2.tourSize()):
         if not child.containsCity(parent2.getCity(i)):
            for ii in range(0, child.tourSize()):
               if child.getCity(ii) == None:
                  child.setCity(ii, parent2.getCity(i))
                  break
      
      return child

   
   #""" NEW """
   #def improvedCrossover(self, parent1, parent2):
   #      child = parent1
   #      position = int(parent1.tourSize() * random.random())
   #      cycle = []
   #      while (parent1.getCity(position)) not in cycle:
   #         cycle.append(parent1.getCity(position))
   #         newCity = parent2.getCity(position)
   #         position = parent1.getCityIndex(newCity)
   #         
   #      for i in range (len(parent2)):
   #         if parent2.getCity(i) not in cycle:
   #            child.setCity(i, parent2.getCity(i))
   #     
   #      return child
   
   #def mutate(self, tour):
   #   for tourPos1 in range(0, tour.tourSize()):
   #      if random.random() < self.mutationRate:
   #         tourPos2 = int(tour.tourSize() * random.random())
   #         
   #         city1 = tour.getCity(tourPos1)
   #         city2 = tour.getCity(tourPos2)
            
   #         tour.setCity(tourPos2, city1)
   #         tour.setCity(tourPos1, city2)

   #""" NEW """        
   def improvedMutate(self, tour, cur_generation, generation_size):
         tourpos1 = int(tour.tourSize() * random.random())
         tourpos2 = int(tour.tourSize() * random.random())
        
         while (tourpos1 == tourpos2):
               tourpos2 = int(tour.tourSize() * random.random())
                
         if (cur_generation <= generation_size/2):
            city1 = tour.popCity(tourpos1)
            tour.insertCity(tourpos2, city1)
            
         else:
            fetchLength = 10
            if fetchLength + tourpos1 >= len(tour):
               tourpos1 = len(tour) - fetchLength - 1 
            
            for i in range (fetchLength):
               city1 = tour.popCity(tourpos1 + i)
               tour.insertCity(tourpos2 + i, city1)
   
   def tournamentSelection(self, pop):
      tournament = Population(self.tourmanager, self.tournamentSize, False)
      for i in range(0, self.tournamentSize):
         randomId = int(random.random() * pop.populationSize())
         tournament.saveTour(i, pop.getTour(randomId))
      fittest = tournament.getFittest()
      return fittest



if __name__ == '__main__':
   
   x1 = []
   y1 = []
   tourmanager = TourManager()
   with open(city_name, 'r') as f:
       for line in f:
           word = line.split(" ")
           new_city = City(float(word[1]),float(word[2]))
           x1.append(float(word[1]))
           y1.append(float(word[2]))
           tourmanager.addCity(new_city)
   x1.append(x1[0])
   y1.append(y1[0])
   
   # Initialize population
   pop = Population(tourmanager, sizeOfPopulation, True)
   print("Initial distance: " + str(pop.getFittest().getDistance()))
   start_time = time.time()
   # Evolve population for given generations
   ga = GA(tourmanager)
   generationSize = generations
   pop = ga.evolvePopulation(pop, 0, generationSize)
   z = []
   w = []
   x = []
   y = []
   for i in range(0, generationSize):
      pop = ga.evolvePopulation(pop, i, generationSize)
      z.append(pop.getFittest().getDistance())
      w.append(i)
      print("Generation: "+ str(i) + "/" + str(generationSize))
      
   
   end_time = time.time()
   # Print final results
   print("Finished")
   print("Elapsed time was {0:.1f} seconds.".format(end_time - start_time))
   print("sqrt used: ", sqrtCalculations, " times")
   print("Final distance: " + str(pop.getFittest().getDistance()))
   print("Solution:")

   mystring = str(pop.getFittest())
   mylist = mystring.split("|")
   mylist.pop(0)
   mylist.pop()
   for i in range(len(mylist)):
      ele = mylist[i].split(',')
      x.append(float(ele[0]))
      y.append(float(ele[1]))
   
   print(mylist)
   x.append(x[0])
   y.append(y[0])

# plotting the points  
plt.figure(1, figsize=(5,6.8))
plt.subplot(211)
plt.title("Original Path")
plt.plot(x1, y1, color='burlywood', linewidth = 1, marker='o', markerfacecolor='brown', markersize=4)
# function to show the plot
plt.subplot(212)
plt.title("Solution Path")
plt.plot(x, y, color='lightgreen', linewidth = 1, marker='o', markerfacecolor='white', markersize=4)

plt.figure(2)
plt.plot(w, z, linewidth=3.0)
plt.grid(True)
plt.title('Progress at Each Generation')
plt.ylabel('Distance')
plt.xlabel('Generation')
plt.show()
