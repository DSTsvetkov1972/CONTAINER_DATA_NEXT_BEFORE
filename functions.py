import pandas as pd
import ctypes
import os
from tqdm import tqdm
import dateutil
from dateutil.parser import parse
import datetime
import tkinter
from tkinter import filedialog
import pyperclip
from tkinter import messagebox
from clickhouse_driver import Client
from datetime import datetime
from params import *
from cryptography.fernet import Fernet
from colorama import init, Fore, Back, Style

def Get_clipboard(text_container):
    try:
        clipboard_content = pyperclip.paste()
    except:
        clipboard_content = '???'
        
    text_container.delete('1.0', tkinter.END)        
    text_container.insert("1.0", clipboard_content)     

def get_df_of_click(query: str):
        params = get_params()
        connection=Client(host   = params[0],
                        port     = params[1],
                        database = params[2],
                        user     = params[3],
                        password = params[4],
                        secure=True,verify=False)
        with connection:
            return connection.query_dataframe(query)
        
def execute_sql_click(query, operation_name = ''):
        try: 
            thread_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(Fore.YELLOW + f'Запущен процесс: {operation_name} - {thread_start_time}' + Fore.WHITE)  
            params = get_params()
            connection=Client(host   = params[0],
                            port     = params[1],
                            database = params[2],
                            user     = params[3],
                            password = params[4],
                            secure=True,verify=False)
            connection.execute(query)
            thread_finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(Fore.GREEN + f'Закончен процесс: {operation_name} (начали {thread_start_time}, закончили {thread_finish_time})' + Fore.WHITE)#, выполнялся {(thread_finish_time-thread_start_time).total_seconds()} секунд' + Fore.WHITE)
        except Exception as e:
            print(Fore.RED + f'Авария при выполнении: {operation_name}.\nОшибка:\n{e}' + Fore.WHITE)
            pass

def insert_from_csv(dwh_table_name,df, operation_name = 'Загружаем в таблицу audit.cvetkov_d_container_date_next_before данные из CSV'):
        try: 
            thread_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(Fore.YELLOW + f'Запущен процесс: {operation_name} - {thread_start_time}' + Fore.WHITE)  
            params = get_params()
            connection=Client(host   = params[0],
                            port     = params[1],
                            database = params[2],
                            user     = params[3],
                            password = params[4],
                            secure=True,
                            verify=False,
                            settings={'use_numpy': True})
            connection.insert_dataframe(f'INSERT INTO {dwh_table_name} VALUES', df)
            thread_finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(Fore.GREEN + f'Закончен процесс для: {operation_name} (начали {thread_start_time}, закончили {thread_finish_time})' + Fore.WHITE)#, выполнялся {(thread_finish_time-thread_start_time).total_seconds()} секунд' + Fore.WHITE)
        except Exception as e:
            print(Fore.RED + f'Авария при выполнении для: {operation_name}.\nОшибка:\n{e}' + Fore.WHITE)
            pass        
        
def keys(event): # Функция чтобы работала вставка из буфера в русской раскладке
    import ctypes
    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    if hex(pf(0)) == '0x4190419':
        keyboard_layout = 'ru'
    if hex(pf(0)) == '0x4090409':
        keyboard_layout = 'en'

    if keyboard_layout == 'ru':
        if event.keycode==86:
            event.widget.event_generate("<<Paste>>")
        elif event.keycode==67: 
            event.widget.event_generate("<<Copy>>")    
        elif event.keycode==88: 
            event.widget.event_generate("<<Cut>>")    
        elif event.keycode==65535: 
            event.widget.event_generate("<<Clear>>")
        elif event.keycode==65: 
            event.widget.event_generate("<<SelectAll>>")

def get_params():
        params = open(os.path.join('.config')).read()
        decoded_text = Fernet(b'lXgjsyWLG2R-nAWC1vBkz-FWFzeWFi-71rNMiO2ON40=').decrypt(params).decode('utf-8')
        return(decoded_text.split('\n'))
 
def get_last_version(label_get_new_version):
    sql = """
        SELECT 
            max(version) new_version,
            argMax(message,version) new_version_message
        FROM
            (SELECT 
                toInt64OrNull(
                    replace(
                        splitByChar('|',log_info )[1],
                        'version',
                        ''
                    )
                ) as version,
                splitByChar('|',log_info )[2] AS message
            FROM 
                audit._check_your_file 
            WHERE 
                log_info LIKE '%version%')
        """

    last_version_info = get_df_of_click(sql)
    #return(last_version_info)
    last_version_number  = last_version_info['new_version'][0]
    last_version_message = last_version_info['new_version_message'][0]

    if last_version_number > version:
        label_get_new_version.config(text = 'Версия %s доступна для скачивания'%last_version_number)
        label_get_new_version.bind('<Button-1>', lambda x:show_message(last_version_message))
    else:
        label_get_new_version.config(text = '')
        label_get_new_version.unbind('<Button-1>')

