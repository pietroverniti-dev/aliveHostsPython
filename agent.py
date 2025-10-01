import threading
import queue
import socket
from multiping import MultiPing
from host import Host


class Agent(threading.Thread):
    def __init__(self, in_queue, out_queue, stop_event):
        super().__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                host = self.in_queue.get(timeout=1)
                self.in_queue.task_done()
            except queue.Empty:
                continue

            reachable, delay = self.ping_host(host.address)
            port_results = self.check_ports(host.address, host.ports)

            host.update_status(reachable, delay, port_results)
            self.out_queue.put(host)

    def ping_host(self, address):
        try:
            mp = MultiPing([address])
            mp.send()
            responses, no_responses = mp.receive(1.0)
            if address in responses:
                return True, responses[address]
        except Exception as e:
            print(f"[Ping error] {address}: {e}")
        return False, None

    def check_ports(self, address, ports):
        result = {}
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.25)
            try:
                s.connect((address, port))
                result[port] = "open"
            except Exception:
                result[port] = "closed"
            finally:
                s.close()
        return result
