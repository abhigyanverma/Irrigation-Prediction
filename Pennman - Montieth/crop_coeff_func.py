import pandas as pd
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
def func_crop_coeff(irrig_freq_input,ref_evapo_transp,Rh_min,wind_vel,crop_id,day_number):
    irrig_freq = str(irrig_freq_input) + ' Days'
    table21 = pd.read_csv('Table_21.csv')
    if(Rh_min > 70):
        #print('Relative Humidity is high.')
        rel_table21 = table21.loc[table21['Rh Min.'] == 'High']
    else:
        #print("Relative Humidity is moderate.")
        rel_table21 = table21.loc[table21['Rh Min.'] == 'Moderate']
    if(wind_vel>5):
        #print('Wind Velocity is high.')
        rel_table21 = rel_table21.loc[rel_table21['Wind Speed'] == 'High']
    else:
        #print('Wind Velocity is moderate.')
        rel_table21 = rel_table21.loc[rel_table21['Wind Speed'] == 'Moderate']

    #print(rel_table21.columns[crop_id - 1])
    crop_coeff_3 = rel_table21[rel_table21.columns[crop_id - 1]].values[0]
    crop_coeff_4 = rel_table21[rel_table21.columns[crop_id - 1]].values[1]

    fig6 = pd.read_csv('figure_6_table.csv')
    #print(fig6[irrig_freq])
    fig6_x = fig6['ref_evapo_transp'].values.reshape(10)
    fig6_y = fig6[irrig_freq].values.reshape(10)
    fig6_i = interp1d(fig6_x,fig6_y,kind = 'linear')
    if(ref_evapo_transp > 10):
        print("EEEEEEEEEEEEEEEEEEEEEEEE_Et0_Warning")
        print(ref_evapo_transp)
        ref_evapo_transp = 10
    crop_coeff_1 = round(float(fig6_i(ref_evapo_transp)),2)
    crop_coeff_graph_data_x = [10,20,55,75,95,110]
    crop_coeff_graph_data_y = [crop_coeff_1,crop_coeff_1,crop_coeff_3,crop_coeff_3,crop_coeff_3,crop_coeff_4]
    crop_coeff_graph_data_y_poly_fit_obj = np.polyfit(crop_coeff_graph_data_x,crop_coeff_graph_data_y,4)
    crop_coeff_graph_data_y_poly_fit = np.poly1d(crop_coeff_graph_data_y_poly_fit_obj)
    #print(crop_coeff_graph_data_y_poly_fit(day_number))
    return crop_coeff_graph_data_y_poly_fit(day_number)

#func_crop_coeff(7,9.091,30,1.5,36,54)