import threading


class Publisher(threading.Thread):
    def __init__(self, out_queue, mqtt_client, root_topic, stop_event):
        super().__init__()
        self.out_queue = out_queue
        self.client = mqtt_client
        self.root = root_topic
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                host = self.out_queue.get(timeout=1)
            except Exception:
                continue

            base_topic = f"{self.root}/{host.name}"
            self.client.publish(f"{base_topic}/status", host.status)

            if host.status == "reachable":
                self.client.publish(f"{base_topic}/delay", str(host.last_delay))
                self.client.publish(f"{base_topic}/last_seen", host.last_seen)

            for port, state in host.port_states.items():
                self.client.publish(f"{base_topic}/ports/{port}/state", state)

            self.out_queue.task_done()
