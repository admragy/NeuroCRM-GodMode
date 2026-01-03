"""
Gemini Live API Service
Real-time voice AI counselor with full CRM context and current deals
"""

import logging
from typing import Dict, Any, Optional
import asyncio
import websockets
import json

logger = logging.getLogger(__name__)


class GeminiLiveService:
    """
    Gemini Live API Integration
    
    OmniOracle: Voice AI with CRM Memory
    - Low-latency voice conversation
    - Full context of customer data and deals
    - Real-time advice and insights
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp",
        voice: str = "Aoede"
    ):
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.enabled = bool(api_key)
        self.websocket_url = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
        
        if self.enabled:
            logger.info(f"✅ Gemini Live Service initialized (model: {model}, voice: {voice})")
        else:
            logger.warning("⚠️ Gemini Live disabled - no API key")
    
    async def start_voice_session(
        self,
        user_id: str,
        crm_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start live voice session with OmniOracle
        
        Args:
            user_id: User initiating the session
            crm_context: Current CRM state (customers, deals, activities)
        
        Returns:
            session_id, websocket_url, configuration
        """
        if not self.enabled:
            return {
                "error": "Gemini Live not enabled",
                "enabled": False
            }
        
        try:
            session_id = f"LIVE-{user_id}-{int(asyncio.get_event_loop().time())}"
            
            # Prepare system prompt with CRM context
            system_prompt = self._build_system_prompt(crm_context)
            
            logger.info(f"🎙️ Starting Gemini Live session: {session_id}")
            
            return {
                "session_id": session_id,
                "websocket_url": f"{self.websocket_url}?key={self.api_key}",
                "model": self.model,
                "voice": self.voice,
                "system_prompt": system_prompt,
                "instructions": {
                    "1": "Connect to WebSocket URL",
                    "2": "Send audio stream (16kHz, mono, PCM)",
                    "3": "Receive real-time responses",
                    "4": "OmniOracle has full CRM context"
                },
                "enabled": True
            }
            
        except Exception as e:
            logger.error(f"Failed to start Gemini Live: {str(e)}")
            return {
                "error": str(e),
                "enabled": False
            }
    
    def _build_system_prompt(self, crm_context: Optional[Dict[str, Any]]) -> str:
        """Build system prompt with CRM context"""
        base_prompt = """You are OmniOracle, an AI advisor for OmniCRM Ultimate.

You have access to the user's CRM data and can provide insights about:
- Customer relationships and health scores
- Deal pipeline and opportunities
- Revenue forecasts
- Strategic recommendations

Always be concise, actionable, and business-focused.
"""
        
        if crm_context:
            context_summary = f"""
Current CRM State:
- Total Customers: {crm_context.get('total_customers', 0)}
- Active Deals: {crm_context.get('active_deals', 0)}
- Pipeline Value: ${crm_context.get('pipeline_value', 0):,.2f}
- Top Priority: {crm_context.get('top_priority', 'None')}
"""
            return base_prompt + context_summary
        
        return base_prompt
    
    async def send_audio_chunk(
        self,
        session_id: str,
        audio_data: bytes
    ) -> bool:
        """
        Send audio chunk to Gemini Live
        
        Note: Requires active WebSocket connection
        This is a simplified placeholder
        """
        try:
            # In production, maintain WebSocket connection
            logger.debug(f"📤 Sending audio chunk ({len(audio_data)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Audio send failed: {str(e)}")
            return False
    
    async def get_crm_context(self, user_id: str, db: Any) -> Dict[str, Any]:
        """
        Fetch current CRM context for user
        """
        try:
            from app.models.customer import Customer
            from app.models.deal import Deal
            from sqlalchemy import select, func
            
            # Get customer count
            customer_count = await db.scalar(select(func.count(Customer.id)))
            
            # Get active deals
            active_deals = await db.scalar(
                select(func.count(Deal.id)).where(
                    Deal.stage.in_(['qualification', 'proposal', 'negotiation', 'closing'])
                )
            )
            
            # Get pipeline value
            pipeline_value = await db.scalar(
                select(func.sum(Deal.value)).where(
                    Deal.stage.in_(['qualification', 'proposal', 'negotiation', 'closing'])
                )
            ) or 0
            
            # Get top priority deal
            top_deal = await db.scalar(
                select(Deal).where(
                    Deal.stage == 'closing'
                ).order_by(Deal.value.desc()).limit(1)
            )
            
            return {
                "total_customers": customer_count or 0,
                "active_deals": active_deals or 0,
                "pipeline_value": float(pipeline_value),
                "top_priority": top_deal.name if top_deal else "None"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch CRM context: {str(e)}")
            return {
                "total_customers": 0,
                "active_deals": 0,
                "pipeline_value": 0,
                "top_priority": "None"
            }


# Singleton
_gemini_live_instance = None

def get_gemini_live(
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash-exp",
    voice: str = "Aoede"
) -> GeminiLiveService:
    global _gemini_live_instance
    if _gemini_live_instance is None:
        _gemini_live_instance = GeminiLiveService(api_key, model, voice)
    return _gemini_live_instance
