import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, trapezoid

# ==========================================
# THE PYTHON "TYPE" (Mimics TRNSYS Structure)
# ==========================================
class Type_NanofluidGreenhouse:
    def __init__(self, name, thickness_mm):
        self.name = name
        
        # Geometry
        self.L, self.W, self.H = 0.8, 0.6, 0.5
        self.A_roof = self.L * self.W
        self.V_air = self.L * self.W * self.H
        self.A_wall = 2 * (self.L * self.H) + 2 * (self.W * self.H)
        
        # Air Properties
        self.rho_air = 1.2
        self.cp_air = 1005
        self.C_air = self.V_air * self.rho_air * self.cp_air
        
        # Heat Transfer Coefficients
        self.h_in = 5.0
        self.h_out_base = 10.0
        self.U_wall = 5.5
        self.U_soil = 2.0
        self.T_soil = 15.0
        self.ACH = 5.0
        self.V_dot = (self.ACH * self.V_air) / 3600
        
        # Nanofluid Properties
        self.thickness_mm = thickness_mm
        self.cp_fluid = 4000
        self.m_dot_fluid = 0.02 * thickness_mm 
        self.C_roof = 1000 * thickness_mm       
        
        # Spectral Data Setup
        self.wavelengths = np.linspace(350, 1600, 1000)
        self.solar_spectrum = np.where((self.wavelengths > 400) & (self.wavelengths < 700), 1.0, 0.6) 
        self.solar_spectrum[self.wavelengths > 1100] = 0.3 
        
        vis_trans = 0.85 - (thickness_mm * 0.005)
        nir_trans = 0.20 - (thickness_mm * 0.01)
        nanofluid_transmittance = np.where((self.wavelengths >= 400) & (self.wavelengths <= 780), vis_trans, nir_trans)
        
        total_energy = trapezoid(self.solar_spectrum, self.wavelengths)
        trans_energy = trapezoid(self.solar_spectrum * nanofluid_transmittance, self.wavelengths)
        
        self.fraction_transmitted = trans_energy / total_energy
        self.fraction_absorbed = 1.0 - self.fraction_transmitted

    def derivatives(self, t, y, inputs):
        T_in, T_roof = y
        T_out, I_solar, Wind, T_fluid_inlet = inputs['T_out'], inputs['Solar'], inputs['Wind'], inputs['T_fluid_inlet']
        
        h_out = self.h_out_base + 2.0 * Wind 
        Q_solar_roof = (I_solar * self.A_roof) * self.fraction_absorbed
        Q_solar_trans = (I_solar * self.A_roof) * self.fraction_transmitted
        
        Q_conv_in = self.h_in * self.A_roof * (T_roof - T_in)
        Q_conv_out = h_out * self.A_roof * (T_roof - T_out)
        Q_wall = self.U_wall * self.A_wall * (T_in - T_out)
        Q_soil = self.U_soil * self.A_roof * (T_in - self.T_soil)
        Q_vent = self.rho_air * self.cp_air * self.V_dot * (T_in - T_out)
        Q_fluid = self.m_dot_fluid * self.cp_fluid * (T_roof - T_fluid_inlet)
        
        dT_in_dt = (Q_solar_trans + Q_conv_in - Q_wall - Q_soil - Q_vent) / self.C_air
        dT_roof_dt = (Q_solar_roof - Q_conv_in - Q_conv_out - Q_fluid) / self.C_roof
        
        return [dT_in_dt, dT_roof_dt]

    def simulate(self, time_data, T_out_data, Solar_data, Wind_data):
        def ode_wrapper(t, y):
            inputs = {
                'T_out': np.interp(t, time_data, T_out_data),
                'Solar': np.interp(t, time_data, Solar_data),
                'Wind': np.interp(t, time_data, Wind_data),
                'T_fluid_inlet': self.T_soil
            }
            return self.derivatives(t, y, inputs)

        y0 = [15.0, 15.0]
        solution = solve_ivp(ode_wrapper, [0, max(time_data)], y0, t_eval=time_data, method='RK45')
        
        T_in_sim = solution.y[0]
        T_roof_sim = solution.y[1]
        Q_harvested = self.m_dot_fluid * self.cp_fluid * (T_roof_sim - self.T_soil)
        
        return T_in_sim, T_roof_sim, Q_harvested

