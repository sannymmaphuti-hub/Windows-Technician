import psutil
import socket
import subprocess
import ipaddress


# ==========================================================
# Windows Technician v0.3
# NETWORK DIAGNOSTIC ENGINE
# ==========================================================


# ==========================================================
# IP CLASSIFICATION
# ==========================================================

def classify_ipv4(ip):

    try:

        address = ipaddress.ip_address(ip)

    except ValueError:

        return "INVALID"

    if address.is_loopback:

        return "LOOPBACK"

    if address.is_link_local:

        return "APIPA"

    if address.is_private:

        return "PRIVATE"

    return "PUBLIC"


# ==========================================================
# NETWORK ADAPTERS
# ==========================================================

def get_network_adapters():

    adapters = []

    interfaces = psutil.net_if_addrs()
    statistics = psutil.net_if_stats()

    for name, addresses in interfaces.items():

        stats = statistics.get(name)

        if stats is None:
            continue

        adapter = {
            "name": name,
            "is_up": stats.isup,
            "speed_mbps": stats.speed,
            "addresses": []
        }

        for address in addresses:

            family = address.family

            if family == socket.AF_INET:

                address_type = "IPv4"

            elif family == socket.AF_INET6:

                address_type = "IPv6"

            elif (
                hasattr(socket, "AF_LINK")
                and family == socket.AF_LINK
            ):
                address_type = "MAC"

            elif family == -1:
                address_type = "MAC"

            else:
                address_type = str(family)

            address_record = {
                "type": address_type,
                "address": address.address,
                "netmask": address.netmask,
                "broadcast": address.broadcast
            }

            if address_type == "IPv4":

                address_record["classification"] = (
                    classify_ipv4(address.address)
                )

            adapter["addresses"].append(
                address_record
            )

        adapters.append(adapter)

    return adapters


# ==========================================================
# VALID IPv4 ADDRESS
# ==========================================================

def get_valid_ipv4(adapter):

    for address in adapter["addresses"]:

        if address["type"] != "IPv4":
            continue

        classification = address.get(
            "classification"
        )

        if classification in (
            "PRIVATE",
            "PUBLIC"
        ):

            return address["address"]

    return None


# ==========================================================
# ACTIVE NETWORK ADAPTER
# ==========================================================

def get_active_adapter(adapters):

    for adapter in adapters:

        if not adapter["is_up"]:
            continue

        ip = get_valid_ipv4(adapter)

        if ip:

            return adapter

    return None


# ==========================================================
# DEFAULT GATEWAY
# ==========================================================

