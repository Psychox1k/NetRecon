import asyncio

async def fetch_banner(target_host: str, target_port: int = 80) -> dict:
    writer = None
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                target_host,
                target_port
            ),
            timeout=3
        )
        try:
            banner = await asyncio.wait_for(reader.read(1024), timeout=2)
            if banner:
                return {
                    "port": target_port,
                    "status": "OPEN",
                    "service_name": "Unknown",
                    "raw_banner": banner.decode(errors="ignore").strip()
                }

        except asyncio.TimeoutError:
            pass

        try:
            payload = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )
            writer.write(payload.encode())

            await writer.drain()
            data = await asyncio.wait_for(reader.read(1024), timeout=3.0)
            if data:

                return {
                    "port": target_port,
                    "status": "OPEN",
                    "service_name": "Unknown",
                    "raw_banner": data.decode(errors="ignore").strip()
                }
            return {
                "port": target_port,
                "status": "OPEN_BUT_SILENT",
                "service_name": None,
                "raw_banner": None
            }

        except asyncio.TimeoutError:
            return {
                "port": target_port,
                "status": "TIMEOUT",
                "service_name": None,
                "raw_banner": None
            }

    except Exception as e:
        return {
            "port": target_port,
            "status": "Error",
            "service_name": None,
            "raw_banner": str(e)
        }

    finally:
        if writer:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionResetError, BrokenPipeError, OSError):
                pass