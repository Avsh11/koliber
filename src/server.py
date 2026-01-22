import socket
import threading
import random
import string

#na tej liscie przechowujemy obiekty gniazd socketow dla wszystkich aktywnych userow. Dzieki temu serwer wie do kogo rozsylac wiadomosci itd. 
user_sockets = []

#na tej liscie natomiast przechowujemy zajete IDki, zebysmy takiego samego nie dali dwom userom, mimo ze jest mala szansa na to.
assigned_id = []

#funckja generuje losowy 6 znakowy ciag - duze litery plus cyfry. Uzywamy moduul string.
def generate_id():
    pool = string.ascii_uppercase + string.digits
    id_result = ""
    #wiadomo stringa budujemy petla/ modul random 
    for i in range(6):
        char = random.choice(pool)
        id_result = id_result + char
    return id_result

#funkcja realizuje logike mostu/relay. Serwer iteruje po liscie aktuwnych socketow i przesyla dane. WAZNE - pominiecie sender_socket, czemu? zeby nadawaca nie otrzymal echa wlasnej wiadomosci
def handle_broadcast(message_bytes, sender_socket):
    for user_socket in user_sockets:
        if user_socket != sender_socket:
            try:
                #probojemy przeslac dane przez socketaw formie bajtow
                user_socket.send(message_bytes)
            except Exception as e:
                #jak sie nie uda to wywalamy socket w przypadku np zerwania polaczenia.
                print("ERROR: rozsylanie wiadomosci" + str(e))
                if user_socket in user_sockets:
                    user_sockets.remove(user_socket)

#funkcja do obslugi watku klienta, kazde polaczenie ma pracowac asynchronicznie, aby recv() nie lbokowalo serwra
def handle_client(user, client_address):
    #przydzielanie idka
    session_id = generate_id()
    #sprawdzamy czy wylosowane id nie jest zajete juz - bylo mowa na zajeciach zeby dodac do funkcji walidacje!!!!
    while session_id in assigned_id:
        session_id = generate_id()
    
    assigned_id.append(session_id)
    
    #Wysylamy informacje o przydzielonym id do usera!!!
    user.send(("SET_ID:" + session_id).encode('utf-8'))
    
    #info systemowe o nowym gosciu - po steonie usera
    handle_broadcast(("Uzytkownik o ID " + session_id + " dolaczyl.").encode('utf-8'), user)
    #info z poziomu serwera tez + z jakiego adresu sie polaczyl
    print("[UBUNTU]: Adres: " + str(client_address) + " ID: " + session_id + " dolaczyl. ")

    #petla nieskonczona while true zeby nasluchiwalo dane przychodzace z konkretnego socketa!!!!
    while True:
        try:
            #1024 rozmiar bufora
            data = user.recv(1024)
            #jesli klient wysle pusty pakiet oznacza to zadanie zamkniecia polaczenia juz. czyli jak np zamknie okno terminala
            if not data:
                break
            
            #tutaj formulowanie juz koncowego pakietu doklejamy id nadawcy do tresci waidomosci
            text = data.decode('utf-8')
            full_message = "Anon#" + session_id + ": " + text
            handle_broadcast(full_message.encode('utf-8'), user)
            
        except Exception as e:
            print("ERROR: uzytkownik " + session_id + " " + str(e))
            break

    print("[UBUNTU]: ID: " + session_id + " sie rozlaczyl. ")
    
    #zwalniamy zasoby, kasujemy dziada i usuwamy id jego z listy zajetych i jego gniazdo z aktywnych socketow
    if session_id in assigned_id:
        assigned_id.remove(session_id)
    if user in user_sockets:
        user_sockets.remove(user)
    
    #po stronie usera powiadomienie ze ten i ten o tym id wyszedl z sesji
    handle_broadcast(("Uzytkownik o ID " + session_id + " wyszedl.").encode('utf-8'), user)
    user.close()

#sockets/gniazda to nic innego jak punkty koncowe komunikacji
#internet socket i TCP czyli typ gniazda (UDP czy TCP), tworzymy obiekt
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#SO_REUSEADDR pozwala na natychmiastowe bindowanie portu po restarcie zapobiega błedowi TIME_WAIT
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#rezewrwacja adresu (ubuntu server) i portu w tym przypadku 55555
server_socket.bind(('192.168.10.1', 55555))
#Tutaj wazne, maks 5 polaczen na raz
server_socket.listen(5)

print("===== SERWER URUCHOMIONY =====")
#petla do akceptacji poaczen + odsylanie usera do osobnego watku
while True:
    #accept() bedzie tworzyc socket (conn) do rozmowy z userem konretnym
    conn, client_address = server_socket.accept()
    user_sockets.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, client_address))
    thread.start()