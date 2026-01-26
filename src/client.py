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
#lista pomocnicza do przetrzymania historii rozmowy zeby nie zamazalo jej przy czyszczeniu ekranu
history_buffer = []

#funkcja dekoracyjna, rozpoznaje system operacyjny i czysci ekran/
def decoration():
    if os.name == 'nt':
        #Wlaczenie kolorow ANSI na windows 11 konieczne zeby nie bylo dziwnych znakow.
        os.system('')
        os.system('cls')
    else:
        os.system('clear')
#wyswietlenie loga ascii: czym robione: https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type+&x=none&v=4&h=4&w=80&we=false
ASCII_LOGO = r"""
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

#czy chcemy nowa sesje czy przywracamy ta starego id 
print("--- KOLIBER ---")
choice = input("Czy chcesz rozpoczac nowa sesje? (T/N): ").upper().strip()

#tworzymy obiekt socketu i probojemy nawiazac sesji tcp z serwerem - socket.SOCK_STREAM TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.10.1', 55555))

#informujemy serwer co wybralsmy na samym poczatku komunikacji
if choice == "T" or choice == "":
    client.send("NEW".encode('utf-8'))
else:
    #strip usuwa spacje, upper robi duze litery
    old_id = input("Podaj swoje stare ID sesji: ").upper().strip()
    if old_id == "":
        client.send("NEW".encode('utf-8'))
    else:
        client.send(("OLD:" + old_id).encode('utf-8'))

#funkcja do odebrania watku odiborczego, musi dzialac rownolegle bo input() blokuje glowny program
def handle_messages():
    global my_id
    while True:
        try:
            #oczekujemy na dane przychodzace z serwera - zwiekszylem bufor dla historii
            received_bytes = client.recv(4096)
            if not received_bytes:
                break
                
            #dekodujemy i rozbijamy pakiety po znaku nowej linii
            raw_data = received_bytes.decode('utf-8')
            messages = raw_data.split('\n')
            
            for msg in messages:
                if not msg: continue

                #sprawdzamy czy otrzyywany ciag jest instrukcja sterujaca SET_ID
                if msg.startswith("SET_ID:"):
                    #wydobujemy id
                    my_id = msg.split(":")[1].strip()
                
                #odbieranie archiwalnych wiadomosci powiazanych z naszym id
                elif msg.startswith("HIST:"):
                    #zapisujemy do bufora zamiast od razu drukowac (zeby logo nie zamazalo)
                    history_buffer.append(msg.replace("HIST:", "").strip())

                #filtrujmey powiadomienie o dolaczeniu 
                elif "dolaczyl" in msg:
                    print("\r" + CLEAR + YELLOW + BOLD + msg + RESET)
                    print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)

                #filtrujemy powiadomienie o odejsciu -78line w serverpy
                elif "wyszedl" in msg:
                    # --- NAPRAWIONO BLAD: msg zamiast message ---
                    print("\r" + CLEAR + RED + BOLD + msg + RESET)
                    print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)
                
                else:
                    #Zwykla wiadomosc od innego usera- \r i flush naprawiaja laga na windows
                    print("\r" + CLEAR + msg)
                    print(GREEN + "TY (ID-" + my_id + "): " + RESET, end="", flush=True)
                
        except Exception as e:
            print("ERROR: odebranie wiadomosci " + str(e))
            break

#start watku, natomaist daemon = True gwarantuje ze watek zakonczy sie po zamknieciu okna
receive_handler = threading.Thread(target=handle_messages)
receive_handler.daemon = True
receive_handler.start()

#program wstrzymuje wykonanie dopoki zmienna my_id nie zostanie zaktualizowana przez watek po tym jak zrobi "handshake" z serwerem.
while my_id == "???":
    time.sleep(0.1)

#wywolujemy metode decoration() do wykasowania terminala i wyswietlamy logo 
decoration()
print(ASCII_LOGO)

#jesli serwer przyslal nam historie to ja wypisujemy w ramce
if history_buffer:
    print(YELLOW + "--- PRZYWROCONA HISTORIA CZATU ---" + RESET)
    for h in history_buffer:
        # --- KOLOROWANIE HISTORII: Sprawdzamy czy to moje stare wiadomosci ---
        if ("#" + my_id + ":") in h:
            print(GREEN + h + RESET)
        else:
            print(h)
    print(YELLOW + "----------------------------------" + RESET)

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