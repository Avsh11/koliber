import socket
import threading

def multiple_users(user, addr):
    while True:
        try:
            data = user.recv(1024)
            if not data:
                print(f"User has disconnected")
                break
            message = data.decode('utf-8')
            print(f"User message: {message}")
        except Exception as e:
            print(f"ERROR: {e}")
            break
    user.close()
#sockets/gniazda to nic innego jak punkty koncowe komunikacji
#internet socket i TCP czyli typ gniazda (UDP czy TCP), tworzymy obiekt
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rezewrwacja adresu (ubuntu server) i portu w tym przypadku 55555
server.bind(('192.168.10.1',55555))
#Tutaj wazne, maks 5 polaczen na raz
server.listen(2)
print("Server is working")
print("Waiting for user connection")
#server gniazdo jest tylko do akceptowania polaczen, zeby userzy mogli sobie gadac potrzeba juz osobnego gniazda tylko dla nich!!!
while True:
    user, addr = server.accept()
    print(f"User with address {addr} has connected")
    thread = threading.Thread(target=multiple_users, args=(user,addr))
    thread.start()

