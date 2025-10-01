from datetime import datetime

class Host:
    def __init__(self, name, address, ports):
        self.name = name
        self.address = address
        self.ports = ports  # list of ports to check
        self.status = "unknown"  # "reachable" or "unreachable"
        self.last_seen = None
        self.last_delay = None  # ping round-trip time
        self.port_states = {}  # port number → "open"/"closed"

    def update_status(self, reachable, delay, port_results):
        self.status = "reachable" if reachable else "unreachable"
        if reachable:
            self.last_seen = datetime.utcnow().isoformat()
            self.last_delay = delay
        self.port_states = port_results

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "status": self.status,
            "last_seen": self.last_seen,
            "last_delay": self.last_delay,
            "ports": self.port_states,
        }
