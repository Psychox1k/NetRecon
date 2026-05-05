from fastapi import APIRouter
from app.routes.target import router as target_router
from app.routes.ip import router as ip_router
from app.routes.ssl_certificate import router as ssl_certificate_router
from app.routes.domain import router as domain_router
from app.routes.port import router as port_router

api_router = APIRouter()

api_router.include_router(target_router, prefix="/targets", tags=["targets"])
api_router.include_router(domain_router, prefix="/domains", tags=["domains"])
api_router.include_router(ip_router, prefix="/ips", tags=["ips"])
api_router.include_router(port_router, prefix="/ports", tags=["ports"])
api_router.include_router(ssl_certificate_router, prefix="/certificates", tags=["ssl"])