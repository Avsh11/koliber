import socket
import threading
import os
import time

#kody ansi - to wziete z internetu, po co? zeby sterowac terminalem bez bibliotek.
#gdzie zielony to kolor z perspektywy usera, czerwony - komunikat o odejsciu, zolty o dolaczeniu, reszta kolejno reset powrot do standardowych ustawien terminala, bold pogrubienie tekstu zeby zwiekszyc cyztelnosc, up przesuniecie o linie w gore zeby nadpisywac input
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"
UP = "\033[F"
CLEAR = "\033[K"

#zmienna globalna przechowujaca stan tozsamosci sesji
my_id = "???"

#funkcja dekoracyjna, rozpoznaje system operacyjny i czysci ekran/
def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
#wyswietlenie loga ascii: czym robione: https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type+&x=none&v=4&h=4&w=80&we=false
ASCII_LOGO = """
                          ,--,                                            
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
#tworzymy obiekt socketu i probojemy nawiazac sesji tcp z serwerem - socket.SOCK_STREAM TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.10.1', 55555))

#funkcja do odebrania watku odiborczego, musi dzialac rownolegle bo input() blokuje glowny program
def handle_messages():
    global my_id
    while True:
        try:
            #oczekujemy na dane przychodzace z serwera
            incoming_bytes = client.recv(1024)
            if not incoming_bytes:
                break
                
            message = incoming_bytes.decode('utf-8')
            
            #sprawdzamy czy otrzyywany ciag jest instrukcja sterujaca SET_ID
            if message.startswith("SET_ID:"):
                #wydobujemy id
                my_id = message.split(":")[1]
            #filtrujmey powiadomienie o dolaczeniu 
            elif "dolaczyl" in message:
                print("\r" + CLEAR + YELLOW + BOLD + message + RESET)
                print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)

            #filtrujemy powiadomienie o odejsciu -78line w serverpy
            elif "wyszedl" in message:
                print("\r" + CLEAR + RED + BOLD + message + RESET)
                print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)
            
            else:
                print("\r" + CLEAR + message)
                print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)
                
        except Exception as e:
            print("ERROR: odebranie wiadomosci" + str(e))
            break

#start watku, natomaist daemon = True gwarantuje ze watek zakonczy sie po zamknieciu okna
receive_handler = threading.Thread(target=handle_messages)
receive_handler.daemon = True
receive_handler.start()
#program wstrzymuje wykonanie dopoki zmienna my_id nie zostanie zaktualizowana przez watek po tym jak zrobi "handshake" z serwerem.
while my_id == "???":
    time.sleep(0.1)

#wywolujemy metode clear_console() do wykasowania terminala i wyswietlamy logo 
clear_console()
print(ASCII_LOGO)

while True:
    try:
        #znak zachety
        current_prompt = GREEN + "TY (ID-" + my_id + "): " + RESET
        user_input = input(current_prompt)
        #jak nacisniemy enter to terminal zostawia wpisany tekst potem uzwamy up i clear aby go wymazac i zastapic lepszym formatowaniem.
        if user_input:
            print(UP + "\r" + CLEAR + GREEN + "TY (ID-" + my_id + "): " + user_input + RESET)
            #wysylamy tekst zmieniony na strumein bajtow 
            client.send(user_input.encode('utf-8'))
            
    except Exception as e:
        #obsluga bledu jakby np zerwalo polaczenie z brama
        print("ERROR: blad wyslania " + str(e))
        break

client.close()