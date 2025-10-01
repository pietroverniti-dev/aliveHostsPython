import json
import time
import queue
import threading
from host import Host
from agent import Agent
from publisher import Publisher
import paho.mqtt.client as mqtt

# Funzione di caricamento dei dati dal file config.json
def load_config(path="config.json"):
    with open(path, 'r') as f:
        return json.load(f)

# Funzione per creazione di oggetti Host
def create_hosts(config):
    return [Host(h["name"], h["address"], h["ports"]) for h in config["hosts"]]


def main():
    config = load_config()
    interval = config.get("interval_sec")
    root_topic = config["mqtt"]["root_topic"]
    num_agents = config.get("num_agents")

    # Queues e stop signal
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    stop_event = threading.Event()

    # MQTT Client
    mqtt_client = mqtt.Client()
    mqtt_client.connect(config["mqtt"]["broker"], config["mqtt"]["port"])
    mqtt_client.loop_start()

    # Publisher thread
    publisher = Publisher(out_queue, mqtt_client, root_topic, stop_event)
    publisher.start()

    # Agent threads
    agents = []
    for _ in range(num_agents):
        agent = Agent(in_queue, out_queue, stop_event)
        agent.start()
        agents.append(agent)

    hosts = create_hosts(config)

    try:
        while True:
            print("Queueing hosts for check...")
            for host in hosts:
                in_queue.put(host)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping all threads...")
        stop_event.set()
        publisher.join()
        for agent in agents:
            agent.join()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
