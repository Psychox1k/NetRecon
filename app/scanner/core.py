from scanner import get_domain_ip_address, scan_ports, fetch_banner, fetch_ssl_certificate
import logging
logger = logging.getLogger(__name__)

import asyncio

async def scan_target(target_domain: str, target_ports: list[int] = None) -> dict:
    default_ports = [21, 22, 80, 443, 3306, 5432, 8080]
    ports_to_scan = target_ports if target_ports else default_ports

    dns_result = await get_domain_ip_address(target_domain)

    if dns_result["error"] is not None:
        logger.error(f"Domain: {target_domain} has bad name or doesn't exist")
        return {
            "domain": target_domain,
            "status": "FAILED",
            "error": dns_result["error"],
            "ips": []
        }



    final_report = {
        "status": "SUCCESS",
        "domain": target_domain,
        "ips": []

    }


    for ip in dns_result["ipv4"]:
        ip_report = {
            "ip": ip,
            "open_ports": [],
            "ssl_cert": None
        }

        open_ports = await scan_ports(ip, ports_to_scan)

        if open_ports:
            banner_tasks = [fetch_banner(ip, port) for port in open_ports]
            banner_results = await asyncio.gather(*banner_tasks)

            ip_report["open_ports"] = banner_results

            if 443 in open_ports:
                ip_report["ssl_cert"] = await fetch_ssl_certificate(target_domain, 443)

        final_report["ips"].append(ip_report)

    for ipv6 in dns_result["ipv6"]:
        ipv6_report = {
            "ip": ipv6,
            "version": "ipv6",
            "open_ports": [],
            "ssl_cert": None
        }

        open_ports = await scan_ports(ipv6, ports_to_scan)

        if open_ports:
            banner_tasks = [fetch_banner(ipv6, port) for port in open_ports]
            banner_results = await asyncio.gather(*banner_tasks)

            ipv6_report["open_ports"] = banner_results

            if 443 in open_ports:
                ip_report["ssl_cert"] = await fetch_ssl_certificate(target_domain, 443)

        final_report["ips"].append(ipv6_report)


    return final_report


if __name__ == "__main__":
    async def test():

        res = await scan_target("google.com")
        import json
        print(json.dumps(res, indent=4, ensure_ascii=False))

    asyncio.run(test())