def connection_settings_file_creator(CLICK_HOST,
                                     CLICK_PORT,
                                     CLICK_DBNAME,
                                     CLICK_USER,
                                     CLICK_PWD,
                                     root,
                                     mainmenu,
                                     label_get_new_version):
    try: 
        #print('aaaa connection_settings_file_creator')
        connection=Client(host=CLICK_HOST,
                port = CLICK_PORT,
                database=CLICK_DBNAME,
                user=CLICK_USER,
                password=CLICK_PWD,
                secure=True,verify=False)
        #print('bbbb connection_settings_file_creator')        
        print(CLICK_HOST,
            CLICK_PORT,
            CLICK_DBNAME,
            CLICK_USER,
            CLICK_PWD,sep='\n')
        if connection.query_dataframe('SELECT 777 AS a')['a'][0] == 777:
            params = ('%s\n%s\n%s\n%s\n%s')%(CLICK_HOST,CLICK_PORT,CLICK_DBNAME,CLICK_USER,CLICK_PWD)
        with open (os.path.join('.config'),'wb') as config_file:
            encoded_text = Fernet(b'lXgjsyWLG2R-nAWC1vBkz-FWFzeWFi-71rNMiO2ON40=').encrypt(params.encode('utf-8'))
            config_file.write(encoded_text)
            # делаем файл с конфигурацией скрытым
            FILE_ATTRIBUTE_HIDDEN = 0x02
            SetFileAttributes = ctypes.windll.kernel32.SetFileAttributesW
            GetLastError = ctypes.windll.kernel32.GetLastError

            filename = ".config"
            if not SetFileAttributes(filename, FILE_ATTRIBUTE_HIDDEN):
                errcode = GetLastError()       
                print("Не удалось скрыть файл. Код ошибки: " + str(errcode))
            else:   
                print("Файл скрыт успешно.")            
        root.destroy() 
        Log_in_check(mainmenu, label_get_new_version)  
        """  
        messagebox.showinfo(MSG_BOX_TITLE, 'Удалось подключиться к DWH!')
        filemenu = tkinter.Menu(mainmenu, tearoff=0)
        filemenu.add_command(label="Проверить соединение", command = lambda: Log_in_check(root,mainmenu))
        filemenu.add_command(label="Сменить пользователя", command = lambda: Log_in(root,mainmenu))
        filemenu.add_command(label="Выйти", command = lambda: Log_out(root,mainmenu))
        mainmenu.delete(3)
        mainmenu.add_cascade(label=get_params()[3],menu = filemenu, foreground = 'green') 
        """
    except Exception as e:
        messagebox.showerror(MSG_BOX_TITLE, f'Не удалось подключиться к DWH!\n{e}\nПроверьте параметры и повторите попрытку!', parent = root)

