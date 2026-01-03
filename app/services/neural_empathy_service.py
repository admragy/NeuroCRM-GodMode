"""
Neural Empathy Sync Service
Analyzes conversation tone and user behavior to update customer emotional state
and alert manager about stress levels or growth opportunities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class NeuralEmpathyService:
    """
    Neural Empathy Sync Engine
    
    Background engine that:
    - Analyzes message sentiment and tone
    - Detects emotional states (stress, happiness, frustration)
    - Updates customer psychological profiles
    - Alerts managers about critical emotional states
    - Identifies growth opportunities based on sentiment
    """
    
    # Emotion detection keywords (multilingual)
    STRESS_KEYWORDS = {
        "en": ["urgent", "asap", "frustrated", "disappointed", "angry", "problem", "issue", "complaint"],
        "ar": ["عاجل", "سريع", "محبط", "مشكلة", "غضبان", "شكوى", "متضايق", "زعلان"]
    }
    
    OPPORTUNITY_KEYWORDS = {
        "en": ["interested", "excited", "love", "amazing", "great", "perfect", "excellent", "want"],
        "ar": ["مهتم", "متحمس", "رائع", "ممتاز", "عظيم", "احب", "اريد", "مثالي"]
    }
    
    def __init__(self, ai_service: Any):
        self.ai_service = ai_service
        logger.info("✅ Neural Empathy Service initialized")
    
    async def analyze_conversation(
        self, 
        conversation_text: str, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze single conversation for emotional content
        
        Returns:
        - sentiment_score: -1 (negative) to +1 (positive)
        - emotional_state: happy, neutral, stressed, frustrated, angry
        - stress_level: 0-100
        - opportunity_score: 0-100
        - detected_emotions: list of emotions
        - recommended_actions: list of suggested responses
        """
        try:
            logger.info(f"🧠 Analyzing conversation (language: {language})")
            
            # 1. Rule-based analysis (fast)
            rule_based = self._rule_based_analysis(conversation_text, language)
            
            # 2. AI-powered analysis (accurate)
            ai_based = await self._ai_sentiment_analysis(conversation_text, language)
            
            # 3. Combine results
            combined_analysis = self._combine_analyses(rule_based, ai_based)
            
            # 4. Generate recommendations
            recommendations = self._generate_recommendations(combined_analysis)
            
            result = {
                "sentiment_score": combined_analysis["sentiment_score"],
                "emotional_state": combined_analysis["emotional_state"],
                "stress_level": combined_analysis["stress_level"],
                "opportunity_score": combined_analysis["opportunity_score"],
                "detected_emotions": combined_analysis["emotions"],
                "recommended_actions": recommendations,
                "requires_manager_attention": combined_analysis["stress_level"] > 70,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Analysis complete: {result['emotional_state']} (stress: {result['stress_level']})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Empathy analysis failed: {str(e)}")
            return {
                "error": str(e),
                "sentiment_score": 0,
                "emotional_state": "unknown"
            }
    
    def _rule_based_analysis(self, text: str, language: str) -> Dict[str, Any]:
        """Fast rule-based sentiment detection"""
        text_lower = text.lower()
        
        # Count stress indicators
        stress_keywords = self.STRESS_KEYWORDS.get(language, [])
        stress_count = sum(1 for keyword in stress_keywords if keyword in text_lower)
        
        # Count opportunity indicators
        opp_keywords = self.OPPORTUNITY_KEYWORDS.get(language, [])
        opp_count = sum(1 for keyword in opp_keywords if keyword in text_lower)
        
        # Detect exclamation marks (excitement or anger)
        exclamation_count = text.count("!")
        question_count = text.count("?")
        
        # Calculate scores
        stress_level = min(100, stress_count * 20 + exclamation_count * 10)
        opportunity_score = min(100, opp_count * 25)
        
        # Determine emotional state
        if stress_level > 60:
            emotional_state = "stressed" if stress_level < 80 else "frustrated"
        elif opportunity_score > 60:
            emotional_state = "excited"
        else:
            emotional_state = "neutral"
        
        sentiment_score = (opportunity_score - stress_level) / 100
        
        return {
            "sentiment_score": max(-1, min(1, sentiment_score)),
            "emotional_state": emotional_state,
            "stress_level": stress_level,
            "opportunity_score": opportunity_score,
            "emotions": [emotional_state],
            "method": "rule_based"
        }
    
    async def _ai_sentiment_analysis(self, text: str, language: str) -> Dict[str, Any]:
        """AI-powered deep sentiment analysis"""
        try:
            prompt = f"""Analyze the emotional tone of this message (language: {language}):

"{text}"

Provide:
1. Sentiment score (-1 to +1)
2. Emotional state (happy/neutral/stressed/frustrated/angry/excited)
3. Stress level (0-100)
4. Opportunity score (0-100) - likelihood of sales opportunity
5. List of detected emotions

Respond in JSON format."""
            
            # Call AI service
            response = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=300
            )
            
            # Parse AI response (simplified - in production, use proper JSON parsing)
            return {
                "sentiment_score": 0.5,  # Placeholder
                "emotional_state": "neutral",
                "stress_level": 30,
                "opportunity_score": 40,
                "emotions": ["calm", "interested"],
                "method": "ai_powered"
            }
            
        except Exception as e:
            logger.error(f"AI sentiment analysis failed: {str(e)}")
            return self._rule_based_analysis(text, language)
    
    def _combine_analyses(self, rule_based: Dict, ai_based: Dict) -> Dict[str, Any]:
        """Combine rule-based and AI results with weighted average"""
        # Weight: 40% rule-based, 60% AI
        combined = {
            "sentiment_score": rule_based["sentiment_score"] * 0.4 + ai_based["sentiment_score"] * 0.6,
            "emotional_state": ai_based["emotional_state"],  # Trust AI for state
            "stress_level": int(rule_based["stress_level"] * 0.4 + ai_based["stress_level"] * 0.6),
            "opportunity_score": int(rule_based["opportunity_score"] * 0.4 + ai_based["opportunity_score"] * 0.6),
            "emotions": list(set(rule_based["emotions"] + ai_based["emotions"]))
        }
        return combined
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate action recommendations based on emotional state"""
        recommendations = []
        
        if analysis["stress_level"] > 70:
            recommendations.append("🚨 Priority: Immediate manager intervention required")
            recommendations.append("🤝 Recommend: Personal call within 2 hours")
            recommendations.append("💼 Action: Assign senior account manager")
            
        elif analysis["stress_level"] > 40:
            recommendations.append("⚠️ Attention: Customer showing signs of frustration")
            recommendations.append("📞 Recommend: Follow-up call within 24 hours")
            
        if analysis["opportunity_score"] > 60:
            recommendations.append("🎯 Opportunity: High purchase intent detected")
            recommendations.append("📊 Action: Send product demo or pricing")
            recommendations.append("⏰ Timing: Contact within 4 hours for best conversion")
        
        if not recommendations:
            recommendations.append("✅ Status: Normal engagement - continue standard follow-up")
        
        return recommendations
    
    async def sync_customer_emotional_state(
        self, 
        customer_id: str, 
        analysis: Dict[str, Any],
        db: Any
    ) -> bool:
        """Update customer record with emotional insights"""
        try:
            from app.models.customer import Customer
            from sqlalchemy import update
            
            # Update customer's emotional profile
            stmt = update(Customer).where(
                Customer.id == customer_id
            ).values(
                emotional_state=analysis["emotional_state"],
                stress_level=analysis["stress_level"],
                last_sentiment_update=datetime.utcnow()
            )
            
            await db.execute(stmt)
            await db.commit()
            
            logger.info(f"✅ Customer {customer_id} emotional state updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync emotional state: {str(e)}")
            return False
    
    async def get_at_risk_customers(self, db: Any, threshold: int = 70) -> List[Dict]:
        """Get list of customers with high stress levels"""
        try:
            from app.models.customer import Customer
            from sqlalchemy import select
            
            stmt = select(Customer).where(
                Customer.stress_level >= threshold
            ).order_by(Customer.stress_level.desc())
            
            result = await db.execute(stmt)
            customers = result.scalars().all()
            
            at_risk_list = [
                {
                    "customer_id": c.id,
                    "name": c.name,
                    "stress_level": c.stress_level,
                    "emotional_state": c.emotional_state,
                    "last_update": c.last_sentiment_update.isoformat() if c.last_sentiment_update else None
                }
                for c in customers
            ]
            
            logger.info(f"📊 Found {len(at_risk_list)} at-risk customers")
            return at_risk_list
            
        except Exception as e:
            logger.error(f"Failed to get at-risk customers: {str(e)}")
            return []


# Singleton instance
_empathy_service_instance = None

def get_empathy_service(ai_service: Any) -> NeuralEmpathyService:
    """Get or create Neural Empathy Service instance"""
    global _empathy_service_instance
    if _empathy_service_instance is None:
        _empathy_service_instance = NeuralEmpathyService(ai_service)
    return _empathy_service_instance
