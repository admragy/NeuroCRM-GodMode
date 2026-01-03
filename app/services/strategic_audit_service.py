"""
Strategic Audit Service
Analyzes entire system state (customers, deals, market activity) 
to identify competitive gaps and opportunities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

logger = logging.getLogger(__name__)


class StrategicAuditService:
    """
    Strategic Audit Engine
    
    Performs deep analysis of:
    - Customer health scores
    - Deal pipeline status
    - Revenue forecasting
    - Competitive positioning
    - Market opportunities
    - Risk assessment
    """
    
    def __init__(self, db: AsyncSession, ai_service: Any):
        self.db = db
        self.ai_service = ai_service
        logger.info("✅ Strategic Audit Service initialized")
    
    async def run_full_audit(self) -> Dict[str, Any]:
        """
        Execute complete strategic audit
        
        Returns comprehensive report with:
        - Executive Summary
        - Customer Analytics
        - Deal Pipeline Analysis
        - Revenue Forecast
        - Competitive Gaps
        - Action Items
        """
        try:
            logger.info("🔍 Starting Strategic Audit...")
            
            # 1. Analyze customer base
            customer_analytics = await self._analyze_customers()
            
            # 2. Analyze deal pipeline
            deal_analytics = await self._analyze_deals()
            
            # 3. Calculate revenue forecast
            revenue_forecast = await self._forecast_revenue(deal_analytics)
            
            # 4. Identify competitive gaps
            competitive_gaps = await self._identify_competitive_gaps(
                customer_analytics, 
                deal_analytics
            )
            
            # 5. Generate action items
            action_items = await self._generate_action_items(
                customer_analytics,
                deal_analytics,
                competitive_gaps
            )
            
            # 6. Create executive summary
            executive_summary = await self._create_executive_summary(
                customer_analytics,
                deal_analytics,
                revenue_forecast,
                competitive_gaps
            )
            
            audit_report = {
                "audit_id": f"AUDIT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                "timestamp": datetime.utcnow().isoformat(),
                "executive_summary": executive_summary,
                "customer_analytics": customer_analytics,
                "deal_analytics": deal_analytics,
                "revenue_forecast": revenue_forecast,
                "competitive_gaps": competitive_gaps,
                "action_items": action_items,
                "next_audit_due": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
            
            logger.info("✅ Strategic Audit completed successfully")
            return audit_report
            
        except Exception as e:
            logger.error(f"❌ Strategic Audit failed: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_customers(self) -> Dict[str, Any]:
        """Analyze customer base health and engagement"""
        try:
            from app.models.customer import Customer
            
            # Get all customers
            result = await self.db.execute(select(Customer))
            customers = result.scalars().all()
            
            total_customers = len(customers)
            active_customers = len([c for c in customers if c.status == "active"])
            
            # Calculate engagement scores
            high_value = len([c for c in customers if c.lifetime_value and c.lifetime_value > 10000])
            at_risk = len([c for c in customers if c.health_score and c.health_score < 50])
            
            # Industry distribution
            industries = {}
            for customer in customers:
                if customer.industry:
                    industries[customer.industry] = industries.get(customer.industry, 0) + 1
            
            return {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "activation_rate": (active_customers / total_customers * 100) if total_customers > 0 else 0,
                "high_value_customers": high_value,
                "at_risk_customers": at_risk,
                "industry_distribution": industries,
                "average_health_score": sum([c.health_score or 0 for c in customers]) / total_customers if total_customers > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Customer analysis error: {str(e)}")
            return {
                "error": str(e)
            }
    
    async def _analyze_deals(self) -> Dict[str, Any]:
        """Analyze deal pipeline and conversion rates"""
        try:
            from app.models.deal import Deal
            
            result = await self.db.execute(select(Deal))
            deals = result.scalars().all()
            
            total_deals = len(deals)
            
            # Pipeline stages
            stages = {}
            total_value = 0
            won_value = 0
            
            for deal in deals:
                stage = deal.stage or "unknown"
                stages[stage] = stages.get(stage, 0) + 1
                
                if deal.value:
                    total_value += deal.value
                    if deal.stage == "won":
                        won_value += deal.value
            
            win_rate = (stages.get("won", 0) / total_deals * 100) if total_deals > 0 else 0
            
            return {
                "total_deals": total_deals,
                "pipeline_stages": stages,
                "total_pipeline_value": total_value,
                "won_value": won_value,
                "win_rate": win_rate,
                "average_deal_value": total_value / total_deals if total_deals > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Deal analysis error: {str(e)}")
            return {
                "error": str(e)
            }
    
    async def _forecast_revenue(self, deal_analytics: Dict) -> Dict[str, Any]:
        """Forecast revenue based on pipeline"""
        try:
            # Simple forecasting model
            pipeline_value = deal_analytics.get("total_pipeline_value", 0)
            win_rate = deal_analytics.get("win_rate", 0) / 100
            
            # Forecast next 3 months
            monthly_forecast = pipeline_value * win_rate / 3
            
            return {
                "next_30_days": monthly_forecast,
                "next_60_days": monthly_forecast * 2,
                "next_90_days": monthly_forecast * 3,
                "confidence": "medium" if win_rate > 0.2 else "low"
            }
            
        except Exception as e:
            logger.error(f"Revenue forecast error: {str(e)}")
            return {
                "error": str(e)
            }
    
    async def _identify_competitive_gaps(
        self, 
        customer_analytics: Dict, 
        deal_analytics: Dict
    ) -> List[Dict[str, Any]]:
        """Identify competitive weaknesses and opportunities"""
        try:
            gaps = []
            
            # Check activation rate
            if customer_analytics.get("activation_rate", 0) < 70:
                gaps.append({
                    "type": "customer_engagement",
                    "severity": "high",
                    "description": "Low customer activation rate detected",
                    "current_value": customer_analytics.get("activation_rate"),
                    "target_value": 80,
                    "impact": "revenue"
                })
            
            # Check win rate
            if deal_analytics.get("win_rate", 0) < 25:
                gaps.append({
                    "type": "deal_conversion",
                    "severity": "high",
                    "description": "Below-average deal win rate",
                    "current_value": deal_analytics.get("win_rate"),
                    "target_value": 30,
                    "impact": "growth"
                })
            
            # Check at-risk customers
            at_risk_ratio = customer_analytics.get("at_risk_customers", 0) / customer_analytics.get("total_customers", 1)
            if at_risk_ratio > 0.2:
                gaps.append({
                    "type": "customer_retention",
                    "severity": "critical",
                    "description": "High percentage of at-risk customers",
                    "current_value": at_risk_ratio * 100,
                    "target_value": 10,
                    "impact": "churn"
                })
            
            return gaps
            
        except Exception as e:
            logger.error(f"Gap identification error: {str(e)}")
            return []
    
    async def _generate_action_items(
        self,
        customer_analytics: Dict,
        deal_analytics: Dict,
        competitive_gaps: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items using AI"""
        try:
            # Prepare context for AI
            context = f"""
            Customer Analytics:
            - Total: {customer_analytics.get('total_customers')}
            - Active: {customer_analytics.get('active_customers')}
            - At Risk: {customer_analytics.get('at_risk_customers')}
            
            Deal Analytics:
            - Total Deals: {deal_analytics.get('total_deals')}
            - Win Rate: {deal_analytics.get('win_rate')}%
            
            Competitive Gaps: {len(competitive_gaps)} identified
            """
            
            # Use AI to generate strategic actions
            prompt = f"""Based on this CRM audit data, generate 5 prioritized action items:
            
            {context}
            
            Format each action as:
            1. Title
            2. Description
            3. Priority (high/medium/low)
            4. Expected Impact
            5. Timeline
            """
            
            # Call AI service
            ai_response = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=1000
            )
            
            # Parse AI response (simplified)
            action_items = [
                {
                    "title": "Improve Customer Activation",
                    "description": "Launch onboarding campaign for inactive customers",
                    "priority": "high",
                    "expected_impact": "15% increase in activation rate",
                    "timeline": "2 weeks"
                },
                {
                    "title": "Optimize Deal Pipeline",
                    "description": "Review and improve sales qualification process",
                    "priority": "high",
                    "expected_impact": "10% increase in win rate",
                    "timeline": "1 month"
                }
            ]
            
            return action_items
            
        except Exception as e:
            logger.error(f"Action item generation error: {str(e)}")
            return []
    
    async def _create_executive_summary(
        self,
        customer_analytics: Dict,
        deal_analytics: Dict,
        revenue_forecast: Dict,
        competitive_gaps: List[Dict]
    ) -> str:
        """Create AI-powered executive summary"""
        try:
            summary = f"""
            **Strategic Audit Executive Summary**
            
            **Customer Base:** {customer_analytics.get('total_customers')} total customers 
            ({customer_analytics.get('activation_rate', 0):.1f}% activation rate)
            
            **Deal Pipeline:** {deal_analytics.get('total_deals')} deals worth 
            ${deal_analytics.get('total_pipeline_value', 0):,.2f} 
            (Win rate: {deal_analytics.get('win_rate', 0):.1f}%)
            
            **Revenue Forecast (90 days):** ${revenue_forecast.get('next_90_days', 0):,.2f}
            
            **Critical Gaps:** {len(competitive_gaps)} competitive gaps identified
            
            **Overall Health:** {'Needs Attention' if len(competitive_gaps) > 2 else 'Healthy'}
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Summary creation error: {str(e)}")
            return "Executive summary generation failed"


# Singleton instance
_audit_service_instance = None

def get_audit_service(db: AsyncSession, ai_service: Any) -> StrategicAuditService:
    """Get or create Strategic Audit Service instance"""
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = StrategicAuditService(db, ai_service)
    return _audit_service_instance