def Log_in(mainmenu,label_get_new_version):
    def on_closing():
        mainmenu.entryconfig(3, state = 'normal')
        root.destroy()

    mainmenu.entryconfig(3, state = 'disabled')

    root = tkinter.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title(MSG_BOX_TITLE)
    root.geometry('720x264')

    label_font = 18
    label_width = 12
    label_height = 1
    label_anchor = 'e'

    text_font = 'Arial 16'
    text_width = 42
    text_height = 1

    r = 0
    label_0 = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text=' ')
    label_0.grid(row = r, column = 0, sticky = 'w' )

    r = 1
    label_host = tkinter.Label(root
                            #,bg="white"
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='HOST')
    label_host.grid(row = r, column = 0, sticky = 'w' )

    text_host = tkinter.Text(root
                            ,font = text_font                         
                            ,height = text_height  
                            ,width= text_width
                            ,fg = 'blue'
                            )
    text_host.grid(row=r,column=1, padx = 5, sticky = 'w' )
    text_host.bind("<Control-KeyPress>", keys)

    r = 2
    label_port = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='PORT')
    label_port.grid(row = r, column = 0, sticky = 'w')

    text_port = tkinter.Text(root
                            ,font = text_font                         
                            ,height = text_height  
                            ,width= text_width
                            ,fg = 'blue')
    text_port.grid(row=r,column=1, padx = 5, sticky = 'w')
    text_port.bind("<Control-KeyPress>", keys)

    r = 3
    label_dbname = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='DBNAME')
    label_dbname.grid(row = r, column = 0, sticky = 'w')

    text_dbname = tkinter.Text(root
                            ,font = text_font                         
                            ,height = text_height  
                            ,width= text_width
                            ,fg = 'blue')
    text_dbname.grid(row=r,column=1, padx = 5, sticky = 'w')
    text_dbname.bind("<Control-KeyPress>", keys)
    
    r = 4
    label_user = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='USER')
    label_user.grid(row = r, column = 0, sticky = 'w')

    text_user = tkinter.Text(root
                            ,font = text_font                         
                            ,height = text_height  
                            ,width= text_width
                            ,fg = 'blue')
    text_user.grid(row=r,column=1, padx = 5, sticky = 'w')
    text_user.bind("<Control-KeyPress>", keys) 
    
    r = 5
    label_password = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='PASSWORD')
    label_password.grid(row = r, column = 0, sticky = 'w')

    entry_password = tkinter.Entry(root
                            ,font = text_font                         
                            ,width= text_width
                            ,fg = 'blue'
                            ,show = "●"
                            )
    entry_password.grid(row=r,column=1, padx = 5, sticky = 'w')
    entry_password.bind("<Control-KeyPress>", keys)   
    
    r = 6
    label_3 = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text=' ')
    label_3.grid(row = r, column = 0, sticky = 'w')       
    
    r = 7
    button_start = tkinter.Button(root
                            ,text = 'Подключиться'
                            ,font = 'Arial 18'
                            ,bg = 'light grey'
                            ,fg = 'green'
                            ,width = 34
                            ,justify='center'
                            #,bg = 'grey'

                            ,command = lambda: connection_settings_file_creator(text_host.get('1.0',tkinter.END).strip(),
                                                                                text_port.get('1.0',tkinter.END).strip(),
                                                                                text_dbname.get('1.0',tkinter.END).strip(),
                                                                                text_user.get('1.0',tkinter.END).strip(),
                                                                                entry_password.get().strip(),
                                                                                root,
                                                                                mainmenu,
                                                                                label_get_new_version)              
                            )
    button_start.grid(row=r,column=1, rowspan=1, padx = 5, columnspan= 2, sticky='n')
    
    r = 8
    label_5 = tkinter.Label(root
                            #,bg="white"                                
                            ,height = label_height
                            ,width  = label_width 
                            ,font   = label_font
                            ,anchor = label_anchor
                            ,text='')
    label_5.grid(row = r, column = 0, sticky = 'w')

    root.mainloop()

def Log_in_check(mainmenu, label_get_new_version, show_message_if_ok = True):
    if not os.path.exists(os.path.join('.config')): 
        messagebox.showwarning(MSG_BOX_TITLE,'Подключитесь, пожалуйста!')
        #root.title(TK_TITLE)
        #filemenu = tkinter.Menu(mainmenu, tearoff=0)
        mainmenu.delete(3)
        mainmenu.add_command(label="Подключиться", command = lambda: Log_in(mainmenu,label_get_new_version), foreground='red')
        return False
    else:
        filemenu = tkinter.Menu(mainmenu, tearoff=0)
        filemenu.add_command(label="Проверить соединение", command = lambda: Log_in_check(mainmenu,label_get_new_version))
        filemenu.add_command(label="Сменить пользователя", command = lambda: Log_in(mainmenu,label_get_new_version))
        filemenu.add_command(label="Выйти", command = lambda: Log_out(mainmenu,label_get_new_version))
    params = get_params()
    #print(params)
    try:
        connection=Client(host=params[0],
                port = int(params[1]),
                database=params[2],
                user=params[3],
                password=params[4],
                secure=True,verify=False)
        """
        connection=Client(host='rc1a-rgjcum1ijv22bo62.mdb.yandexcloud.net',
                port = 9440,
                database='history',
                user='cvetkov_d',
                password='NdKVRepY1eUWq35Tk22d',
                secure=True,verify=False)
        """
        #print((params[0]),int(params[1]),params[2],params[3],params[4],sep='\n')  
        #print(connection.query_dataframe('SELECT 777 AS a')['a'][0])   
        
        if connection.query_dataframe('SELECT 777 AS a')['a'][0] == 777:
            #root.title(TK_TITLE + ' ' + params[3])  
            mainmenu.delete(3)
            mainmenu.add_cascade(label=get_params()[3],menu = filemenu, foreground = 'green')
            #get_last_version(label_get_new_version)
            if show_message_if_ok: 
                messagebox.showinfo(MSG_BOX_TITLE,"Соединение установлено!")
            return True
        else:
            mainmenu.delete(3)
            mainmenu.add_cascade(label=get_params()[3],menu = filemenu, foreground = 'red')
            messagebox.showerror(MSG_BOX_TITLE,"Нет соединения с базой данных!\nВозможно не работает интернет или проблемы на стороне сервера.")
            return False
    except Exception as e:
        mainmenu.delete(3)
        mainmenu.add_cascade(label=get_params()[3],menu = filemenu, foreground = 'red')         
        messagebox.showerror(MSG_BOX_TITLE,f"Непредусмотренная ошибка соединения с базой данных!\n{e}")    
        return False

