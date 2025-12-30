"""
OmniCRM Integrations Module
Complete integrations for Facebook Ads and WhatsApp Business API
"""
from .facebook_ads_integration import (
    FacebookAdsIntegration,
    CampaignObjective,
    AdPlacement
)
from .whatsapp_integration import (
    WhatsAppBusinessIntegration,
    MessageType,
    MessageStatus
)

__all__ = [
    "FacebookAdsIntegration",
    "CampaignObjective",
    "AdPlacement",
    "WhatsAppBusinessIntegration",
    "MessageType",
    "MessageStatus"
]
