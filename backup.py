import socket
import threading
import random
import string

#tablica przechowuje nam polaczonych userow
users = []

#funkcja sluzy do generowania losowego id 6 znakowego, zamiast tego aby user wpisywal swoj nickname. Podobnie jak dziala to na 4chanie na boardach /pol/, /int/. Stad tez uzycie biblioteki string.
def generate_id():
    #ABC + 123 itd.
    id_pool = string.ascii_uppercase + string.digits
    id_result = ""
    for i in range(6):
        char = random.choice(id_pool)
        id_result = id_result + char
    return id_result

def broadcast(message, sender):
    for user in users:
        if user != sender:
            try:
                user.send(message)
            except Exception as e:
                print(f"ERROR: {e}")
                if user in users: 
                    users.remove(user)

def handle_client(user, addr):
    session_id = generate_id()
    user.send(f"SET_ID:{session_id}".encode('utf-8'))
    
    while True:
        try:
            data = user.recv(1024)
            if not data: 
                break
            
            full_message = f"Anon#{session_id}: {data.decode('utf-8')}"
            broadcast(full_message.encode('utf-8'), user)
        except Exception as e:
            print(f"ERROR: {e}")
            break
            
    if user in users:
        users.remove(user)
    broadcast(f"ANON {session_id} HAS LEFT".encode('utf-8'), user)
    user.close()

#sockets/gniazda to nic innego jak punkty koncowe komunikacji
#internet socket i TCP czyli typ gniazda (UDP czy TCP), tworzymy obiekt
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rezewrwacja adresu (ubuntu server) i portu w tym przypadku 55555
server.bind(('192.168.10.1', 55555))
#Tutaj wazne, maks 5 polaczen na raz
server.listen(5)

while True:
    user, addr = server.accept()
    users.append(user)
    thread = threading.Thread(target=handle_client, args=(user, addr))
    thread.start()


import socket
import threading
import os
import shutil
import time

GREEN = "\033[92m"  
RED = "\033[91m"    
BOLD = "\033[1m"
UP_ONE = "\033[F"
CLEAR_LINE = "\033[K"

my_id = "???"

def decoration():
    os.system('cls' if os.name == 'nt' else 'clear')

title = """                          ,--,                                            
       ,--.  ,----..   ,---.'|                                            
   ,--/  /| /   /   \  |   | :      ,---,    ,---,.     ,---,.,-.----.    
,---,': / '/   .     : :   : |   ,`--.' |  ,'  .'  \  ,'  .' |\    /  \   
:   : '/ /.   /   ;.  \|   ' :   |   :  :,---.' .' |,---.'   |;   :    \  
|   '   ,.   ;   /  ` ;;   ; '   :   |  '|   |  |: ||   |   .'|   | .\ :  
'   |  / ;   |  ; \ ; |'   | |__ |   :  |:   :  :  /:   :  |-,.   : |: |  
|   ;  ; |   :  | ; | '|   | :.'|'   '  ;:   |    ; :   |  ;/||   |  \ :  
:   '   \.   |  ' ' ' :'   :    ;|   |  ||   :     \|   :   .'|   : .  /  
|   |    '   ;  \; /  ||   |  ./ '   :  ;|   |   . ||   |  |-,;   | |  \  
'   : |.  \   \  ',  / ;   : ;   |   |  ''   :  '; |'   :  ;/||   | ;\  \ 
|   | '_\.';   :    /  |   ,/    '   :  ||   |  | ; |   |    \:   ' | \.' 
'   : |     \   \ .'   '---'     ;   |.' |   :   /  |   :   .':   : :-'   
;   |,'      `---`               '---'   |   | ,'   |   | ,'  |   |.'     
'---'                                    `----'     `----'    `---'       
                                                                          
"""

user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user.connect(('192.168.10.1', 55555))

def receive():
    global my_id
    while True:
        try:
            message = user.recv(1024).decode('utf-8')
            
            if message.startswith("SET_ID:"):
                my_id = message.split(":")[1]
            
            elif message.startswith("LEFT:"):
                print(f"\r{CLEAR_LINE}{RED}{BOLD}{message}{RESET}")
                print(f"{GREEN}You (ID-{my_id}): {RESET}", end="", flush=True)
            
            else:
                print(f"\r{CLEAR_LINE}{message}")
                print(f"{GREEN}You (ID-{my_id}): {RESET}", end="", flush=True)
        except:
            break

threading.Thread(target=receive, daemon=True).start()

while my_id == "???":
    time.sleep(0.1)

decoration()
print(title)

while True:
    prompt = f"{GREEN}You (ID-{my_id}): {RESET}"
    text = input(prompt)
    
    if text:
        print(f"{UP_ONE}\r{CLEAR_LINE}", end="")
        width = shutil.get_terminal_size().columns
        my_msg = f"[TY]: {text}"
        print(f"{GREEN}{my_msg.rjust(width)}{RESET}")
        
        user.send(text.encode('utf-8'))
