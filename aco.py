import numpy as np
import random as rnd
import time

movements = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]

class aco:
    def __init__(self, dimensions, no_ants, no_food, carry_capacity=3, food_capacity=10, home_coors=None, pheromone_deposit=1000.0, evaporation_coefficient=0.02, alpha=10, beta=1, food_deplete=True, random_ant_colour=False, verbose=False):
        self.ants = []
        self.food = {}
        self.dimensions = dimensions
        self.pheromones = np.full(dimensions, 1.0, dtype=float)
        if home_coors != None:  
            self.home_coors = home_coors
        else:
            self.home_coors = [int(dimensions[0]/2), int(dimensions[1]/2)]
        self.all_food = no_food*food_capacity
        self.brought_food = 0
        self.evaporation_coefficient = 0.02
        self.pheromone_deposit = 1000.0
        self.alpha = alpha
        self.beta = beta
        self.food_deplete = food_deplete
        self.random_ant_colour = random_ant_colour

        if no_ants + no_food > dimensions[0]*dimensions[1]:
            print("not enough cells")
            exit()

        food_coors = [self.home_coors]
        while len(food_coors) < (no_food + 1):
            coors = [rnd.randint(0, dimensions[0]-1), rnd.randint(0, dimensions[1]-1)]
            if coors not in food_coors:
                self.food[str(coors[0])+","+str(coors[1])] = Food(coors, food_capacity)
                food_coors.append(coors)

        ant_coors = []
        
        ants_created = 0
        while ants_created < no_ants:
            coors = self.home_coors
            self.ants.append(Ant(coors, carry_capacity=carry_capacity, random_colour=self.random_ant_colour))
            ants_created += 1

        self.ant_grid, self.food_grid = self.get_object_grids()

    def start_aco(self):
        """
        Starts the ant colony optimisation, printing the grid
        to the console.
        """
        self.print_grid()
        while(True):

            if self.is_finished():
                break
            self.increment()
            self.print_grid()
            time.sleep(0.5)

        print("Simulation ended.")

    def increment(self):
        """
        Increments the simulation.
        :return int: Total food left
        """
        self.move_ants()
        self.ant_grid, self.food_grid = self.get_object_grids()
        total_food = 0

        for key in self.food.keys():
            total_food += self.food[key].food_val
        
        return total_food
        
    def is_finished(self):
        """
        Checks if all food is collected.
        :return bool: If all food is collected
        """
        carried_food = 0
        for ant in self.ants:
            carried_food += ant.current_carry

        return (self.all_food == self.brought_food) or (carried_food == 0 and len(self.food.keys()) == 0)

    def move_ants(self):
        """
        Moves all ants according to movement probabilities.
        """
        for ant in self.ants:
            for key in ant.taboo.keys():
                if ant.taboo[key] >= 1:
                    ant.taboo[key] -= 1
            mov_probs = self.get_movement_probs(ant)

            if sum(mov_probs) != 0:
                movement = rnd.choices(movements, weights=mov_probs, k=1)[0]
                x, y = ant.location[0]+movement[0], ant.location[1]+movement[1]
                ant.location = [x, y]
                if self.food_grid[x][y] > 0:
                    taboo_key = str(x)+","+str(y)
                    ant.taboo[str(x)+","+str(y)] = ant.taboo_cooldown
                    ant.current_carry += 1
                    if self.food[taboo_key].food_val > 1:
                        if self.food_deplete:
                            self.food[taboo_key].food_val -= 1
                    else: 
                        #self.food[taboo_key].food_val = 0
                        _ = self.food.pop(taboo_key)
                elif ant.location == self.home_coors:
                    self.brought_food += ant.current_carry
                    ant.current_carry = 0
                
            self.ant_grid, self.food_grid = self.get_object_grids()
            self.update_pheromones()

    
    def get_movement_probs(self, ant):
        """
        Finds an ant's movement probabilities for the 8 adjacent tiles.
        :param ant:      Ant to move
        :return [float]: Movement probabilties
        """
        centre = ant.location
        mov_weights = []
        food_present = False
        going_home = False

        for i in range(-1, 2):
            for j in range(-1, 2):
                if centre[0] + i >= 0 and centre[0] + i < self.dimensions[0]:
                    if centre[1] + j >= 0 and centre[1] + j < self.dimensions[1]:

                        # probability of not moving = 0
                        if i == 0 and j == 0:
                            continue
                        
                        # If adjacent to home, and carrying food, will always
                        # go to home. If not carrying food, probability = 0
                        elif [centre[0]+i, centre[1]+j] == self.home_coors:
                            if ant.current_carry > 0:
                                mov_weights = [0]*len(mov_weights)
                                mov_weights.append(1.0)
                                while len(mov_weights) < 8:
                                    mov_weights.append(0)
                                return mov_weights
                            else:
                                mov_weights.append(0)
                        
                        # Probability of moving to food is 1.0, if
                        # food present, all other movement weights = 0
                        elif self.food_grid[centre[0]+i][centre[1]+j] > 0:
                            taboo_key = str(centre[0]+i)+","+str(centre[1]+j)
                            if (taboo_key not in ant.taboo or ant.taboo[taboo_key] == 0) and ant.current_carry < ant.carry_capacity:
                                if not food_present:
                                    mov_weights = [0]*len(mov_weights)
                                    food_present = True
                                
                                mov_weights.append(self.food_grid[centre[0]+i][centre[1]+j])
                            else:
                                mov_weights.append(0)

                        # Probability of moving to a cell where there
                        # is already an ant = 0
                        elif self.ant_grid[centre[0]+i][centre[1]+j] == 1 or food_present:
                            mov_weights.append(0)

                        else: mov_weights.append(self.pheromones[centre[0]+i][centre[1]+j])
                    else: mov_weights.append(0)
                else: mov_weights.append(0)

        if ant.current_carry == ant.carry_capacity or (len(self.food.keys()) == 0):
            for i in range(len(mov_weights)):
                possible_move_location = [centre[0]+movements[i][0], centre[1]+movements[i][1]]
                if self.manhattan(possible_move_location) > self.manhattan(centre):
                    mov_weights[i] = 0
                elif mov_weights[i] > 0: mov_weights[i] = 1

        """
        # Implementing proper movement probability formula
        if sum(mov_weights) == 0:
            return mov_weights
        else:
            for i in range(len(mov_weights)):
                x, y = centre[0]+movements[i][0], centre[1]+movements[i][1]
                mov_weights[i] = (mov_weights[i]**self.alpha)*(self.manhattan([x,y])**self.beta)
            return [x / sum(mov_weights) for x in mov_weights]
        """
        return mov_weights

    def update_pheromones(self):
        """
        Applies pheromone evaporation and deposits.
        """
        for i in range(self.pheromones.shape[0]):
            for j in range(self.pheromones.shape[1]):
                self.pheromones[i][j] *= (1 - self.evaporation_coefficient)
                if self.pheromones[i][j] < 1.0:
                    self.pheromones[i][j] = 1.0

        for ant in self.ants:
            x, y = ant.location[0], ant.location[1]
            if ant.current_carry == ant.carry_capacity:
                self.pheromones[x][y] += self.pheromone_deposit

    def manhattan(self, coor):
        """
        Calculates manhattan distance from coordinate to home.
        :param coor: Starting coordinate
        :return int: Manhattan distance to home
        """
        return abs(coor[0]-self.home_coors[0]) + abs(coor[1]-self.home_coors[1])

    def print_grid(self, home_char='H', ant_char='A', food_char='F', empty_char='.'):
        """
        Prints grid to the console.
        :param home_char:  Character at home coor
        :param ant_char:   Character for all ants
        :param food_char:  Character for food
        :param empty_char: Character for empty tile
        """
        ant_grid, food_grid = self.get_object_grids()
        print(" "+("-"*(ant_grid.shape[1]*2+1)))
        for i in range(ant_grid.shape[0]):
            row = "| "
            for j in range(ant_grid.shape[1]):
                if [i, j] == self.home_coors: row += home_char+" "
                elif food_grid[i, j] > 0: row += food_char+" "
                elif ant_grid[i, j] == 1: row += ant_char+" "
                
                else: row += empty_char+" "
            print(row+"|")
        print(" "+("-"*(ant_grid.shape[1]*2+1)))

    def get_object_grids(self):
        """
        Returns grids denoting where ants and food are located.
        :return np.array: Numpy array denoting ants
        :return np.array: Numpy array denoting food
        """
        ant_grid = np.zeros(self.dimensions, dtype=int)
        food_grid = np.zeros(self.dimensions, dtype=int)
        ant_coors, food_coors = self.get_object_coors()
        for coors in ant_coors:
            ant_grid[coors[0]][coors[1]] = 1
        for coors in food_coors:
            food_grid[coors[0]][coors[1]] += 100
        return ant_grid, food_grid

    def get_object_coors(self):
        """
        Returns coordinates of all ants and food.
        :return [[int]]: All ant coordinates
        :return [[int]]: All food coordinates
        """
        ant_coors = []
        for ant in self.ants:
            ant_coors.append(ant.location)
        food_coors = []
        for food in self.food.values():
            food_coors.append(food.location)

        return ant_coors, food_coors

class Ant:
    def __init__(self, location, carry_capacity=3, taboo_cooldown=5, random_colour=False):
        self.location = location
        self.taboo = {}
        self.taboo_cooldown = taboo_cooldown
        self.carry_capacity = carry_capacity
        self.current_carry = 0
        if random_colour:
            self.colour = ("#%06x" % rnd.randint(0x55555, 0xFFFFFF)).upper()
        else:
            self.colour = "#FF0000"

class Food:
    def __init__(self, location, food_capacity=10):
        self.location = location
        self.food_val = food_capacity
        self.food_capacity = food_capacity

if __name__ == "__main__":
    acoApp = aco((20, 20), 25, 10)
    acoApp.start_aco()