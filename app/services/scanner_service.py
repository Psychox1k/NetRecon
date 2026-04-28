import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database.models import DomainModel, TargetModel, IPAddressModel, PortModel, SSLCertificateModel
from database.models.domain import StatusDomain
from database.models.port import PortStatus

logger = logging.getLogger(__name__)

class ScanService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _parse_port_status(status: str | None) -> PortStatus:
        if not status:
            return PortStatus.CLOSED

        status_upper = status.strip().upper()

        if status_upper == "OPEN":
            return PortStatus.OPEN
        elif status_upper in ["TIMEOUT", "FILTERED"]:
            return PortStatus.FILTERED
        else:
            return PortStatus.CLOSED

    async def save_scan_results(
            self,
            target_name: str,
            domain_name: str,
            scan_data: dict
    ) -> DomainModel:
        try:
            result = await self.db.execute(
                select(TargetModel).where(TargetModel.name == target_name)
            )
            target = result.scalar_one_or_none()

            if not target:
                target = TargetModel(name=target_name)
                self.db.add(target)
                await self.db.flush()

            result = await self.db.execute(
                select(DomainModel).where(DomainModel.domain_name == domain_name)
            )
            domain = result.scalar_one_or_none()

            if not domain:
                domain = DomainModel(
                    domain_name=domain_name,
                    target_id=target.id,
                    status=StatusDomain.ACTIVE
                )
                self.db.add(domain)
                await self.db.flush()
            else:
                domain.status = StatusDomain.ACTIVE

            ips_list = scan_data.get("ips", [])
            for ip_data in ips_list:
                ip_str = ip_data.get("ip")
                if not ip_str:
                    continue

                query = await self.db.execute(
                    select(IPAddressModel).where(
                        IPAddressModel.ip == ip_str,
                        IPAddressModel.domain_id == domain.id
                    )
                )
                ip_model = query.scalar_one_or_none()

                if not ip_model:
                    ip_model = IPAddressModel(
                        ip=ip_str,
                        version=ip_data.get("version", "IPv4" if "." in ip_str else "IPv6"),
                        domain_id=domain.id,
                    )
                    self.db.add(ip_model)
                    await self.db.flush()

                await self.db.execute(
                    delete(PortModel).where(
                    PortModel.ip_id == ip_model.id
                    )
                )

                await self.db.execute(
                    delete(SSLCertificateModel).where(
                        SSLCertificateModel.ip_id == ip_model.id
                    )
                )
                await self.db.flush()

                open_ports = ip_data.get("open_ports", [])
                for port in open_ports:
                    port_model = PortModel(
                        port_number=port.get("port"),
                        service_name=port.get("service_name"),
                        status=self._parse_port_status(port.get("status")),
                        banner=port.get("raw_banner"),
                        ip_id=ip_model.id
                    )
                    self.db.add(port_model)

                ssl_info = ip_data.get("ssl_cert", {})
                if ssl_info and isinstance(ssl_info, dict) and ssl_info.get("status") == "SUCCESS":
                    ssl_cert_model = SSLCertificateModel(
                        serial_number=ssl_info.get("serial_number"),
                        public_key=ssl_info.get("public_key"),
                        issuer=ssl_info.get("issuer"),
                        subject=ssl_info.get("subject"),
                        not_before=ssl_info.get("not_before"),
                        not_after=ssl_info.get("not_after"),
                        subdomains=ssl_info.get("subdomains", []),
                        ip_id=ip_model.id
                    )
                    self.db.add(ssl_cert_model)
            await self.db.commit()
            return domain

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error saving scan data for {domain_name}: {e}")
            raise e