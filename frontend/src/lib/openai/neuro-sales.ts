/**
 * Neuro-Sales Engine - Psychological Customer Analysis
 * Analyzes customer messages and classifies them psychologically
 * Adjusts response tone automatically to maximize conversion
 */

import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

export type CustomerPsychProfile =
  | 'stingy' // بخيل
  | 'hesitant' // متردد
  | 'vip' // VIP
  | 'urgent' // مستعجل
  | 'price_sensitive' // حساس للسعر
  | 'quality_focused' // يهتم بالجودة
  | 'impulsive'; // اندفاعي

export interface NeuroAnalysisResult {
  profile: CustomerPsychProfile;
  confidence: number; // 0-100
  suggestedTone: 'aggressive' | 'soft' | 'professional' | 'urgent' | 'luxury';
  suggestedResponse: string;
  urgencyLevel: 'low' | 'medium' | 'high' | 'critical';
  buyingProbability: number; // 0-100
  recommendedDiscount: number; // 0-30%
  keywords: string[];
}

const PSYCHOLOGICAL_PATTERNS = {
  stingy: [
    'غالي',
    'أرخص',
    'تخفيض',
    'مجانا',
    'كم السعر',
    'expensive',
    'cheaper',
    'discount',
    'free',
  ],
  hesitant: [
    'مش متأكد',
    'لسه',
    'بفكر',
    'هشوف',
    'not sure',
    'thinking',
    'maybe',
    'later',
  ],
  vip: ['أفضل', 'premium', 'luxury', 'best quality', 'exclusive', 'top'],
  urgent: [
    'بسرعة',
    'الآن',
    'عاجل',
    'ضروري',
    'urgent',
    'now',
    'asap',
    'immediately',
  ],
  price_sensitive: ['كم', 'سعر', 'تكلفة', 'price', 'cost', 'how much'],
  quality_focused: [
    'جودة',
    'ضمان',
    'مواصفات',
    'quality',
    'guarantee',
    'specifications',
  ],
  impulsive: ['!', 'عايز', 'أريد', 'want', 'need', 'buy now', 'عاوز'],
};

/**
 * Analyze customer message psychologically
 */
