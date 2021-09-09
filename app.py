import aco
import tkinter as tk

class paramWindow:
    def __init__(self):
        self.param_window = tk.Tk()
        self.inputs = {}
        self.parameters = []

        self.param_window.title('ACO')

    def add_parameter(self, paramId, dataType, valRange=None, label="Parameter"):
        self.inputs[paramId] = {
            'label': label,
            'entry': None,
            'value': None,
            'valRange': valRange,
            'dataType': dataType
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
            input_dict['entry'].pack()
            
            self.rows += 1

        frame = tk.Frame(master=self.param_window)
        frame.grid(padx=10, pady=20, columnspan = 2)
        self.submit_btn = tk.Button(master=frame, text="Submit", width=10)
        self.submit_btn.pack()
        self.submit_btn.bind("<Button-1>", self.submit_values)

        self.param_window.mainloop()

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
        else:
            self.status.config(fg='red')
            self.parameters = []
       
if __name__ == "__main__":

    app = paramWindow()
    app.add_parameter('x', dataType=int, label='Rows:',  valRange=[0, 100])
    app.add_parameter('y', dataType=int, label='Columns:',  valRange=[0, 100])
    app.add_parameter('ants', dataType=int, label='Number of ants:',  valRange=[0, 100])
    app.add_parameter('food', dataType=int, label='Amount of food:',  valRange=[0, 20])
    app.add_parameter('other', dataType=bool, label='Boolean:')

    app.display_window()
