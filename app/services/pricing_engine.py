from decimal import Decimal
from typing import Dict, Optional

class NeuroSalesEngine:
    def __init__(self, min_margin_percent: float = 0.15):
        self.min_margin = min_margin_percent

    def calculate_dynamic_price(self, 
                                cost_price: float, 
                                competitor_price: Optional[float], 
                                customer_profile: str) -> Dict:
        # 1. Floor Price (Cost + 15%)
        min_acceptable_price = cost_price * (1 + self.min_margin)
        
        # Base Price
        if competitor_price:
            base_price = competitor_price
        else:
            base_price = cost_price * 1.30
        
        final_price = base_price
        log = []

        # 2. Competitor Logic
        if competitor_price:
            if competitor_price < min_acceptable_price:
                final_price = min_acceptable_price
                log.append(f"Competitor ({competitor_price}) below floor. Holding floor.")
            else:
                final_price = competitor_price * 0.99
                log.append("Undercut competitor by 1%.")

        # 3. Psycho-Profiling
        discount_reason = None
        
        if customer_profile == "price_sensitive":
            # If price is high, drop it to floor
            if final_price > min_acceptable_price:
                final_price = min_acceptable_price 
                discount_reason = "Max discount applied for price sensitivity."
            # If price is ALREADY at floor (due to aggressive competitor), explain why
            else:
                discount_reason = "Best possible market price guaranteed (Floor Reached)."
                
        elif customer_profile == "vip":
            premium_price = cost_price * 1.50
            if final_price < premium_price:
                final_price = premium_price
                discount_reason = "Premium pricing applied for VIP experience."
            
        elif customer_profile == "hesitant":
            potential_price = final_price * 0.95
            if potential_price >= min_acceptable_price:
                final_price = potential_price
                discount_reason = "5% Nudge discount."
            else:
                final_price = min_acceptable_price
                discount_reason = "Best possible price offered (floor reached)."

        # Safety Check
        final_price = max(final_price, min_acceptable_price)

        return {
            "final_price": round(final_price, 2),
            "min_acceptable_price": round(min_acceptable_price, 2),
            "margin_percent": round(((final_price - cost_price) / cost_price) * 100, 2),
            "customer_profile": customer_profile,
            "note": discount_reason or "Standard competitive pricing"
        }
