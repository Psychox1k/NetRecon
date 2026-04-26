import asyncio
import socket


async def get_domain_ip_address(domain: str) -> dict:
    loop = asyncio.get_running_loop()
    try:
        result = await loop.getaddrinfo(host=domain, port=None, family=socket.AF_UNSPEC)


        ipv4_addresses = []
        ipv6_addresses = []

        for res in result:
            family = res[0]
            sockaddr = res[4]
            ip = sockaddr[0]

            if family == socket.AF_INET and ip not in ipv4_addresses:
                ipv4_addresses.append(ip)
            elif family == socket.AF_INET6 and ip not in ipv6_addresses:
                ipv6_addresses.append(ip)


        return {
            "domain": domain,
            "ipv4": ipv4_addresses,
            "ipv6": ipv6_addresses,
            "status": "success",
            "error": None
        }


    except socket.gaierror as e:

        return {
            "domain": domain,
            "ipv4": [],
            "ipv6": [],
            "status": "failed",
            "error": str(e)
        }

# Testing
if __name__ == "__main__":
    res = asyncio.run(get_domain_ip_address("www.google.com"))
    print(res)