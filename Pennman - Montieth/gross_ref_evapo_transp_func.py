import pandas as pd
import math
from scipy.interpolate import interp1d
def get_vap_press(T):
    T_deno = float(T) + 237.3
    T_ratio = 17.27*float(T)/T_deno
    val = 0.6108*math.exp(T_ratio)
    return val

def get_psycho_const(altitude):
    at_press = 101.3*(((293.0 - 0.0065*altitude)/293.0)**5.26)
    sp_heat = 1.013
    mol_wt = 0.622
    lat_heat_vap = 2.45
    psy_const = (sp_heat*at_press)/(mol_wt*lat_heat_vap*1000)
    return psy_const

def get_sigma_T4(T):
    T = T + 273.16
    sigma = 4.903*(10**(-9))
    val = sigma*(T**4)
    return val

def get_Ra(month,latitude,alph_month):
    table10 = pd.read_csv('Table_10.csv')
    table10_i = interp1d(table10['Latitude'].values.reshape(26),table10[alph_month[month - 1]].values.reshape(26),kind = 'linear')
    if(latitude <=50):
        #print("Taking Ra from Table 10")
        Ra = table10_i(latitude)
    else:
        print("ERROR : Ra can't be taken from Table 10")
    return Ra*2.45

def get_N(month,latitude,alph_month):
    table11 = pd.read_csv('Table_11.csv')
    table11_i = interp1d(table11['Latitude'].values.reshape(14),table11[alph_month[month - 1]].values.reshape(14),kind = 'linear')
    if(latitude <= 50):
        #print("Taking N from Table 11")
        N = table11_i(latitude)
    return N

def func_ref_evapo_transp(Rh_data,T_data,slight_dur,wind_vel_mps,latitude,altitude,month):
    #print(Rh_data,T_data,slight_dur,wind_vel_mps,latitude,altitude,month)
    Rh_max,Rh_mean,Rh_min = Rh_data[0] , Rh_data[1] , Rh_data[2]
    T_max,T_min,T_mean,T_month,T_prev_month = T_data[0] , T_data[1] , T_data[2] , T_data[3] , T_data[4]
    alph_month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    T_deno = float(T_mean) + 237.3

    #Algorithm
    delta = 4098*get_vap_press(T_mean)/(T_deno**2)
    psy_const = get_psycho_const(altitude)
    es = (get_vap_press(T_max) + get_vap_press(T_min))/2.0
    ea = ((get_vap_press(T_max)*Rh_min) + (get_vap_press(T_min)*Rh_max))/200.0
    #print(get_vap_press(T_max))
    #print(get_vap_press(T_min))
    N = get_N(month,latitude,alph_month)
    Ra = get_Ra(month,latitude,alph_month)
    Rs = (0.25 + 0.5*slight_dur/N)*Ra
    Rns = 0.77*Rs
    Rso = (0.75 + 2*(altitude)/100000)*Ra
    Rnl_fac1 = (get_sigma_T4(T_max) + get_sigma_T4(T_min))/2.0
    Rnl_fac2 = 0.34 - 0.14*math.sqrt(ea)
    Rnl_fac3 = (1.35*Rs/Rso) - 0.35
    Rnl = Rnl_fac1*Rnl_fac2*Rnl_fac3
    Rn = Rns - Rnl
    G = 0.14*(T_month - T_prev_month)
    ref_evapo_transp_fac1 = 0.408*delta*(Rn-G)/(delta + psy_const*(1 + 0.34*wind_vel_mps))
    ref_evapo_transp_fac2 = 900*psy_const*wind_vel_mps*(es - ea)/((delta + psy_const*(1 + 0.34*wind_vel_mps))*T_deno)
    ref_evapo_transp = ref_evapo_transp_fac1 + ref_evapo_transp_fac2
    #print(delta,psy_const,es,ea,Ra,N,Rs,Rns,Rso,Rnl_fac1,Rnl_fac2,Rnl_fac3,Rnl,Rn,G)
    #print(ref_evapo_transp)
    return ref_evapo_transp
