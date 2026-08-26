# ==========================================
# WINDOWS TECHNICIAN v0.1
# NETWORK EVIDENCE COLLECTOR
# ==========================================

import socket
import psutil


class NetworkCollector:

    name = "Network Collector"
    category = "NETWORK"

    def collect(self):

        adapters = []

        for interface, addresses in psutil.net_if_addrs().items():

            for address in addresses:

                if address.family == socket.AF_INET:

                    adapters.append({
                        "name": interface,
                        "ip_address": address.address,
                        "netmask": address.netmask
                    })

        return {
            "adapters": adapters
        }