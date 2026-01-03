"""
Advanced Features API Routes
- Strategic Audit
- Neural Empathy Sync
- Strategic Compass
- Supabase Sync
- Marketing Hub
- Gemini Live
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_service import get_ai_service
from app.services.strategic_audit_service import get_audit_service
from app.services.neural_empathy_service import get_empathy_service
from app.services.strategic_compass_service import get_compass_service
from app.services.supabase_service import get_supabase_service
from app.services.marketing_hub_service import get_marketing_hub
from app.services.gemini_live_service import get_gemini_live
from app.core.config import settings

router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])


# ==================== REQUEST MODELS ====================

class ConversationAnalysisRequest(BaseModel):
    conversation_text: str
    language: str = "en"
    customer_id: Optional[str] = None


class ABTestRequest(BaseModel):
    campaign_name: str
    target_audience: str
    brand_voice: str = "professional"


class CompetitorAnalysisRequest(BaseModel):
    industry: str
    company_name: str


class VoiceSessionRequest(BaseModel):
    user_id: str
    include_crm_context: bool = True


# ==================== STRATEGIC AUDIT ====================

@router.post("/strategic-audit/run")
async def run_strategic_audit(
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 Run complete strategic audit
    
    Analyzes:
    - Customer health
    - Deal pipeline
    - Revenue forecast
    - Competitive gaps
    - Action items
    """
    if not settings.STRATEGIC_AUDIT_ENABLED:
        raise HTTPException(status_code=403, detail="Strategic Audit not enabled")
    
    ai_service = get_ai_service()
    audit_service = get_audit_service(db, ai_service)
    
    report = await audit_service.run_full_audit()
    
    return {
        "success": True,
        "report": report
    }


@router.get("/strategic-audit/status")
async def get_audit_status():
    """Get Strategic Audit feature status"""
    return {
        "enabled": settings.STRATEGIC_AUDIT_ENABLED,
        "interval_hours": settings.STRATEGIC_AUDIT_INTERVAL / 3600,
        "auto_run": settings.STRATEGIC_AUDIT_AUTO_RUN
    }


# ==================== NEURAL EMPATHY SYNC ====================

