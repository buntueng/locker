import pathlib
import pygubu
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "newproject"


class NewprojectApp:
    def __init__(self, master=None):
        # build ui
        self.main_frame = ttk.Frame(master)
        self.start_button = ttk.Button(self.main_frame)
        self.start_button.configure(text='START', width='15')
        self.start_button.grid(column='4', padx='10', row='0', sticky='e')
        self.start_button.configure(command=self.start_button_pressed)
        self.stop_button = ttk.Button(self.main_frame)
        self.stop_button.configure(text='STOP', width='15')
        self.stop_button.grid(column='4', padx='10', row='1', sticky='e')
        self.stop_button.configure(command=self.stop_button_pressed)
        self.serial_port = ttk.Combobox(self.main_frame)
        self.comport = tk.StringVar(value='')
        self.serial_port.configure(textvariable=self.comport, width='8')
        self.serial_port.grid(column='1', padx='10 10', row='0', sticky='w')
        self.port_label = ttk.Label(self.main_frame)
        self.port_label.configure(text='เลือกคอมพอร์ต')
        self.port_label.grid(column='0', padx='10 0', pady='10', row='0', sticky='w')
        self.data_label = ttk.Label(self.main_frame)
        self.data_label.configure(text='ข้อมูล')
        self.data_label.grid(column='0', padx='10', row='1', sticky='w')
        self.text1 = tk.Text(self.main_frame)
        self.text1.configure(height='10', width='100')
        self.text1.grid(column='0', columnspan='5', padx='10', pady='10', row='3')
        self.main_frame.configure(height='200', width='500')
        self.main_frame.grid(column='0', padx='0', pady='0', row='0')

        # Main widget
        self.mainwindow = self.main_frame
    
    def run(self):
        self.mainwindow.mainloop()

    def start_button_pressed(self):
        pass

    def stop_button_pressed(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    app = NewprojectApp(root)
    app.run()


