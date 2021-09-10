import time
from aco import aco
import tkinter as tk
import numpy as np

class paramWindow:
    def __init__(self):
        self.param_window = tk.Tk()
        self.inputs = {}
        self.parameters = []
        self.valid_params = False

        self.param_window.title('ACO')

    def add_parameter(self, paramId, dataType, default, valRange=None, label="Parameter"):
        self.inputs[paramId] = {
            'label': label,
            'entry': None,
            'value': None,
            'valRange': valRange,
            'dataType': dataType,
            'default': default
        }
        
    def display_window(self):
        frame = tk.Frame(master=self.param_window)
        frame.grid(padx=10, pady=20, columnspan=2)
        tk.Label(master=frame, text="Enter simulation parameters").pack()

        self.status_text = tk.StringVar()
        self.status_text.set("Status message")
        
        self.rows = 1
        for input_key in self.inputs.keys():
            input_dict = self.inputs[input_key]
            
            frame = tk.Frame(master=self.param_window)
            frame.grid(row=self.rows, column=0, padx=10, pady=5)
            input_dict['label'] = tk.Label(master=frame, text=input_dict['label'])
            input_dict['label'].pack()

            frame = tk.Frame(master=self.param_window)
            frame.grid(row=self.rows, column=1, padx=10, pady=5)
            input_dict['entry'] = tk.Entry(master=frame, width=10)
            input_dict['entry'].insert(0, input_dict['default'])
            input_dict['entry'].pack()
            
            self.rows += 1

        frame = tk.Frame(master=self.param_window)
        frame.grid(padx=10, pady=20, columnspan = 2)
        self.submit_btn = tk.Button(master=frame, text="Submit", width=10)
        self.submit_btn.pack()
        self.submit_btn.bind("<Button-1>", self.submit_values)

        self.param_window.mainloop()
        return self.parameters

    def update_values(self):
        for key in self.inputs.keys():
            value = self.inputs[key]['entry'].get()
            self.inputs[key]['value'] = value

    def submit_values(self, event):
        self.update_values()
        self.parameters = []
        
        failed = False
        for key in self.inputs.keys():
            input_dict = self.inputs[key]
            input_dict['label'].config(fg='black')
            try:
                if input_dict['dataType'] == int:
                    value = int(input_dict['value'])
                elif input_dict['dataType'] == float:
                    value = float(input_dict['value'])
                elif input_dict['dataType'] == bool:
                    if input_dict['value'].upper() in ['TRUE', 'FALSE']:
                        value = (input_dict['value'].upper() == 'TRUE')
                    else:
                        input_dict['label'].config(fg='red')
                        self.status_text.set("Wrong data types used: true / false.")
                        failed = True
                        
                if input_dict['valRange'] != None:
                    valRange = input_dict['valRange']
                    if value < valRange[0] or value > valRange[1]:
                        input_dict['label'].config(fg='red')
                        self.status_text.set("Values out of range: "+str(valRange[0])+" - "+str(valRange[1]))
                        failed = True
                        
                self.parameters.append(value)
                
            except ValueError:
                input_dict['label'].config(fg='red')
                self.status_text.set("Wrong data types used.") 
                failed = True
                
        if not hasattr(self, 'status'):
            frame = tk.Frame(master=self.param_window)
            frame.grid(padx=10, pady=5, columnspan = 2)
            self.status = tk.Label(master=frame, textvariable=self.status_text)
            self.status.pack()

        if not failed:
            self.status.config(fg='green')
            self.status_text.set("Done!")
            self.param_window.after(1000, self.param_window.destroy)
        else:
            self.status.config(fg='red')
            self.parameters = []