def get_default_gateway():

    try:

        result = subprocess.run(
            [
                "powershell",
                "-Command",
                (
                    "Get-NetRoute "
                    "-DestinationPrefix '0.0.0.0/0' "
                    "| Where-Object {$_.NextHop -ne '0.0.0.0'} "
                    "| Sort-Object RouteMetric "
                    "| Select-Object -First 1 -ExpandProperty NextHop"
                )
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        gateway = result.stdout.strip()

        if gateway:

            return gateway

    except (
        subprocess.SubprocessError,
        OSError
    ):

        pass

    return None


# ==========================================================
# PING TEST
# ==========================================================

def ping_host(host):

    try:

        result = subprocess.run(
            [
                "ping",
                "-n",
                "1",
                "-w",
                "2000",
                host
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        return result.returncode == 0

    except (
        subprocess.SubprocessError,
        OSError
    ):

        return False


# ==========================================================
# DNS TEST
# ==========================================================

def test_dns_resolution(
    hostname="www.microsoft.com"
):

    try:

        socket.gethostbyname(
            hostname
        )

        return True

    except (
        socket.gaierror,
        OSError
    ):

        return False


# ==========================================================
# INTERNET CONNECTIVITY
# ==========================================================

def test_internet_connectivity():

    return ping_host(
        "1.1.1.1"
    )


# ==========================================================
# NETWORK HEALTH
# ==========================================================

def determine_network_status(
    active_adapter,
    gateway,
    gateway_reachable,
    internet_reachable,
    dns_working
):

    if active_adapter is None:

        return "CRITICAL"

    if (
        not internet_reachable
        and not dns_working
    ):

        return "WARNING"

    if internet_reachable and dns_working:

        return "HEALTHY"

    if internet_reachable or dns_working:

        return "ATTENTION"

    if gateway and not gateway_reachable:

        return "WARNING"

    return "ATTENTION"


# ==========================================================
# NETWORK DIAGNOSIS
# ==========================================================

def diagnose_network():

    adapters = get_network_adapters()

    active_adapter = get_active_adapter(
        adapters
    )

    gateway = get_default_gateway()

    gateway_reachable = False

    if gateway:

        gateway_reachable = ping_host(
            gateway
        )

    internet_reachable = (
        test_internet_connectivity()
    )

    dns_working = test_dns_resolution()

    network_status = determine_network_status(
        active_adapter,
        gateway,
        gateway_reachable,
        internet_reachable,
        dns_working
    )

    findings = []

    # ------------------------------------------------------
    # ADAPTER
    # ------------------------------------------------------

    if active_adapter:

        active_ip = get_valid_ipv4(
            active_adapter
        )

        findings.append({
            "severity": "INFO",
            "category": "NETWORK ADAPTER",
            "message": (
                f"Active network adapter detected: "
                f"{active_adapter['name']} "
                f"with IPv4 address {active_ip}."
            )
        })

    else:

        findings.append({
            "severity": "CRITICAL",
            "category": "NETWORK ADAPTER",
            "message": (
                "No active network adapter with a "
                "usable IPv4 address was detected."
            )
        })

    # ------------------------------------------------------
    # APIPA DETECTION
    # ------------------------------------------------------

    apipa_adapters = []

    for adapter in adapters:

        for address in adapter["addresses"]:

            if (
                address["type"] == "IPv4"
                and address.get("classification")
                == "APIPA"
            ):

                apipa_adapters.append(
                    adapter["name"]
                )

                break

    if apipa_adapters:

        findings.append({
            "severity": "INFO",
            "category": "APIPA",
            "message": (
                "One or more adapters have "
                "169.254.x.x link-local addresses: "
                + ", ".join(apipa_adapters)
                + "."
            )
        })

    # ------------------------------------------------------
    # GATEWAY
    # ------------------------------------------------------

    if gateway is None:

        if (
            internet_reachable
            and dns_working
        ):

            findings.append({
                "severity": "INFO",
                "category": "NETWORK GATEWAY",
                "message": (
                    "A default gateway was not identified "
                    "by the route query, but Internet and "
                    "DNS connectivity are working."
                )
            })

        else:

            findings.append({
                "severity": "WARNING",
                "category": "NETWORK GATEWAY",
                "message": (
                    "No default gateway was detected."
                )
            })

    elif gateway_reachable:

        findings.append({
            "severity": "INFO",
            "category": "NETWORK GATEWAY",
            "message": (
                f"Default gateway {gateway} "
                "is reachable."
            )
        })

    else:

        findings.append({
            "severity": "WARNING",
            "category": "NETWORK GATEWAY",
            "message": (
                f"Default gateway {gateway} "
                "is not reachable."
            )
        })

    # ------------------------------------------------------
    # INTERNET
    # ------------------------------------------------------

    if internet_reachable:

        findings.append({
            "severity": "INFO",
            "category": "INTERNET",
            "message": (
                "External network connectivity "
                "is available."
            )
        })

    else:

        findings.append({
            "severity": "WARNING",
            "category": "INTERNET",
            "message": (
                "External network connectivity "
                "could not be confirmed."
            )
        })

    # ------------------------------------------------------
    # DNS
    # ------------------------------------------------------

    if dns_working:

        findings.append({
            "severity": "INFO",
            "category": "DNS",
            "message": (
                "DNS hostname resolution "
                "is working."
            )
        })

    else:

        findings.append({
            "severity": "WARNING",
            "category": "DNS",
            "message": (
                "DNS hostname resolution failed."
            )
        })

    # ------------------------------------------------------
    # FINAL NETWORK STATUS
    # ------------------------------------------------------

    findings.append({
        "severity": (
            "INFO"
            if network_status == "HEALTHY"
            else "WARNING"
            if network_status in (
                "WARNING",
                "ATTENTION"
            )
            else "CRITICAL"
        ),
        "category": "NETWORK HEALTH",
        "message": (
            f"Overall network status: "
            f"{network_status}."
        )
    })

    return {
        "status": network_status,
        "adapters": adapters,
        "active_adapter": active_adapter,
        "gateway": gateway,
        "gateway_reachable": gateway_reachable,
        "internet_reachable": internet_reachable,
        "dns_working": dns_working,
        "findings": findings
    }


# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    print("==========================================")
    print("Windows Technician v0.3")
    print("NETWORK DIAGNOSTICS")
    print("==========================================")

    result = diagnose_network()

    print()
    print("Network Adapters")
    print("------------------------------------------")

    for adapter in result["adapters"]:

        print(
            f"Adapter : {adapter['name']}"
        )

        print(
            f"Status  : "
            f"{'UP' if adapter['is_up'] else 'DOWN'}"
        )

        print(
            f"Speed   : "
            f"{adapter['speed_mbps']} Mbps"
        )

        for address in adapter["addresses"]:

            classification = ""

            if address["type"] == "IPv4":

                classification = (
                    f" "
                    f"[{address.get('classification', 'UNKNOWN')}]"
                )

            print(
                f"    {address['type']} : "
                f"{address['address']}"
                f"{classification}"
            )

        print()

    print("Connectivity")
    print("------------------------------------------")

    active_adapter_name = (
        result["active_adapter"]["name"]
        if result["active_adapter"]
        else "None"
    )

    print(
        f"Active Adapter     : "
        f"{active_adapter_name}"
    )

    print(
        f"Default Gateway    : "
        f"{result['gateway'] or 'None'}"
    )

    print(
        f"Gateway Reachable  : "
        f"{'YES' if result['gateway_reachable'] else 'NO'}"
    )

    print(
        f"Internet Reachable : "
        f"{'YES' if result['internet_reachable'] else 'NO'}"
    )

    print(
        f"DNS Working        : "
        f"{'YES' if result['dns_working'] else 'NO'}"
    )

    print(
        f"Network Status     : "
        f"{result['status']}"
    )

    print()
    print("Network Findings")
    print("------------------------------------------")

    for finding in result["findings"]:

        print(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )
