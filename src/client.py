import socket

#to samo co na serwerze, tworzymy gniazdo dla usera i to samo, przez internet i protokol TCP lecimy i laczymy sie do serwera o adresie tym i tym. Dla UDP by bylo SOCK_DGRAM np.
user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user.connect(('192.168.10.1', 55555))

while True:
    text = input("Wyslij wiadomosc test:")
    user.send(text.encode('utf-8'))