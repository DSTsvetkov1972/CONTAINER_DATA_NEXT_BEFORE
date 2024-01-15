from functions import *
from colorama import init, Fore, Back, Style
import tkinter 
from functions import *
from params import *

"""
# предлагаем залогиниться
if not os.path.exists(os.path.join('.config','.config')): 
    messagebox.showwarning(MSG_BOX_TITLE,'Залогиньтесь, пожалуйста!')
    Log_in(TK_TITLE)
"""
# 
root = tkinter.Tk()
TK_TITLE = MSG_BOX_TITLE  + ' запущено из: ' + os.path.join(os.path.abspath(os.curdir))

root.title(TK_TITLE)
root.geometry('%sx120'%(840 if len(os.path.abspath(os.curdir)) <= 80 else int(840/80*len(os.path.abspath(os.curdir)))))

mainmenu = tkinter.Menu(root)

#print(dir(mainmenu))

#--------------------------------------------



label_font = 14
label_width = 6
label_height = 1
label_anchor = 'e'

text_font = 'Arial 16'
text_width = 16
text_height = 1

r = 0
label_0 = tkinter.Label(root
                        #,bg="white"                                
                        ,height = label_height
                        ,width  = label_width 
                        ,font   = label_font
                        ,anchor = label_anchor
                        ,text= '')
label_0.grid(row = r, column = 0, sticky = 'w' )

r = 1
button_start = tkinter.Button(root
                        ,text = 'Парсировать данные'
                        ,font = 'Arial 18'
                        ,bg = 'light grey'
                        ,fg = 'green'
                        ,width = 24
                        ,justify='center'
                        #,bg = 'grey'
                        ,command = lambda: processing(mainmenu, label_get_new_version)
                        )
button_start.grid(row=r,column=0,  padx = 5,  sticky='nw')
r = 2
label_1 = tkinter.Label(root
                        #,bg="white"                                
                        ,height = label_height
                        ,width  = label_width 
                        ,font   = label_font
                        ,anchor = label_anchor
                        ,text= '')
label_1.grid(row = r, column = 0)#, sticky = 'center' )
r = 3

label_get_new_version = tkinter.Label(root
                        ,fg='red'                                
                        ,height = label_height
                        ,width  = label_width*10
                        ,font   = 'Arial 10 underline'
                        ,anchor = 'w'
                        ,text= '')

label_get_new_version.grid(row = r, column = 0, sticky = 'w', padx= 10 )


root.config(menu=mainmenu)

mainmenu.add_command(label='Инструкция'            , command = lambda: show_message(instruction_message,'520x390'))
mainmenu.add_command(label='Контакты разработчиков', command = lambda: show_message(developers_message,'420x160'))
mainmenu.add_command(label="Подключиться"          , command = lambda: Log_in(mainmenu,label_get_new_version), foreground='red')

Log_in_check(mainmenu,label_get_new_version)

root.mainloop()
init(); print(Style.BRIGHT)
#print(DT.datetime.strptime('01-01-2022 0:0:0.0', '%d-%m-%Y %H:%M:%S.%f'))