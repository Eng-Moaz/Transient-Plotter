import tkinter as tk
import math
from tkinter import ttk
from tkinter import messagebox
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


#********integration functions*********
#parallel RLC circuits
def dSdt_parallel(t, S, R, L, C, I_source):
    v_C, i_L = S
    # Add checks for R, L, C being zero if necessary
    dv_C_dt = (I_source - (v_C / R) - i_L) / C
    di_L_dt = v_C / L
    return [dv_C_dt, di_L_dt]

#series RLC circuits
def dSdt_series(t, S, R, L, C, V_source):
    i_L, v_C = S
    # Add checks for L, C being zero if necessary
    di_L_dt = (V_source - R * i_L - v_C) / L
    dv_C_dt = i_L / C
    return [di_L_dt, dv_C_dt]


#********Application's interface*********

window = tk.Tk()
window.title("RLC Simulator")


#Radio Button variables and functions
circuit_type_value = tk.StringVar()
transient_type_value = tk.StringVar()

def update_everything():
    circuit_t = circuit_type_value.get()
    transient_t = transient_type_value.get()
    if transient_t == "step":
        Source_entry.config(state=tk.NORMAL)
        if circuit_t == "series":
            Source_Label.config(text="Voltage Source(V): ")
        else:
            Source_Label.config(text="Current Source(A): ")
    else:
        Source_Label.config(text="No Source")
        Source_entry.config(state=tk.DISABLED)


#*****plotting function*****

def plot_the_function():
    # ****Variables declaration****
    capacitance_value = float(Capacitance_entry.get())
    inductance_value = float(Inductance_entry.get())
    resistance_values = list(map(float , Resistance_entry.get().split(',')))
    i0_value = float(I0_entry.get())
    v0_value = float(V0_entry.get())
    time_value = float(Time_entry.get())

    #damping factor and resonant frequency
    def print_type(resistance):
        alpha = 0
        omega = 1/math.sqrt(inductance_value * capacitance_value)
        if circuit_type_value.get() == "series":
            alpha = resistance / (2 * inductance_value)
        else:
            alpha = 1 / (2 * resistance * capacitance_value)
        if (alpha * alpha) > (omega * omega):
            print(f"circuit is overdamped at resistance {resistance} ohms")
        elif math.isclose(alpha * alpha, omega * omega):
            print(f"circuit is critically damped at resistance {resistance} ohms")
        else :
            print(f"circuit is underdamped at resistance {resistance} ohms")


    #setting the plot
    t_eval = np.linspace(0, time_value, 1000)
    t_span = (0, time_value)
    plt.figure(figsize=(8, 4))
    plt.style.use('seaborn-v0_8-darkgrid')

    #y_axis label
    y_data_label = ""

    #choosing the right integrating function
    if circuit_type_value.get() == "parallel":
        if transient_type_value.get() == "natural":
            for r in resistance_values:
                sol1 = solve_ivp(dSdt_parallel, t_span=t_span, t_eval=t_eval, args=(r , inductance_value , capacitance_value , 0), y0=[v0_value , i0_value])
                plt.plot(sol1.t * 1e6, sol1.y[0], label=f"v(t) at R = {r}")
                y_data_label = "Voltage (V)"
                print_type(r)
            print('\n')
        else:
            for r in resistance_values:
                sol1 = solve_ivp(dSdt_parallel, t_span=t_span, t_eval=t_eval,
                                 args=(r, inductance_value, capacitance_value, float(Source_entry.get())), y0=[v0_value, i0_value])
                plt.plot(sol1.t * 1e6, sol1.y[1] * 1e3, label=f"i(t) at R = {r}")
                y_data_label = "Current (mA)"
                print_type(r)
            print('\n')
    elif circuit_type_value.get() == "series":
        if transient_type_value.get() == "natural":
            for r in resistance_values:
                sol1 = solve_ivp(dSdt_series, t_span=t_span, t_eval=t_eval, args=(r , inductance_value , capacitance_value , 0), y0=[i0_value , v0_value])
                plt.plot(sol1.t * 1e6, sol1.y[0] * 1e3, label=f"i(t) at R = {r}")
                y_data_label = "Current (mA)"
                print_type(r)
            print('\n')
        else:
            for r in resistance_values:
                sol1 = solve_ivp(dSdt_series, t_span=t_span, t_eval=t_eval,
                                 args=(r, inductance_value, capacitance_value, float(Source_entry.get())), y0=[i0_value, v0_value])
                plt.plot(sol1.t * 1e6, sol1.y[1], label=f"v(t) at R = {r}")
                y_data_label = "Voltage (V)"
                print_type(r)
            print('\n')

    plt.xlabel("Time (µs)")
    plt.ylabel(y_data_label)
    plt.grid(True)
    plt.legend()
    plt.show()