export async function analyzeCustomerPsychology(
  message: string,
  previousMessages: string[] = []
): Promise<NeuroAnalysisResult> {
  // Step 1: Pattern matching for quick classification
  const profiles = Object.entries(PSYCHOLOGICAL_PATTERNS).map(
    ([profile, keywords]) => {
      const matches = keywords.filter((keyword) =>
        message.toLowerCase().includes(keyword.toLowerCase())
      ).length;
      return { profile: profile as CustomerPsychProfile, matches };
    }
  );

  const topProfile = profiles.reduce((max, curr) =>
    curr.matches > max.matches ? curr : max
  );

  // Step 2: Deep AI analysis with GPT-4o
  const prompt = `You are a psychological sales analyst for e-commerce. Analyze this customer message and conversation history.

Current Message: "${message}"
Previous Messages: ${previousMessages.join('\n')}

Classify the customer into ONE category:
- stingy (بخيل): Focuses on price, always looking for discounts
- hesitant (متردد): Unsure, needs reassurance
- vip: Wants premium quality, willing to pay
- urgent (مستعجل): Needs it fast
- price_sensitive: Price is main concern
- quality_focused: Quality over price
- impulsive: Quick to decide, emotional buyer

Respond in JSON format:
{
  "profile": "category",
  "confidence": 0-100,
  "suggestedTone": "aggressive/soft/professional/urgent/luxury",
  "suggestedResponse": "Tailored response in Arabic",
  "urgencyLevel": "low/medium/high/critical",
  "buyingProbability": 0-100,
  "recommendedDiscount": 0-30,
  "keywords": ["key", "words", "found"]
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [
      {
        role: 'system',
        content:
          'You are a world-class sales psychologist specializing in Middle Eastern e-commerce customer behavior.',
      },
      { role: 'user', content: prompt },
    ],
    temperature: 0.3,
    response_format: { type: 'json_object' },
  });

  const analysis: NeuroAnalysisResult = JSON.parse(
    response.choices[0].message.content || '{}'
  );

  // Fallback to pattern matching if AI fails
  if (!analysis.profile) {
    return {
      profile: topProfile.profile,
      confidence: (topProfile.matches / PSYCHOLOGICAL_PATTERNS[topProfile.profile].length) * 100,
      suggestedTone: 'professional',
      suggestedResponse: generateFallbackResponse(topProfile.profile),
      urgencyLevel: 'medium',
      buyingProbability: 50,
      recommendedDiscount: 5,
      keywords: PSYCHOLOGICAL_PATTERNS[topProfile.profile],
    };
  }

  return analysis;
}

/**
 * Generate automated response based on psychological profile
 */
function generateFallbackResponse(profile: CustomerPsychProfile): string {
  const responses: Record<CustomerPsychProfile, string> = {
    stingy: '🎁 عندنا عرض خاص اليوم! خصم 15% لفترة محدودة. السعر الأصلي كان أعلى بكتير.',
    hesitant:
      '😊 مفيش مشكلة! احنا هنا عشان نساعدك. عندنا ضمان استرجاع 14 يوم لو مش عاجبك المنتج.',
    vip: '⭐ منتجاتنا Premium بجودة استثنائية. شحن VIP مجاني + هدية فاخرة مع طلبك.',
    urgent:
      '⚡ متوفر الآن! شحن سريع خلال 24 ساعة. احجز دلوقتي قبل نفاذ الكمية.',
    price_sensitive: '💰 السعر: [PRICE] جنيه. قسط على 3 دفعات بدون فوائد.',
    quality_focused:
      '✅ جودة مضمونة 100%. ضمان سنتين + شهادة أصالة. مستورد من [BRAND].',
    impulsive: '🔥 اطلب الآن! العرض ينتهي خلال ساعات. اضغط للشراء مباشرة.',
  };

  return responses[profile];
}

/**
 * Auto-adjust message tone based on psychology
 */
export function adjustMessageTone(
  originalMessage: string,
  targetTone: NeuroAnalysisResult['suggestedTone']
): string {
  const toneAdjustments = {
    aggressive: (msg: string) =>
      `⚡ ${msg} 🔥 العرض لفترة محدودة! احجز الآن قبل فوات الأوان.`,
    soft: (msg: string) => `😊 ${msg} نحن هنا لمساعدتك في أي وقت.`,
    professional: (msg: string) => `${msg} نتشرف بخدمتكم.`,
    urgent: (msg: string) => `⏰ ${msg} الكمية محدودة! سارع بالحجز.`,
    luxury: (msg: string) => `⭐ ${msg} تجربة تسوق استثنائية تليق بك.`,
  };

  return toneAdjustments[targetTone](originalMessage);
}

/**
 * Calculate optimal discount based on customer profile
 */
export function calculateOptimalDiscount(
  profile: CustomerPsychProfile,
  originalPrice: number,
  targetProfit: number
): {
  discountPercentage: number;
  finalPrice: number;
  expectedConversionIncrease: number;
} {
  const discountMap: Record<
    CustomerPsychProfile,
    { discount: number; conversionBoost: number }
  > = {
    stingy: { discount: 20, conversionBoost: 85 },
    hesitant: { discount: 10, conversionBoost: 45 },
    vip: { discount: 0, conversionBoost: 20 }, // VIPs don't need discounts
    urgent: { discount: 5, conversionBoost: 60 },
    price_sensitive: { discount: 15, conversionBoost: 70 },
    quality_focused: { discount: 5, conversionBoost: 30 },
    impulsive: { discount: 10, conversionBoost: 90 },
  };

  const { discount, conversionBoost } = discountMap[profile];
  const finalPrice = originalPrice * (1 - discount / 100);

  // Ensure minimum profit margin
  const profitMargin = ((finalPrice - targetProfit) / finalPrice) * 100;
  const adjustedDiscount = profitMargin < 15 ? discount - 5 : discount;

  return {
    discountPercentage: Math.max(0, adjustedDiscount),
    finalPrice: originalPrice * (1 - adjustedDiscount / 100),
    expectedConversionIncrease: conversionBoost,
  };
}
