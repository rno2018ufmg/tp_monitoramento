from collections import deque
from time import sleep
import time
from typing import List
from threading import Lock

from tqdm import tqdm
import dearpygui.dearpygui as dpg

class Logger:
    def __init__(self):
        self.Temperature: deque[float] = deque(maxlen=100)
        self.Voltage: deque[float] = deque(maxlen=100)
        self.mutex = Lock()
        self.active = True
        self.temp_lower: float = 0.0
        self.temp_upper: float = 1.0
        self.temp_alert: float = 0.8
        self.temp_alert_enabled = False
        self.voltage_lower: float = 0.0
        self.voltage_upper: float = 1.0
        self.voltage_alert: float = 0.8
        self.volt_alert_enabled = False
        self.ok_color = [0,255,0,255]
        self.warning_color = [255,0,0,255]
        self.elapsedTime: deque[int] = deque(maxlen=100)
        for i in range(100):
            self.elapsedTime.append(i+1)
            self.Voltage.append(0)
            self.Temperature.append(0)
        

    def shutdown(self):
        self.mutex.acquire()
        self.active = False
        self.mutex.release()

    def set_temp_limits(self, lower: float, upper: float, alert: float):
        self.temp_lower = lower
        self.temp_upper = upper
        self.temp_alert = alert

    def set_voltage_limits(self, lower: float, upper: float, alert: float):
        self.voltage_lower = lower
        self.voltage_upper = upper
        self.voltage_alert = alert

    def push_temperature(self, value: float):
        self.mutex.acquire()
        if(value > self.temp_alert):
            print("High Temperature")
        self.Temperature.append(value)
        self.mutex.release()

    def push_voltage(self, value: float):
        self.mutex.acquire()
        if(value > self.voltage_alert):
            print("High Voltage")
        self.Voltage.append(value)
        self.mutex.release()

    def update_data(self):
        dpg.configure_item('comp_voltage', x=list(self.elapsedTime), y=list(self.Voltage))
        dpg.configure_item('comp_temp', x=list(self.elapsedTime), y=list(self.Temperature))

    def print_infos(self):
        dpg.create_context()

        with dpg.window(label="Tutorial"):
            
            with dpg.plot(label="Voltage Plot", height=240, width=600):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes
                dpg.add_plot_axis(dpg.mvXAxis, label="last 100 samples")
                dpg.add_plot_axis(dpg.mvYAxis, label="Chip Voltage", tag="volt_y_axis")
            
                dpg.set_axis_limits("volt_y_axis", self.voltage_lower - 0.1, self.voltage_upper + .1)
                # series belong to a y axis
                dpg.add_line_series(list(self.elapsedTime), list(self.Voltage), label="Component Voltage", parent="volt_y_axis", tag="comp_voltage")


            with dpg.plot(label="Temperature Plot", height=240, width=600):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes
                dpg.add_plot_axis(dpg.mvXAxis, label="last 100 samples")
                dpg.add_plot_axis(dpg.mvYAxis, label="Chip Temperature", tag="temp_y_axis")
                dpg.set_axis_limits("temp_y_axis", self.temp_lower - 0.1, self.temp_upper + .1)
                # series belong to a y axis
                dpg.add_line_series(list(self.elapsedTime), list(self.Temperature), label="Component Temperature", parent="temp_y_axis", tag="comp_temp")

        dpg.create_viewport(title='Custom Title', width=1440, height=810)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            self.update_data()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()