# ==========================================
# EXECUTION SCRIPT
# ==========================================
if __name__ == "__main__":
    # Make sure you have the Excel file in the same folder if you run this!
    try:
        file_path = 'ClimateCropControl_Exp_v1.xlsx'
        df_out = pd.read_excel(file_path, sheet_name='Outdoor climate')
        df_in = pd.read_excel(file_path, sheet_name='Greenhouse climate')
        
        df_out = df_out[['Time', 'Air temperature [℃]', 'Shortwave radiation [W·m-2]', 'Wind speed\n[m·s-1]']].copy()
        df_in = df_in[['Time', 'Air temperature [℃]']].copy()
        df_out.columns = ['Time', 'T_out', 'Solar', 'Wind']
        df_in.columns = ['Time', 'T_in_measured']

        df_out['Time_hours'] = (df_out['Time'] - df_out['Time'].iloc[0]).dt.total_seconds() / 3600
        sim_length = 288 
        
        time_data = df_out['Time_hours'].values[:sim_length]
        T_out_data = df_out['T_out'].values[:sim_length]
        Solar_data = df_out['Solar'].values[:sim_length]
        Wind_data = df_out['Wind'].values[:sim_length]

        type_5mm = Type_NanofluidGreenhouse("Case_A_5mm", thickness_mm=5)
        type_10mm = Type_NanofluidGreenhouse("Case_B_10mm", thickness_mm=10)
        type_15mm = Type_NanofluidGreenhouse("Case_C_15mm", thickness_mm=15)

        print("Running simulations...")
        T_in_5, _, Q_harv_5 = type_5mm.simulate(time_data, T_out_data, Solar_data, Wind_data)
        T_in_10, _, Q_harv_10 = type_10mm.simulate(time_data, T_out_data, Solar_data, Wind_data)
        T_in_15, _, Q_harv_15 = type_15mm.simulate(time_data, T_out_data, Solar_data, Wind_data)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})

        ax1.plot(df_in['Time'].values[:sim_length], df_in['T_in_measured'].values[:sim_length], label='Measured Conventional', color='black', linewidth=2)
        ax1.plot(df_out['Time'].values[:sim_length], T_in_5, label='Nanofluid 5mm (Case A)', color='orange', linestyle='--')
        ax1.plot(df_out['Time'].values[:sim_length], T_in_10, label='Nanofluid 10mm (Case B)', color='green', linestyle='-.')
        ax1.plot(df_out['Time'].values[:sim_length], T_in_15, label='Nanofluid 15mm (Case C)', color='purple', linestyle=':')
        ax1.plot(df_out['Time'].values[:sim_length], T_out_data, label='Outdoor Temp', color='blue', alpha=0.2)
        ax1.set_title('Parametric Study: Greenhouse Indoor Temperature')
        ax1.set_ylabel('Temperature (°C)')
        ax1.legend()
        ax1.grid(True)

        ax2.plot(df_out['Time'].values[:sim_length], Q_harv_5, label='Heat Harvested (5mm)', color='orange', linestyle='--')
        ax2.plot(df_out['Time'].values[:sim_length], Q_harv_10, label='Heat Harvested (10mm)', color='green', linestyle='-.')
        ax2.plot(df_out['Time'].values[:sim_length], Q_harv_15, label='Heat Harvested (15mm)', color='purple', linestyle=':')
        ax2.set_title('Thermal Energy Harvested by Nanofluid (NIR Absorption)')
        ax2.set_xlabel('Time (Hours)')
        ax2.set_ylabel('Heat Rate (Watts)')
        ax2.legend()
        ax2.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        
    except FileNotFoundError:
        print("Excel file not found. Please place 'ClimateCropControl_Exp_v1.xlsx' in this folder to run the simulation.")