def Log_out(mainmenu, label_get_new_version):
    if os.path.exists(os.path.join('.config')):
        os.remove(os.path.join('.config')) 
        #print(dir(mainmenu))
        mainmenu.delete(3)
        mainmenu.add_command(label="Подключиться", command = lambda: Log_in(mainmenu, label_get_new_version), foreground='red')
        messagebox.showwarning(MSG_BOX_TITLE,'Вы вышли из аккаунта!')        
    else:
        messagebox.showwarning(MSG_BOX_TITLE,'А Вы и не были подключены!')

def show_message(message, root_geometry):
    root = tkinter.Tk()
    root.title(MSG_BOX_TITLE)
    root.geometry(root_geometry)


    developers_info_text = tkinter.Text(root,wrap=tkinter.WORD, padx=0)

    developers_info_text.bind("<Control-KeyPress>", keys)
    developers_info_text.insert('1.0', message)
    developers_info_text.configure(state='disabled')
    developers_info_text.pack()
    root.mainloop() 

def preprocessing(df):
    '''
    Загружаем данные из экселя, проверяем корректность данных, создаём столбцы с исправленными значениями контейнера и даты
    '''

    df = df.fillna('') 
    df.index += 1
    df =  df.reset_index(names = 'source_row')
    df['source_row'] = df['source_row'].apply(str)

    #df.to_excel('AAA.xlsx')
    #print(df['container_number'])

    # Проверяем корректность входного файла
    print(Fore.MAGENTA + 'Проверяем корректность данных во входном файле...' + Fore.WHITE)
    err_list = []
    for i in tqdm(df.itertuples(), total=len(df)):
        source_row = i[1]
        container_number_raw = i[2]
        date_raw = i[3]
        if container_number_raw == '' or date_raw == '': 
            err_list.append(f'Cтрока {source_row}: пустые значения контенера или даты!')
            continue
        try:
            parse(str(date_raw))
        except dateutil.parser._parser.ParserError:
            err_list.append(f'Cтрока {source_row}: не удаётся преобразовать значение в дату!')
    if len(err_list) >0: 
        print('Следующие строки содержат ошибки:','\n'.join(err_list), sep = '\n')
        return False

    print(Fore.MAGENTA + 'Преобрабразуем даты в даты, чистим номера конейнеров...' + Fore.WHITE)
    df['container_number'] = df['container_number_raw'].map(lambda x: x.replace(' ','').upper())
    df['date'] = df['date_raw'].map(str).map(lambda x : parse(x)).map(str)
    df['date_raw'] = df['date_raw'].map(str)
    return df

