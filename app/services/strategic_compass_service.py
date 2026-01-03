"""
Strategic Compass Service
Smart task dashboard that generates daily priorities based on expected capital value of deals
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

logger = logging.getLogger(__name__)


class StrategicCompassService:
    """
    Strategic Compass - Priority Task Generator
    
    Generates intelligent daily priorities based on:
    - Expected deal value
    - Deal stage and conversion probability
    - Customer lifetime value
    - Time sensitivity
    - Resource allocation
    """
    
    # Priority weights
    WEIGHTS = {
        "deal_value": 0.35,
        "conversion_probability": 0.25,
        "time_sensitivity": 0.20,
        "customer_ltv": 0.15,
        "relationship_strength": 0.05
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("✅ Strategic Compass Service initialized")
    
    async def generate_daily_priorities(
        self, 
        user_id: Optional[str] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Generate top N priority tasks for today
        
        Returns:
        - priority_tasks: list of tasks ordered by strategic value
        - expected_revenue_impact: total potential revenue
        - time_allocation: recommended time distribution
        - strategic_insights: key insights
        """
        try:
            logger.info(f"🧭 Generating Strategic Compass for user: {user_id or 'all'}")
            
            # 1. Get active deals
            deals = await self._get_active_deals(user_id)
            
            # 2. Calculate priority scores
            scored_deals = await self._calculate_priority_scores(deals)
            
            # 3. Generate tasks
            priority_tasks = self._generate_tasks_from_deals(scored_deals, top_n)
            
            # 4. Calculate expected impact
            revenue_impact = self._calculate_revenue_impact(priority_tasks)
            
            # 5. Recommend time allocation
            time_allocation = self._recommend_time_allocation(priority_tasks)
            
            # 6. Generate strategic insights
            insights = self._generate_strategic_insights(priority_tasks, scored_deals)
            
            result = {
                "compass_id": f"COMPASS-{datetime.utcnow().strftime('%Y%m%d')}",
                "generated_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "priority_tasks": priority_tasks,
                "expected_revenue_impact": revenue_impact,
                "time_allocation": time_allocation,
                "strategic_insights": insights,
                "next_refresh": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
            
            logger.info(f"✅ Generated {len(priority_tasks)} priority tasks")
            return result
            
        except Exception as e:
            logger.error(f"❌ Strategic Compass generation failed: {str(e)}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _get_active_deals(self, user_id: Optional[str] = None) -> List[Any]:
        """Get all active deals from database"""
        try:
            from app.models.deal import Deal
            
            query = select(Deal).where(
                Deal.stage.in_(['qualification', 'proposal', 'negotiation', 'closing'])
            )
            
            if user_id:
                query = query.where(Deal.owner_id == user_id)
            
            result = await self.db.execute(query)
            deals = result.scalars().all()
            
            logger.info(f"📊 Found {len(deals)} active deals")
            return deals
            
        except Exception as e:
            logger.error(f"Failed to get active deals: {str(e)}")
            return []
    
    async def _calculate_priority_scores(self, deals: List[Any]) -> List[Dict[str, Any]]:
        """Calculate priority score for each deal"""
        scored_deals = []
        
        for deal in deals:
            # Get deal value
            deal_value = getattr(deal, 'value', 0) or 0
            
            # Calculate conversion probability based on stage
            stage_probabilities = {
                'qualification': 0.10,
                'proposal': 0.30,
                'negotiation': 0.60,
                'closing': 0.85
            }
            conv_prob = stage_probabilities.get(getattr(deal, 'stage', 'qualification'), 0.1)
            
            # Calculate time sensitivity (days since last update)
            last_update = getattr(deal, 'updated_at', datetime.utcnow())
            days_stale = (datetime.utcnow() - last_update).days if last_update else 0
            time_sensitivity = max(0, 100 - (days_stale * 10))  # Decays by 10 per day
            
            # Customer LTV (if available)
            customer_ltv = 0
            if hasattr(deal, 'customer') and deal.customer:
                customer_ltv = getattr(deal.customer, 'lifetime_value', 0) or 0
            
            # Relationship strength (simplified)
            relationship_strength = 50  # Default
            
            # Calculate weighted score
            normalized_value = min(100, deal_value / 1000)  # Normalize to 0-100
            normalized_ltv = min(100, customer_ltv / 10000)
            
            priority_score = (
                normalized_value * self.WEIGHTS['deal_value'] +
                conv_prob * 100 * self.WEIGHTS['conversion_probability'] +
                time_sensitivity * self.WEIGHTS['time_sensitivity'] +
                normalized_ltv * self.WEIGHTS['customer_ltv'] +
                relationship_strength * self.WEIGHTS['relationship_strength']
            )
            
            scored_deals.append({
                "deal_id": deal.id,
                "deal_name": getattr(deal, 'name', 'Untitled Deal'),
                "deal_value": deal_value,
                "stage": getattr(deal, 'stage', 'unknown'),
                "conversion_probability": conv_prob,
                "expected_value": deal_value * conv_prob,
                "priority_score": priority_score,
                "time_sensitivity": time_sensitivity,
                "days_stale": days_stale,
                "customer_name": getattr(deal.customer, 'name', 'Unknown') if hasattr(deal, 'customer') and deal.customer else 'Unknown'
            })
        
        # Sort by priority score
        scored_deals.sort(key=lambda x: x['priority_score'], reverse=True)
        return scored_deals
    
    def _generate_tasks_from_deals(self, scored_deals: List[Dict], top_n: int) -> List[Dict[str, Any]]:
        """Generate actionable tasks from top deals"""
        tasks = []
        
        for i, deal in enumerate(scored_deals[:top_n], 1):
            # Determine task based on stage
            task_templates = {
                'qualification': f"🎯 Qualify: {deal['deal_name']} - Validate budget and decision makers",
                'proposal': f"📄 Proposal: {deal['deal_name']} - Send detailed proposal and pricing",
                'negotiation': f"💬 Negotiate: {deal['deal_name']} - Address objections and finalize terms",
                'closing': f"🤝 Close: {deal['deal_name']} - Get contract signed today"
            }
            
            task = {
                "rank": i,
                "task_id": f"TASK-{deal['deal_id']}-{datetime.utcnow().strftime('%Y%m%d')}",
                "title": task_templates.get(deal['stage'], f"📞 Follow up: {deal['deal_name']}"),
                "deal_id": deal['deal_id'],
                "deal_name": deal['deal_name'],
                "customer_name": deal['customer_name'],
                "priority_score": round(deal['priority_score'], 2),
                "expected_value": deal['expected_value'],
                "deal_value": deal['deal_value'],
                "stage": deal['stage'],
                "conversion_probability": deal['conversion_probability'] * 100,
                "urgency": "high" if deal['time_sensitivity'] < 50 else "medium" if deal['time_sensitivity'] < 75 else "low",
                "recommended_time": self._estimate_task_time(deal),
                "action_items": self._generate_action_items(deal)
            }
            
            tasks.append(task)
        
        return tasks
    
    def _estimate_task_time(self, deal: Dict) -> int:
        """Estimate time needed for task (in minutes)"""
        base_time = {
            'qualification': 30,
            'proposal': 60,
            'negotiation': 45,
            'closing': 90
        }
        return base_time.get(deal['stage'], 30)
    
    def _generate_action_items(self, deal: Dict) -> List[str]:
        """Generate specific action items for deal"""
        stage_actions = {
            'qualification': [
                "Review company profile and recent news",
                "Prepare discovery questions",
                "Schedule qualification call"
            ],
            'proposal': [
                "Customize proposal template",
                "Calculate ROI and pricing",
                "Send proposal via email"
            ],
            'negotiation': [
                "Review contract terms",
                "Prepare negotiation points",
                "Schedule negotiation meeting"
            ],
            'closing': [
                "Prepare final contract",
                "Schedule signing meeting",
                "Coordinate with legal team"
            ]
        }
        return stage_actions.get(deal['stage'], ["Follow up with customer"])
    
    def _calculate_revenue_impact(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Calculate total expected revenue impact"""
        total_expected = sum(task['expected_value'] for task in tasks)
        total_potential = sum(task['deal_value'] for task in tasks)
        avg_conversion = sum(task['conversion_probability'] for task in tasks) / len(tasks) if tasks else 0
        
        return {
            "total_expected_revenue": total_expected,
            "total_potential_revenue": total_potential,
            "average_conversion_probability": round(avg_conversion, 1),
            "high_priority_count": len([t for t in tasks if t['urgency'] == 'high'])
        }
    
    def _recommend_time_allocation(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Recommend time distribution across tasks"""
        total_time = sum(task['recommended_time'] for task in tasks)
        
        return {
            "total_recommended_time_minutes": total_time,
            "total_recommended_time_hours": round(total_time / 60, 1),
            "time_by_urgency": {
                "high": sum(t['recommended_time'] for t in tasks if t['urgency'] == 'high'),
                "medium": sum(t['recommended_time'] for t in tasks if t['urgency'] == 'medium'),
                "low": sum(t['recommended_time'] for t in tasks if t['urgency'] == 'low')
            },
            "recommended_schedule": "Focus on high-urgency tasks in morning (9-12), medium in afternoon (1-4)"
        }
    
    def _generate_strategic_insights(self, tasks: List[Dict], all_deals: List[Dict]) -> List[str]:
        """Generate strategic insights"""
        insights = []
        
        if tasks:
            # Top opportunity
            top_task = tasks[0]
            insights.append(
                f"🎯 Top Priority: {top_task['deal_name']} - Expected value ${top_task['expected_value']:,.2f}"
            )
            
            # Urgency alert
            high_urgency = [t for t in tasks if t['urgency'] == 'high']
            if high_urgency:
                insights.append(
                    f"⚠️ {len(high_urgency)} deals require immediate attention (stale > 5 days)"
                )
            
            # Stage distribution
            stages = {}
            for task in tasks:
                stages[task['stage']] = stages.get(task['stage'], 0) + 1
            insights.append(
                f"📊 Pipeline Focus: {', '.join([f'{k}: {v}' for k, v in stages.items()])}"
            )
        
        return insights


# Singleton instance
_compass_service_instance = None

def get_compass_service(db: AsyncSession) -> StrategicCompassService:
    """Get or create Strategic Compass Service instance"""
    global _compass_service_instance
    if _compass_service_instance is None:
        _compass_service_instance = StrategicCompassService(db)
    return _compass_service_instance
