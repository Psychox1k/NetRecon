import asyncio
import ssl
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

def parse_raw_certificate(cert_bytes):
    cert = x509.load_der_x509_certificate(cert_bytes)
    subject = cert.subject.rfc4514_string()
    issuer = cert.issuer.rfc4514_string()


    valid_from = cert.not_valid_before_utc
    valid_until = cert.not_valid_after_utc
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        domains = ext.value.get_values_for_type(x509.DNSName)

    except x509.ExtensionNotFound:
        domains = []

    return [subject, issuer, valid_from, valid_until, domains]



async def fetch_ssl_certificate(target_host: str, target_port: int) -> dict:
    writer = None

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                target_host,
                target_port,
                ssl=ctx,
                server_hostname=target_host
            ), timeout=3.0
        )

        print(f"Established connection with {target_host}:{target_port}")

        ssl_object = writer.get_extra_info("ssl_object")

        cert = ssl_object.getpeercert(binary_form=True)
        print(f"Size of certificate:{len(cert)} bytes")


        subject, issuer, valid_from, valid_until, domains = parse_raw_certificate(cert)

        return {
            "port": target_port,
            "status": "SUCCESS",
            "subject": subject,
            "issuer": issuer,
            "not_before": valid_from.isoformat(),
            "not_after": valid_until.isoformat(),
            "subdomains": domains,
            "error": None
        }
    except asyncio.TimeoutError:
        return {
            "port": target_port,
            "status": "TIMEOUT",
            "subject": None,
            "issuer": None,
            "not_before": None,
            "not_after": None,
            "subdomains": [],
            "error": "Connection Timeout"
        }

    except Exception as e:
        return {
            "port": target_port,
            "status": "Error",
            "subject": None,
            "issuer": None,
            "not_before": None,
            "not_after": None,
            "subdomains": [],
            "error": str(e)
        }
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()