class mainWindow:
    def __init__(self, parameters):
        self.columns = parameters[0]
        self.rows = parameters[1]
        self.ants = parameters[2]
        self.food = parameters[4]
        self.speed = parameters[6]

        self.aco = aco((self.rows, self.columns), self.ants, self.food, carry_capacity=parameters[3], food_capacity=parameters[5], home_coors=[int(self.rows/2), int(self.columns/2)])
        
        self.grid = []
        
        self.running = False

    def display(self):
        self.main_window = tk.Tk()
        self.status_text = tk.StringVar()
        self.status_text.set("Click start to run the simulation.")

        self.grid_frame = tk.Frame(master=self.main_window, relief=tk.RAISED,  borderwidth=1)
        self.grid_frame.grid(padx=10, pady=10)

        for y in range(self.rows):
            row = []
            for x in range(self.columns):
                frame = tk.Frame(master=self.grid_frame, width=10, height=10, bg='blue')
                frame.grid(row=y, column=x, padx=1, pady=1)
                row.append(frame)
            self.grid.append(row)

        frame = tk.Frame(master=self.main_window)
        frame.grid(padx=10, pady=5, columnspan = self.columns)
        self.status = tk.Label(master=frame, textvariable=self.status_text)
        self.status.pack()

        frame = tk.Frame(master=self.main_window)
        frame.grid(padx=10, pady=5, columnspan = self.columns)
        self.submit_btn = tk.Button(master=frame, text="Start", width=10)
        self.submit_btn.pack()
        self.submit_btn.bind("<Button-1>", self.start_aco)

        frame = tk.Frame(master=self.main_window)
        frame.grid(padx=10, pady=5, columnspan = self.columns)
        self.submit_btn = tk.Button(master=frame, text="End", width=10)
        self.submit_btn.pack()
        self.submit_btn.bind("<Button-1>", self.start_aco)

        frame = tk.Frame(master=self.main_window, width=10, height=15)
        frame.grid(columnspan = self.columns)

        self.main_window.mainloop()

    def start_aco(self, event):
        """
        for ant in self.aco.ants:
            ant_coors = ant.location
            self.grid[ant_coors[0]][ant_coors[1]].config(bg='red')
            """
        self.running = True
        self.main_window.after(100, self.update_aco)

    def end_aco(self, event):
        self.running = False

    def update_aco(self):
        if self.running:
            for x in range(self.columns):
                for y in range(self.rows):
                    colour = get_colour((self.aco.pheromones[x][y]-1)/50, [(255, 255, 255), (0, 0, 0)])
                    self.grid[x][y].config(bg=colour)
            for ant in self.aco.ants:
                ant_coors = ant.location
                self.grid[ant_coors[0]][ant_coors[1]].config(bg='red')

            home_coors = self.aco.home_coors
            self.grid[home_coors[0]][home_coors[1]].config(bg='blue')

            for food_key in self.aco.food.keys():
                food = self.aco.food[food_key].location
                self.grid[food[0]][food[1]].config(bg=get_colour(self.aco.food[food_key].food_val/self.aco.food[food_key].food_capacity, [(184, 232, 182), (55, 144, 52)]))
            
            total_food = self.aco.increment()
            brought_food = self.aco.brought_food
            if not self.aco.is_finished():
                self.status_text.set("Total: "+str(total_food)+", brought: "+str(brought_food))
                self.main_window.after(100, self.update_aco)
            else:
                self.status.config(fg='green')
                self.status_text.set("Simulation complete!")
            
def get_colour(progress, colours):
    """
    Interpolates between colours by a given percent.
    :param progress: Value 0 <= x <= 1 of how far to interpolate
    :param colours:  List of 2 colours to interpolate betweeen
    :return str:     Hex code of final colour
    """
    if progress >= 0 and progress <= 1:
        start_colour, end_colour = colours[0], colours[1]

        r = start_colour[0] + (end_colour[0] - start_colour[0]) * progress
        b = start_colour[1] + (end_colour[1] - start_colour[1]) * progress
        g = start_colour[2] + (end_colour[2] - start_colour[2]) * progress

        return '#%02x%02x%02x' % (round(r), round(b), round(g))
    
    else: return '#000000'

if __name__ == "__main__":

    param_input = paramWindow()
    param_input.add_parameter('x', dataType=int, default=25, label='Rows:',  valRange=[0, 100])
    param_input.add_parameter('y', dataType=int, default=25, label='Columns:',  valRange=[0, 100])
    param_input.add_parameter('ants', dataType=int, default=25, label='Number of ants:',  valRange=[0, 100])
    param_input.add_parameter('carry', dataType=int, default=3, label='Ant carry capacity:',  valRange=[1, 10])
    param_input.add_parameter('food', dataType=int, default=10, label='Amount of food:',  valRange=[1, 20])
    param_input.add_parameter('fsize', dataType=int, default=10, label='Size of food',  valRange=[1, 20])
    param_input.add_parameter('speed', dataType=float, default=100, label='Simulation Speed (%):',  valRange=[10, 500])

    parameters = param_input.display_window()
    
    main = mainWindow(parameters)
    main.display()