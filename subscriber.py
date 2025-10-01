import paho.mqtt.client as mqtt

host_states = {}


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker.")
    client.subscribe("Verniti/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"[MQTT] {topic}: {payload}")

    parts = topic.split('/')
    if len(parts) < 3:
        return

    _, hostname, field = parts[0], parts[1], parts[2]
    state = host_states.setdefault(hostname, {"ports": {}})

    if field == "status":
        old_status = state.get("status")
        state["status"] = payload
        if payload == "unreachable" and old_status != "unreachable":
            print(f"[ALERT] Host {hostname} is unreachable!")
            # QUI puoi aggiungere invio email o telegram
    elif field == "delay":
        state["delay"] = float(payload)
    elif field == "last_seen":
        state["last_seen"] = payload
    elif field == "ports" and len(parts) == 5:
        port = int(parts[3])
        state["ports"][port] = payload


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.hivemq.com", 1883)
    client.loop_forever()


if __name__ == "__main__":
    main()