def processing(mainmenu, label_get_new_version):
    if Log_in_check(mainmenu, label_get_new_version, show_message_if_ok = False):
        user_name = get_params()[3]
        file = filedialog.askopenfilename()
        print(Fore.CYAN + 'СТАРТОВАЛО ПАРСИРОВАНИЕ ДЛЯ:' + Fore.WHITE)
        print(file)

        try:
            print(Fore.MAGENTA + 'Считывыаем данные из исходного файла' + Fore.WHITE)
            df = pd.read_excel(file, header= None, names = ['container_number_raw','date_raw'])
        except ValueError:
            messagebox.showerror(MSG_BOX_TITLE,'Парсируемый файл должен быть в экселевском формате!')  
            print(Fore.RED + 'ПАРСИРОВАНИЕ НЕ СОСТОЯЛОСЬ ПО ПРИЧИНЕ НЕПРАВИЛЬНОГО ФОРМАТА ВХОДНОГО ФАЙЛА!\n\n' + Fore.WHITE)
            return         
        except Exception as e:
            messagebox.showerror(f'Непредвиденная ошибка выбора файла\n{e}\nОбратитесь к разработчикам!')
            print(Fore.RED + 'ПАРСИРОВАНИЕ НЕ СОСТОЯЛОСЬ ПО ПРИЧИНЕ НЕПРАВИЛЬНОГО ФОРМАТА ВХОДНОГО ФАЙЛА!\n\n' + Fore.WHITE)
            return
        dwh_table_name = f'audit.{user_name}_CONTAINER_DATA_NEXT_BEFORE'
        df = preprocessing(df)
        sql = f'''
        CREATE OR REPLACE TABLE {dwh_table_name}
        (source_row String,
        container_number_raw String,
        date_raw String,
        container_number String,
        `date` String
        )
        ENGINE = Memory()
        '''

        execute_sql_click(sql, operation_name = f'Создаём в DWH таблицу {dwh_table_name}')
        insert_from_csv(dwh_table_name,df, operation_name = f'Загружаем в таблицу {dwh_table_name} из CSV')

        sql = f'''
        CREATE OR REPLACE TABLE {dwh_table_name}
        ENGINE = Memory() AS
        (
        WITH
        SVOD AS ( 
        SELECT --TOP(10000)
            toInt32(source_row) AS source_row,
            container_number_raw,
            date_raw,
            container_number,
            toDateTime(`date`,'Europe/Moscow') AS `date`
        FROM 
            {dwh_table_name}
        --) SELECT * FROM SVOD			
        ),
        CITTRANS AS ( 
            SELECT 
                CITTRANS_OPER.mOprId,
                CITTRANS_OPER.KontOtprId,
                EsrOper,
                Nom_Vag,
                container_operation_code,
                shipment_document_number,
                Date_pop,
                container_number,
                `date`
            FROM 
                cittrans__container_oper_v3 AS CITTRANS_OPER
                LEFT JOIN SVOD ON SVOD.container_number = CITTRANS_OPER.container_number
            WHERE  
                CITTRANS_OPER.container_number IN (SELECT DISTINCT container_number FROM SVOD)
        --) SELECT * FROM CITTRANS WHERE container_number = 'TKRU4396050' AND Date_pop >= toDate('2022-01-26 15:55:00') --AND '2023-03-15'
        --
        --SELECT max(Date_pop) FROM cittrans__container_oper_v3  --WHERE container_number = 'TKRU4396050' 
        ),
        CITTRANS AS (
            SELECT 
                container_number,
                `date`,
                -----------------------------------------------------------------------------------------------------
                argMaxIf(mOprId                  , Date_pop, `date` >= Date_pop) AS mOprId_before,
                argMaxIf(KontOtprId              , Date_pop, `date` >= Date_pop) AS KontOtprId_before,
                argMaxIf(EsrOper                 , Date_pop, `date` >= Date_pop) AS EsrOper_before,			
                argMaxIf(Nom_Vag                 , Date_pop, `date` >= Date_pop) AS Nom_Vag_before,			
                argMaxIf(container_operation_code, Date_pop, `date` >= Date_pop) AS container_operation_code_before,					
                argMaxIf(shipment_document_number, Date_pop, `date` >= Date_pop) AS shipment_document_number_before,	
                argMaxIf(Date_pop                , Date_pop, `date` >= Date_pop) AS Date_pop_before,
                -----------------------------------------------------------------------------------------------------
                argMinIf(mOprId                  , Date_pop, `date` <= Date_pop) AS mOprId_after,
                argMinIf(KontOtprId              , Date_pop, `date` <= Date_pop) AS KontOtprId_after,
                argMinIf(EsrOper                 , Date_pop, `date` <= Date_pop) AS EsrOper_after,			
                argMinIf(Nom_Vag                 , Date_pop, `date` <= Date_pop) AS Nom_Vag_after,			
                argMinIf(container_operation_code, Date_pop, `date` <= Date_pop) AS container_operation_code_after,							
                argMinIf(shipment_document_number, Date_pop, `date` <= Date_pop) AS shipment_document_number_after,	
                argMinIf(Date_pop                , Date_pop, `date` <= Date_pop) AS Date_pop_after
            FROM 
                CITTRANS
            --WHERE 
            --	container_number = 'TKRU4396050'
            GROUP BY
                container_number,
                `date`
        --		) SELECT * FROM CITTRANS 
        ),
        CITTRANS AS ( 
            SELECT * /* 
                CITTRANS_OPER.*,
                CITTRANS_OTPR_BEFORE.FirstOperId AS FirstOperId_before,
                CITTRANS_OTPR_AFTER.FirstOperId AS FirstOperId_after	*/		
            FROM 
                CITTRANS AS CITTRANS_OPER
                ----------------------------------------------------------------------------------------------
                LEFT JOIN (
                    SELECT DISTINCT 
                        mOprId,KontOtprId,FirstOperId 
                    FROM 
                        cittrans__container_otpr_v3 
                    WHERE 
                        FirstOperId BETWEEN 12000000 AND 40000000 /*AND 
                        shipment_document_number IN  (SELECT DISTINCT container_operation_code_before FROM CITTRANS)*/
                    ) AS CITTRANS_OTPR_BEFORE 
                    ON CITTRANS_OPER.mOprId_before = CITTRANS_OTPR_BEFORE.mOprId AND CITTRANS_OPER.KontOtprId_before = CITTRANS_OTPR_BEFORE.KontOtprId
                ----------------------------------------------------------------------------------------------	
                LEFT JOIN (
                    SELECT DISTINCT 
                        mOprId,KontOtprId,FirstOperId 
                    FROM 
                        cittrans__container_otpr_v3 
                    WHERE 
                        FirstOperId BETWEEN 12000000 AND 40000000 /*AND 
                        shipment_document_number IN  (SELECT DISTINCT container_operation_code_after FROM CITTRANS)*/
                    ) AS CITTRANS_OTPR_AFTER
                    ON CITTRANS_OPER.mOprId_after = CITTRANS_OTPR_AFTER.mOprId AND CITTRANS_OPER.KontOtprId_after = CITTRANS_OTPR_AFTER.KontOtprId				
        --) SELECT * FROM CITTRANS
        ),
        OBRABOTKA AS (
        SELECT 
        *
        FROM 
            SVOD
            LEFT JOIN CITTRANS ON `CITTRANS_OPER.container_number` = `container_number` AND `CITTRANS_OPER.date` = `date`
        )
        SELECT 
        source_row,
        container_number_raw,
        date_raw,
        container_number,
        `date`,
        --`CITTRANS_OPER.container_number`,`CITTRANS_OPER.date`,`CITTRANS_OPER.mOprId_before`,`CITTRANS_OPER.KontOtprId_before`,
        `CITTRANS_OPER.EsrOper_before`                              AS `EsrOper_before`,
        `CITTRANS_OPER.container_operation_code_before`             AS `container_operation_code_before`,
        toTimezone(`CITTRANS_OPER.Date_pop_before`,'Europe/Moscow') AS `Date_pop_before`,
        `CITTRANS_OPER.shipment_document_number_before`             AS `shipment_document_number_before`,         
        `CITTRANS_OPER.Nom_Vag_before`                              AS `Nom_Vag_before`,
        `CITTRANS_OTPR_BEFORE.FirstOperId`                          AS `FirstOperId_before`,
            
        --`CITTRANS_OPER.mOprId_after`,`CITTRANS_OPER.KontOtprId_after`,
        `CITTRANS_OPER.EsrOper_after`                               AS `EsrOper_after`,
        `CITTRANS_OPER.container_operation_code_after`              AS `container_operation_code_after`,  
        toTimeZone(`CITTRANS_OPER.Date_pop_after`,'Europe/Moscow')  AS `Date_pop_after`,
        `CITTRANS_OPER.shipment_document_number_after`              AS `shipment_document_number_after`,         
        `CITTRANS_OPER.Nom_Vag_after`                               AS `Nom_Vag_after`,
        `CITTRANS_OTPR_AFTER.FirstOperId`                           AS `FirstOperId_after`	
        --`CITTRANS_OTPR_BEFORE.mOprId`,`CITTRANS_OTPR_BEFORE.KontOtprId`,
        --`CITTRANS_OTPR_AFTER.mOprId`,`CITTRANS_OTPR_AFTER.KontOtprId`,
        FROM 
        OBRABOTKA
        )	
        '''
        execute_sql_click(sql, operation_name = f'Подтягиваем до и после к таблице {dwh_table_name}')

        print(Fore.CYAN + 'ПАРСИРОВАНИЕ ЗАВЕРШЕНО!\n\n' + Fore.WHITE)
    else:
        print(Fore.RED + 'ПАРСИРОВАНИЕ НЕ СОСТОЯЛОСЬ ПО ПРИЧИНЕ ОТСУТСТВИЯ СОЕДИНЕНИЯ С DWH!\n\n' + Fore.WHITE)