#****elements instantiation and displaying****

#first row (Circuit type)
circuit_type_label = ttk.Label(window ,text="Circuit type: ")
circuit_type_label.grid(row = 0 , column = 0, padx=5, pady=2, sticky=tk.W)
parallel_Radio_button = ttk.Radiobutton(window ,text = "parallel" , variable = circuit_type_value , value = "parallel" , command = update_everything)
parallel_Radio_button.grid(row = 0 , column = 1, padx=5, pady=2, sticky=tk.W)
series_Radio_button = ttk.Radiobutton(window ,text = "series" , variable = circuit_type_value , value = "series" , command = update_everything)
series_Radio_button.grid(row = 0 , column = 2, padx=5, pady=2, sticky=tk.W)

#second row (Transient type)
transient_type_label = ttk.Label(window ,text="Transient type: ")
transient_type_label.grid(row = 1 , column = 0, padx=5, pady=2, sticky=tk.W)
natural_Radio_button = ttk.Radiobutton(window ,text = "natural" , variable = transient_type_value , value = "natural" , command = update_everything)
natural_Radio_button.grid(row = 1 , column = 1, padx=5, pady=2, sticky=tk.W)
step_Radio_button = ttk.Radiobutton(window ,text = "step" , variable = transient_type_value , value = "step" , command = update_everything)
step_Radio_button.grid(row = 1 , column = 2, padx=5, pady=2, sticky=tk.W)

#third row (L & C)
Inductance_Label = ttk.Label(window ,text = "Inductance(H): ")
Inductance_Label.grid(row = 2 , column = 0, padx=5, pady=2, sticky=tk.W)
Inductance_entry = ttk.Entry(window, width=15)
Inductance_entry.grid(row = 2 , column = 1, padx=5, pady=2, sticky=tk.W)
Capacitance_Label = ttk.Label(window ,text = "Capacitance(F): ")
Capacitance_Label.grid(row = 2 , column = 2, padx=5, pady=2, sticky=tk.W)
Capacitance_entry = ttk.Entry(window, width=15)
Capacitance_entry.grid(row = 2 , column = 3, padx=5, pady=2, sticky=tk.W)

#fourth row (R)
Resistance_Label = ttk.Label(window ,text = "Resistance(Ohm, comma-sep): ")
Resistance_Label.grid(row = 3 , column = 0, padx=5, pady=2, sticky=tk.W)
Resistance_entry = ttk.Entry(window)
Resistance_entry.grid(row = 3 , column = 1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=2)

#fifth row (initial conditions)
I0_Label = ttk.Label(window ,text = "iL(0) (A): ")
I0_Label.grid(row = 4 , column = 0, padx=5, pady=2, sticky=tk.W)
I0_entry = ttk.Entry(window, width=15)
I0_entry.grid(row = 4 , column = 1, padx=5, pady=2, sticky=tk.W)
V0_Label = ttk.Label(window ,text = "vC(0) (V): ")
V0_Label.grid(row = 4 , column = 2, padx=5, pady=2, sticky=tk.W)
V0_entry = ttk.Entry(window, width=15)
V0_entry.grid(row = 4 , column = 3, padx=5, pady=2, sticky=tk.W)

#sixth row (source and time)
Source_Label = ttk.Label(window ,text = "No Source")
Source_Label.grid(row = 5 , column = 0, padx=5, pady=2, sticky=tk.W)
Source_entry = ttk.Entry(window, width=15)
Source_entry.grid(row = 5 , column = 1, padx=5, pady=2, sticky=tk.W)
Time_Label = ttk.Label(window ,text = "T_end (s): ")
Time_Label.grid(row = 5 , column = 2, padx=5, pady=2, sticky=tk.W)
Time_entry = ttk.Entry(window, width=15)
Time_entry.grid(row = 5 , column = 3, padx=5, pady=2, sticky=tk.W)

#seventh row (run)
run_button = ttk.Button(window , width = 20 , text = "Run Simulation" , command = plot_the_function)
run_button.grid(row = 6 , column = 0 , columnspan = 4, padx=5, pady=10)

#Running the program
circuit_type_value.set("parallel")
transient_type_value.set("natural")
update_everything()
window.mainloop()
