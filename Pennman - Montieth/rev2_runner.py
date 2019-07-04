import gross_ref_evapo_transp_func
import crop_coeff_func
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
Rh_max = 0.0
Rh_min = 0.0
T_mean = 0.0
slight_duration = 0.0
wind_vel = 0.0
ud_un_ratio = 0.0
latitude = 0.0
longitude = 0.0
altitude = 0.0
month = 0
day_number = 0
crop_id = 0
irrig_freq = 0
Rh_mean = 0.0

def get_live_weather(day_number):
    farmer1_name = 'Mulay'
    farmer2_name = 'P.B.Shinde'
    farmer = farmer2_name
    if(day_number <= 14):
        data_prev = pd.read_csv('data_farmer/' + farmer + '/' + 'april.csv')
        data = pd.read_csv('data_farmer/' + farmer + '/' + 'may.csv')
    elif(day_number <= 44):
        data_prev = pd.read_csv('data_farmer/' + farmer + '/' + 'may.csv')
        data = pd.read_csv('data_farmer/' + farmer + '/' + 'june.csv')
        day_number -= 14
    elif(day_number <= 75):
        data_prev = pd.read_csv('data_farmer/' + farmer + '/' + 'june.csv')
        data = pd.read_csv('data_farmer/' + farmer + '/' + 'july.csv')
        day_number -= 44
    elif(day_number <= 106):
        data_prev = pd.read_csv('data_farmer/' + farmer + '/' + 'july.csv')
        data = pd.read_csv('data_farmer/' + farmer + '/' + 'august.csv')
        day_number -= 75
    elif(day_number <= 123):
        data_prev = pd.read_csv('data_farmer/' + farmer + '/' + 'august.csv')
        data = pd.read_csv('data_farmer/' + farmer + '/' + 'september.csv')
        day_number -= 106
    else:
        print("Day Number out-of-bounds")

    data_days_prev = data_prev[pd.isnull(data_prev).any(axis=1)]
    temp_max_month_prev = np.average(data_days_prev.iloc[:,1:2].values)
    temp_min_month_prev = np.average(data_days_prev.iloc[:,3:4].values)
    temp_month_prev = (temp_max_month_prev + temp_min_month_prev)/2.0
    data_days = data[pd.isnull(data).any(axis=1)]
    data_days = data.loc[data['FeelsLikeC'] != data['FeelsLikeC']]
    temp_max_month = np.average(data_days.iloc[:,1:2].values)
    temp_min_month = np.average(data_days.iloc[:,3:4].values)
    temp_month = (temp_max_month + temp_min_month)/2.0

    data_hours = data.loc[data['FeelsLikeC'] == data['FeelsLikeC']]
    data_thatday = data_hours.iloc[8*(day_number-1):8*(day_number),:]
    temp_max = np.max(data_thatday.iloc[:,2:3].values)
    temp_min = np.min(data_thatday.iloc[:,2:3].values)
    temp_mean = np.average(data_thatday.iloc[:,2:3].values)
    u_night_mean = (np.sum(data_thatday.iloc[0:2,5:6].values.astype(float)) + np.sum(data.iloc[6:8,5:6].values.astype(float)))*12.0
    u_day_mean = np.average(data_thatday.iloc[2:6,5:6].values.astype(float))*24.0
    #print(u_day_mean,u_night_mean)
    wind_mean = (u_day_mean + u_night_mean)/2.0
    rel_humid_mean = np.average(data_thatday.iloc[:,13:14].values)
    rel_humid_max = np.max(data_thatday.iloc[:,13:14].values)
    rel_humid_min = np.min(data_thatday.iloc[:,13:14].values)
    timestr_rise = str(data_days.iloc[day_number-1:day_number,5:6].values[0][0])
    hs = float(timestr_rise[0:2])
    ms = float(timestr_rise[3:5])
    tps = 0
    if(timestr_rise[6] == 'P'):
        tps = 12
    time_frac_rise = hs + ms/60.0 + tps
    timestr_fall = str(data_days.iloc[day_number-1:day_number,6:7].values[0][0])
    hf = float(timestr_fall[0:2])
    mf = float(timestr_fall[3:5])
    tpf = 0
    if(timestr_fall[6] == 'P'):
        tpf = 12
    time_frac_fall = hf + mf/60.0 + tpf
    slight = time_frac_fall - time_frac_rise
    return [temp_max,temp_min,temp_mean,temp_month,temp_month_prev],wind_mean,[rel_humid_max,rel_humid_mean,rel_humid_min],slight


    
    
