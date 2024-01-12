from functions import *
from colorama import init, Fore, Back, Style

init(); print(Style.BRIGHT)
#print(DT.datetime.strptime('01-01-2022 0:0:0.0', '%d-%m-%Y %H:%M:%S.%f'))

#########################################################################
#########################################################################
file = 'real_case_1000000.xlsx'                                      
user_name = get_params()[3]                                          
#########################################################################
#########################################################################


processing(user_name, file)	