# 2D ACO Simulator

The ant colony optimisation (ACO) program simulates the movement of a colony of ants collecting food and bringing it home. Their individual movements are influenced by pheromones laid by other ants, which evaporates over time.

This changes a regular graph-based ant colony optimisation problem by applying it to a 2D grid-based problem. More information on ACO can be found [here](http://www.scholarpedia.org/article/Ant_colony_optimization).

## Console Version

```python
from aco import aco

# Creates an 12x12 ACO grid with 8 ants and 4 food.
ants = aco(dimensions=(12, 12), no_ants=8, food=4)

# Starts the simulation, printing the board to the console.
ants.start_aco()
```

```bash
>> python3 aco.py
 ---------------------
| . . . A . . . . . . |
| . . . . F . . . . . |
| . . . . . . . . . . |
| . . . . . . F . . . |
| . . . . . . . . . . |
| . . . . A H . . . . |
| . A . . . . . . . . |
| . . . . . . . . . F |
| . A . . A . . . A . |
| . . . . . A . . . . |
 ---------------------
```

## Window Version
The window version displays the simulation using Tkinter, and includes a window with parameter inputs.
```python
# Creates a parameter input window object.
param_input = paramWindow()

# Parameters can be defined with a data type, default value and
# possible range.
param_input.add_parameter(paramId='ants',
                          dataType=int,
                          default=25,
                          label='Number of ants:',
                          valRange=[0, 100])

# The display window function returns the values entered by the
# user once they have given valid inputs.
parameters = param_input.display_window()

# This can then be used to create the main simulation window and
# start the simulation.
main = mainWindow(parameters)
main.display()
```
![Simulation Grid](simulation_grid.png?raw=true "Simulation Grid")