def take_input():
    print('Enter latitude')
    print('Enter Altitude')
    print('Enter Crop ID')
    print('Enter available irrigation frequency eg. 2, 4, 7, 10, 20')

    latitude = float(input())
    altitude = float(input())
    crop_id = int(input())
    irrig_freq = int(input())
    return latitude,altitude,crop_id,irrig_freq

def take_csv():
    input_data = pd.read_csv('input_file.csv')
    print(input_data)
    input_array = input_data.iloc[0:1,:].values.reshape(13)
    #print(input_array)
    Rh_max = input_array[0]
    Rh_min = input_array[1]
    T_mean = input_array[2]
    slight_duration = input_array[3]
    wind_vel = input_array[4]
    ud_un_ratio = input_array[5]
    latitude = input_array[6]
    longitude = input_array[7]
    altitude = input_array[8]
    month = int(input_array[9])
    day_number = int(input_array[10])
    crop_id = int(input_array[11])
    irrig_freq = int(input_array[12])
    Rh_mean = (Rh_max + Rh_min)/2.0
    return Rh_max,Rh_min,T_mean,slight_duration,wind_vel,ud_un_ratio,latitude,longitude,altitude,month,day_number,crop_id,irrig_freq,Rh_mean

def get_crop_name(crop_id):
    data = pd.read_csv('crop_id.csv')
    name = data.iloc[crop_id - 4,0]
    return name

def run_for_cycle():
    irrig = []
    ref_irrig = []
    coeff = []
    days = []
    latitude,altitude,crop_id,irrig_freq = take_input()
    wind_vel = 250*0.01157407407
    i = 1
    month = 5
    day_max_arr = [31,28,31,30,13,30,31,31,20,31,30,31]
    flag = 1
    crop_name = get_crop_name(crop_id)
    print("Crop Selected is : " + crop_name)
    while(i<=123):
        T_data,wind_vel,Rh_data,slight_duration = get_live_weather(i)
        wind_vel = wind_vel**0.01157407407
        ref_evapo_transp = gross_ref_evapo_transp_func.func_ref_evapo_transp(Rh_data,T_data,slight_duration,wind_vel,latitude,altitude,month)
        crop_coeff = crop_coeff_func.func_crop_coeff(irrig_freq,ref_evapo_transp,Rh_data[2],wind_vel,crop_id,i)
        irrigation_required = crop_coeff*ref_evapo_transp
        days.append(i)
        ref_irrig.append(ref_evapo_transp)
        coeff.append(crop_coeff)
        irrig.append(irrigation_required)
        if(flag > day_max_arr[month - 1]):
            print("##########################################################################################")
            print(month)
            print(day_max_arr[month - 1])
            flag = 1
            month +=1
        i+=1
        flag+=1
      

    irrig_hat = savgol_filter(irrig,27, 4)
    plt.plot(days,ref_irrig,label = 'Reference Irrigation')
    plt.grid()
    plt.legend()
    plt.show()
    plt.plot(days,coeff,label = 'Crop Coefficient')
    plt.grid()
    plt.legend()
    plt.show()
    plt.plot(days[0:20],irrig[0:20],label = 'Required Irrigation in Initial Phase')
    plt.plot(days[19:55],irrig[19:55],label = 'Required Irrigation in Crop Development Phase')
    plt.plot(days[54:95],irrig[54:95],label = 'Required Irrigation in Mid-Season Phase')
    plt.plot(days[94:123],irrig[94:123],label = 'Required Irrigation in Late Phase')
    
    plt.plot(days[0:20],irrig_hat[0:20],label = 'Smooth Irrigation in Initial Phase')
    plt.plot(days[19:55],irrig_hat[19:55],label = 'Smooth Irrigation in Crop Development Phase')
    plt.plot(days[54:95],irrig_hat[54:95],label = 'Smooth Irrigation in Mid-Season Phase')
    plt.plot(days[94:123],irrig_hat[94:123],label = 'Smooth Irrigation in Late Phase')
    plt.plot([14.5,14.5],[-20,20],'--',label = 'May - June Boundary')
    plt.plot([44.5,44.5],[-20,20],'--',label = 'June - July Boundary')
    plt.plot([75.5,75.5],[-20,20],'--',label = 'July - August Boundary')
    plt.plot([106.5,106.5],[-20,20],'--',label = 'August - September Boundary')
    plt.ylim(0,14)
    plt.grid()
    plt.legend()
    plt.show()
    print("AREA UNDER CURVES")
    print(np.sum(irrig))
    print(np.sum(irrig_hat))

    crop_name = get_crop_name(crop_id)
    print(crop_name)


    

run_for_cycle()