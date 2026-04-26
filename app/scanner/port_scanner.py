import asyncio
import logging

from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6
from scapy.sendrecv import sr1

import ipaddress
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
SEM = asyncio.Semaphore(200)


async def syn_scan(target_ip: str, target_port: int) -> int | None:
    loop = asyncio.get_running_loop()

    pkt = None

    try:
        ip_obj = ipaddress.ip_address(target_ip)
    except ValueError:
        return None

    if ip_obj.version == 4:
        pkt = IP(dst=target_ip) / TCP(dport=target_port, flags="S")
    elif ip_obj.version == 6:
        pkt = IPv6(dst=target_ip) / TCP(dport=target_port, flags="S")

    async with SEM:
        response = await loop.run_in_executor(None, lambda: sr1(pkt, timeout=1, verbose=0))

    if response and response.haslayer(TCP):
        flag = response.getlayer(TCP).flags
        if flag == 0x12:
            return target_port

    return None


async def scan_ports(target_ip: str, ports: list[int]) -> list[int]:
    tasks = [syn_scan(target_ip, p) for p in ports]
    raw_results = await asyncio.gather(*tasks)
    open_ports = [p for p in raw_results if p is not None]

    return open_ports
#
#
# if __name__ == "__main__":
#     async def test():
#         ip = "8.8.8.8"
#         test_ports = [21, 22, 53, 80, 443, 8080]
#
#         print(f"Starting scan {ip}...")
#         open_ports = await scan_ports(ip, test_ports)
#         print(f"Open: {open_ports}")
#
#
#     asyncio.run(test())