@router.post("/empathy/analyze")
async def analyze_conversation_sentiment(
    request: ConversationAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    🧠 Analyze conversation for emotional content
    
    Returns:
    - Sentiment score
    - Emotional state
    - Stress level
    - Recommended actions
    """
    if not settings.NEURAL_EMPATHY_ENABLED:
        raise HTTPException(status_code=403, detail="Neural Empathy not enabled")
    
    ai_service = get_ai_service()
    empathy_service = get_empathy_service(ai_service)
    
    analysis = await empathy_service.analyze_conversation(
        request.conversation_text,
        request.language
    )
    
    # Sync to customer record if customer_id provided
    if request.customer_id:
        background_tasks.add_task(
            empathy_service.sync_customer_emotional_state,
            request.customer_id,
            analysis,
            db
        )
    
    return {
        "success": True,
        "analysis": analysis
    }


@router.get("/empathy/at-risk")
async def get_at_risk_customers(
    threshold: int = 70,
    db: AsyncSession = Depends(get_db)
):
    """
    ⚠️ Get list of customers with high stress levels
    """
    if not settings.NEURAL_EMPATHY_ENABLED:
        raise HTTPException(status_code=403, detail="Neural Empathy not enabled")
    
    ai_service = get_ai_service()
    empathy_service = get_empathy_service(ai_service)
    
    at_risk = await empathy_service.get_at_risk_customers(db, threshold)
    
    return {
        "success": True,
        "count": len(at_risk),
        "customers": at_risk
    }


# ==================== STRATEGIC COMPASS ====================

@router.get("/compass/priorities")
async def get_strategic_priorities(
    user_id: Optional[str] = None,
    top_n: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    🧭 Get today's strategic priorities
    
    Returns prioritized tasks based on:
    - Expected deal value
    - Conversion probability
    - Time sensitivity
    """
    if not settings.STRATEGIC_COMPASS_ENABLED:
        raise HTTPException(status_code=403, detail="Strategic Compass not enabled")
    
    compass_service = get_compass_service(db)
    
    priorities = await compass_service.generate_daily_priorities(user_id, top_n)
    
    return {
        "success": True,
        "compass": priorities
    }


@router.get("/compass/status")
async def get_compass_status():
    """Get Strategic Compass feature status"""
    return {
        "enabled": settings.STRATEGIC_COMPASS_ENABLED,
        "recalc_interval_hours": settings.STRATEGIC_COMPASS_RECALC_INTERVAL / 3600,
        "top_priority_count": settings.STRATEGIC_COMPASS_TOP_PRIORITY_COUNT
    }


# ==================== SUPABASE SYNC ====================

@router.post("/supabase/sync/customer")
async def sync_customer_to_cloud(
    customer_data: Dict[str, Any]
):
    """
    ☁️ Manually trigger customer sync to Supabase
    """
    if not settings.SUPABASE_SYNC_ENABLED:
        raise HTTPException(status_code=403, detail="Supabase sync not enabled")
    
    supabase = get_supabase_service(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    success = await supabase.silent_sync_customer(customer_data)
    
    return {
        "success": success,
        "message": "Customer synced to cloud" if success else "Sync failed"
    }


@router.get("/supabase/health")
async def check_supabase_health():
    """
    🏥 Check Supabase connection health
    """
    supabase = get_supabase_service(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    health = await supabase.health_check()
    
    return health


@router.get("/supabase/fetch/settings")
async def fetch_brand_settings():
    """
    ⚙️ Fetch brand settings from Supabase with fallback
    """
    supabase = get_supabase_service(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    settings_data = await supabase.fetch_brand_settings()
    
    return {
        "success": True,
        "settings": settings_data
    }


# ==================== MARKETING HUB ====================

@router.post("/marketing/ab-test/generate")
async def generate_ab_test(
    request: ABTestRequest
):
    """
    🧪 Generate A/B test variants
    
    Creates two variants:
    - Variant A: Brand authority
    - Variant B: Gap discovery
    """
    if not settings.AB_TESTING_ENABLED:
        raise HTTPException(status_code=403, detail="A/B Testing not enabled")
    
    marketing_hub = get_marketing_hub(
        settings.GOOGLE_SEARCH_API_KEY,
        settings.GOOGLE_SEARCH_ENGINE_ID
    )
    
    test = await marketing_hub.generate_ab_test(
        request.campaign_name,
        request.target_audience,
        request.brand_voice
    )
    
    return {
        "success": True,
        "test": test
    }


@router.post("/marketing/visual/generate")
async def generate_ad_visual(
    prompt: str,
    brand_colors: Optional[list] = None,
    style: str = "professional"
):
    """
    🎨 Generate commercial-grade image using Google Imagen
    """
    if not settings.IMAGEN_ENABLED:
        raise HTTPException(status_code=403, detail="Imagen not enabled")
    
    marketing_hub = get_marketing_hub()
    
    visual = await marketing_hub.generate_ad_visual(prompt, brand_colors, style)
    
    return {
        "success": True,
        "visual": visual
    }


@router.post("/marketing/competitors/analyze")
async def analyze_competitors(
    request: CompetitorAnalysisRequest
):
    """
    🔍 Analyze competitors using Google Search
    """
    if not settings.MARKET_INTELLIGENCE_ENABLED:
        raise HTTPException(status_code=403, detail="Market Intelligence not enabled")
    
    marketing_hub = get_marketing_hub(
        settings.GOOGLE_SEARCH_API_KEY,
        settings.GOOGLE_SEARCH_ENGINE_ID
    )
    
    analysis = await marketing_hub.analyze_competitors(
        request.industry,
        request.company_name
    )
    
    return {
        "success": True,
        "analysis": analysis
    }


# ==================== GEMINI LIVE ====================

@router.post("/gemini-live/session/start")
async def start_gemini_live_session(
    request: VoiceSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    🎙️ Start Gemini Live voice session with OmniOracle
    
    Returns:
    - Session ID
    - WebSocket URL
    - System prompt with CRM context
    """
    if not settings.GEMINI_LIVE_ENABLED:
        raise HTTPException(status_code=403, detail="Gemini Live not enabled")
    
    gemini_live = get_gemini_live(
        settings.GOOGLE_API_KEY,
        settings.GEMINI_LIVE_MODEL,
        settings.GEMINI_LIVE_VOICE
    )
    
    # Get CRM context
    crm_context = None
    if request.include_crm_context:
        crm_context = await gemini_live.get_crm_context(request.user_id, db)
    
    session = await gemini_live.start_voice_session(request.user_id, crm_context)
    
    return {
        "success": True,
        "session": session
    }


@router.get("/gemini-live/status")
async def get_gemini_live_status():
    """Get Gemini Live feature status"""
    return {
        "enabled": settings.GEMINI_LIVE_ENABLED,
        "model": settings.GEMINI_LIVE_MODEL,
        "voice": settings.GEMINI_LIVE_VOICE,
        "websocket_url": settings.GEMINI_LIVE_WEBSOCKET_URL
    }


# ==================== FEATURE STATUS OVERVIEW ====================

@router.get("/features/status")
async def get_all_features_status():
    """
    📊 Get status of all advanced features
    """
    return {
        "strategic_audit": {
            "enabled": settings.STRATEGIC_AUDIT_ENABLED,
            "auto_run": settings.STRATEGIC_AUDIT_AUTO_RUN,
            "interval_hours": settings.STRATEGIC_AUDIT_INTERVAL / 3600
        },
        "neural_empathy": {
            "enabled": settings.NEURAL_EMPATHY_ENABLED,
            "model": settings.NEURAL_EMPATHY_MODEL,
            "threshold": settings.NEURAL_EMPATHY_THRESHOLD,
            "languages": settings.NEURAL_EMPATHY_LANGUAGES
        },
        "strategic_compass": {
            "enabled": settings.STRATEGIC_COMPASS_ENABLED,
            "recalc_interval_hours": settings.STRATEGIC_COMPASS_RECALC_INTERVAL / 3600,
            "top_priorities": settings.STRATEGIC_COMPASS_TOP_PRIORITY_COUNT
        },
        "supabase_sync": {
            "enabled": settings.SUPABASE_SYNC_ENABLED,
            "realtime": settings.SUPABASE_REALTIME_ENABLED,
            "auto_backup": settings.SUPABASE_AUTO_BACKUP
        },
        "marketing_hub": {
            "enabled": settings.MARKETING_HUB_ENABLED,
            "ab_testing": settings.AB_TESTING_ENABLED,
            "imagen": settings.IMAGEN_ENABLED,
            "market_intelligence": settings.MARKET_INTELLIGENCE_ENABLED
        },
        "gemini_live": {
            "enabled": settings.GEMINI_LIVE_ENABLED,
            "model": settings.GEMINI_LIVE_MODEL,
            "voice": settings.GEMINI_LIVE_VOICE
        }
    }
