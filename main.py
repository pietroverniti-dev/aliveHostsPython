import json
import time
import queue
import threading
from host import Host           # Classe che rappresenta un host da monitorare
from agent import Agent         # Thread che esegue controlli sugli host
from publisher import Publisher # Thread che pubblica i risultati via MQTT
import paho.mqtt.client as mqtt # Libreria per la comunicazione MQTT

# Carica la configurazione da file JSON
def load_config(path="config.json"):
    with open(path, 'r') as f:
        return json.load(f)

# Crea oggetti Host a partire dai dati di configurazione
def create_hosts(config):
    return [Host(h["name"], h["address"], h["ports"]) for h in config["hosts"]]

def main():
    # Lettura parametri principali dalla configurazione
    config = load_config()
    interval = config.get("interval_sec")               # Frequenza di controllo degli host
    root_topic = config["mqtt"]["root_topic"]           # Topic MQTT base
    num_agents = config.get("num_agents")               # Numero di thread Agent da avviare

    # Code per la comunicazione tra thread e segnale di arresto
    in_queue = queue.Queue()        # Host da controllare
    out_queue = queue.Queue()       # Risultati da pubblicare
    stop_event = threading.Event()  # Flag per terminare i thread

    # Inizializzazione client MQTT
    mqtt_client = mqtt.Client()
    mqtt_client.connect(config["mqtt"]["broker"], config["mqtt"]["port"])
    mqtt_client.loop_start()       # Avvia il loop MQTT in background

    # Avvio del thread Publisher per inviare i risultati via MQTT
    publisher = Publisher(out_queue, mqtt_client, root_topic, stop_event)
    publisher.start()

    # Avvio dei thread Agent per elaborare gli host
    agents = []
    for _ in range(num_agents):
        agent = Agent(in_queue, out_queue, stop_event)
        agent.start()
        agents.append(agent)

    # Creazione degli host da monitorare
    hosts = create_hosts(config)

    try:
        # Ciclo principale: inserisce gli host nella coda a intervalli regolari
        while True:
            print("Queueing hosts for check...")
            for host in hosts:
                in_queue.put(host)  # Inserisce ogni host nella coda per essere elaborato
            time.sleep(interval)   # Attende prima di ripetere il ciclo
    except KeyboardInterrupt:
        # Arresto ordinato in caso di interruzione manuale (Ctrl+C)
        print("Stopping all threads...")
        stop_event.set()          # Segnala ai thread di terminare
        publisher.join()          # Attende la fine del thread Publisher
        for agent in agents:
            agent.join()          # Attende la fine di ogni thread Agent
        mqtt_client.loop_stop()   # Ferma il loop MQTT
        mqtt_client.disconnect()  # Disconnette il client MQTT
        print("Shutdown complete.")

# Avvio del programma
if __name__ == "__main__":
    main()
