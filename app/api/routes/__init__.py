"""
API Routes Package
"""
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

# Import all route modules
try:
    from . import ai, auth, customers, deals, email, facebook_ads, reports, webhooks, whatsapp
    
    # Include all routers
    api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
    api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
    api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])
    api_router.include_router(email.router, prefix="/email", tags=["Email"])
    api_router.include_router(facebook_ads.router, prefix="/facebook-ads", tags=["Facebook Ads"])
    api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
    api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
    api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
except ImportError as e:
    import logging
    logging.warning(f"Some API routes could not be imported: {e}")

__all__ = ["api_router"]
