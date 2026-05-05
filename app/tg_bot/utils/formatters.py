# app/tg_bot/utils/formatters.py
from app.database.models import DomainModel


def format_domain_results(domain: DomainModel) -> str:
    """Generates a beautiful HTML report for a scanned domain."""

    text = f"🌐 <b>Target Domain:</b> {domain.domain_name}\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if not domain.ips:
        text += "<i>No scan data available for this domain yet.</i>\n"
        text += "<i>Please trigger a new scan.</i>\n"
        return text

    for ip in domain.ips:
        text += f"📡 <b>Host IP:</b> <code>{ip.ip}</code>\n"

        if ip.ports:
            open_ports = [str(p.port_number) for p in ip.ports]
            text += (f"  ├ 🔓 <b>Open Ports:</b> "
                     f"<code>{', '.join(open_ports)}</code>\n")
        else:
            text += "  ├ 🔒 <i>No open ports detected.</i>\n"

        if ip.certificate:
            cert = ip.certificate
            text += "  └ 🔐 <b>SSL Certificate:</b>\n"

            issuer = cert.issuer[:35] + "..." if len(cert.issuer) > 35 else cert.issuer

            text += f"      • <b>Issuer:</b> {issuer}\n"
            text += f"      • <b>Expires:</b> {cert.not_after}\n"
        else:
            text += "  └ ⚠️ <i>No SSL certificate found.</i>\n"

        text += "\n"

    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "<i>⏱ Data is valid as of the last scan.</i>\n\n"
    text += "👇 <b>View full scan information below:</b>"

    return text
