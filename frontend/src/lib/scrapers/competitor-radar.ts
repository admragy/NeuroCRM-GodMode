/**
 * Competitor Radar - 24/7 Competitor Monitoring System
 * Scrapes competitor pages and sends instant alerts on price changes
 * Suggests counter-offers automatically
 */

import puppeteer, { Browser } from 'puppeteer';
import * as cheerio from 'cheerio';
import { supabase } from '@/lib/supabase/client';

export interface CompetitorData {
  id: string;
  name: string;
  url: string;
  currentPrice: number;
  previousPrice: number;
  priceChange: number; // percentage
  lastChecked: Date;
  productName: string;
  stockStatus: 'in_stock' | 'out_of_stock' | 'low_stock';
  promoText?: string;
}

export interface CounterOfferSuggestion {
  suggestedPrice: number;
  discountPercentage: number;
  reasoning: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  marketingMessage: string;
}

let browser: Browser | null = null;

/**
 * Initialize headless browser for scraping
 */
async function initBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
      ],
    });
  }
  return browser;
}

/**
 * Scrape competitor product page
 */
export async function scrapeCompetitorPage(
  url: string
): Promise<Partial<CompetitorData>> {
  const browser = await initBrowser();
  const page = await browser.newPage();

  try {
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    );

    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000,
    });

    // Wait for content to load
    await page.waitForTimeout(2000);

    const html = await page.content();
    const $ = cheerio.load(html);

    // Generic selectors - adapt to your competitors' structure
    const priceSelectors = [
      '.price',
      '[class*="price"]',
      '[id*="price"]',
      'span[itemprop="price"]',
      '.product-price',
      '.woocommerce-Price-amount',
    ];

    let price = 0;
    for (const selector of priceSelectors) {
      const priceText = $(selector).first().text().trim();
      const priceMatch = priceText.match(/[\d,]+\.?\d*/);
      if (priceMatch) {
        price = parseFloat(priceMatch[0].replace(/,/g, ''));
        if (price > 0) break;
      }
    }

    // Product name
    const productName =
      $('h1').first().text().trim() ||
      $('[class*="product-title"]').first().text().trim() ||
      $('title').text().trim();

    // Stock status
    const stockText = $('body').text().toLowerCase();
    let stockStatus: CompetitorData['stockStatus'] = 'in_stock';
    if (
      stockText.includes('out of stock') ||
      stockText.includes('نفذت الكمية')
    ) {
      stockStatus = 'out_of_stock';
    } else if (
      stockText.includes('low stock') ||
      stockText.includes('كمية محدودة')
    ) {
      stockStatus = 'low_stock';
    }

    // Promo text
    const promoText =
      $('[class*="promo"]').first().text().trim() ||
      $('[class*="sale"]').first().text().trim() ||
      $('[class*="offer"]').first().text().trim();

    return {
      currentPrice: price,
      productName,
      stockStatus,
      promoText,
      lastChecked: new Date(),
    };
  } catch (error) {
    console.error('Scraping error:', error);
    throw error;
  } finally {
    await page.close();
  }
}

/**
 * Monitor competitor and save to database
 */
export async function monitorCompetitor(
  competitorId: string,
  url: string,
  name: string
): Promise<CompetitorData> {
  // Get previous data
  const { data: previousData } = await supabase
    .from('competitors')
    .select('*')
    .eq('id', competitorId)
    .single();

  // Scrape current data
  const scrapedData = await scrapeCompetitorPage(url);

  const previousPrice = previousData?.current_price || 0;
  const currentPrice = scrapedData.currentPrice || 0;
  const priceChange =
    previousPrice > 0 ? ((currentPrice - previousPrice) / previousPrice) * 100 : 0;

  const competitorData: CompetitorData = {
    id: competitorId,
    name,
    url,
    currentPrice,
    previousPrice,
    priceChange,
    lastChecked: new Date(),
    productName: scrapedData.productName || 'Unknown Product',
    stockStatus: scrapedData.stockStatus || 'in_stock',
    promoText: scrapedData.promoText,
  };

  // Save to database
  await supabase.from('competitors').upsert({
    id: competitorId,
    name,
    url,
    current_price: currentPrice,
    previous_price: previousPrice,
    price_change_percentage: priceChange,
    product_name: competitorData.productName,
    stock_status: competitorData.stockStatus,
    promo_text: competitorData.promoText,
    last_checked: new Date().toISOString(),
  });

  // Log price change history
  if (Math.abs(priceChange) > 1) {
    await supabase.from('competitor_price_history').insert({
      competitor_id: competitorId,
      old_price: previousPrice,
      new_price: currentPrice,
      change_percentage: priceChange,
      detected_at: new Date().toISOString(),
    });
  }

  return competitorData;
}

/**
 * Generate counter-offer suggestion using AI
 */
export async function generateCounterOffer(
  competitorPrice: number,
  ourPrice: number,
  ourCost: number,
  minProfitMargin: number = 15
): Promise<CounterOfferSuggestion> {
  const priceDifference = ((ourPrice - competitorPrice) / competitorPrice) * 100;

  let urgency: CounterOfferSuggestion['urgency'] = 'low';
  let suggestedPrice = ourPrice;
  let reasoning = '';

  // Critical: Competitor is 15%+ cheaper
  if (priceDifference > 15) {
    urgency = 'critical';
    // Match their price but maintain minimum profit
    const matchPrice = competitorPrice * 0.98; // 2% cheaper than competitor
    const profit = matchPrice - ourCost;
    const profitMargin = (profit / matchPrice) * 100;

    if (profitMargin >= minProfitMargin) {
      suggestedPrice = matchPrice;
      reasoning = `⚠️ CRITICAL: Competitor is ${priceDifference.toFixed(1)}% cheaper! Suggested price: ${matchPrice.toFixed(2)} EGP (undercut by 2%)`;
    } else {
      suggestedPrice = ourCost * (1 + minProfitMargin / 100);
      reasoning = `⚠️ Cannot match competitor price without losing profit. Minimum viable price: ${suggestedPrice.toFixed(2)} EGP (${minProfitMargin}% margin)`;
    }
  }
  // High: Competitor is 10-15% cheaper
  else if (priceDifference > 10) {
    urgency = 'high';
    suggestedPrice = competitorPrice * 1.02; // Match +2%
    reasoning = `⚡ HIGH: Competitor is ${priceDifference.toFixed(1)}% cheaper. Suggested: ${suggestedPrice.toFixed(2)} EGP (match +2%)`;
  }
  // Medium: Competitor is 5-10% cheaper
  else if (priceDifference > 5) {
    urgency = 'medium';
    suggestedPrice = competitorPrice * 1.05; // Match +5%
    reasoning = `⚠️ MEDIUM: Competitor is ${priceDifference.toFixed(1)}% cheaper. Suggested: ${suggestedPrice.toFixed(2)} EGP (match +5%)`;
  }
  // Low: We're competitive
  else if (priceDifference > -5) {
    urgency = 'low';
    reasoning = `✅ LOW: Prices are competitive (difference: ${priceDifference.toFixed(1)}%). No action needed.`;
  }
  // We're cheaper
  else {
    urgency = 'low';
    reasoning = `✅ ADVANTAGE: We're ${Math.abs(priceDifference).toFixed(1)}% cheaper! Maintain current pricing.`;
  }

  const discountPercentage = ((ourPrice - suggestedPrice) / ourPrice) * 100;

  const marketingMessages = {
    critical:
      '🔥 عرض صاعق! خصم فوري الآن! سعر لن يتكرر. اطلب خلال ساعة واحصل على شحن مجاني!',
    high: '⚡ عرض خاص اليوم! خصم حصري لعملائنا المميزين. الكمية محدودة!',
    medium: '💰 سعر منافس! جودة أعلى بسعر أفضل. اطلب الآن.',
    low: '✨ منتج مميز بسعر عادل. جودة مضمونة + ضمان سنتين.',
  };

  return {
    suggestedPrice,
    discountPercentage: Math.max(0, discountPercentage),
    reasoning,
    urgency,
    marketingMessage: marketingMessages[urgency],
  };
}

/**
 * Schedule automatic competitor monitoring (cron-like)
 */
export async function scheduleCompetitorMonitoring(
  competitors: Array<{ id: string; name: string; url: string }>,
  intervalMinutes: number = 60
) {
  console.log(`🎯 Starting Competitor Radar - Monitoring ${competitors.length} competitors`);

  const monitorLoop = async () => {
    for (const competitor of competitors) {
      try {
        const data = await monitorCompetitor(
          competitor.id,
          competitor.url,
          competitor.name
        );

        // Alert if significant price change detected
        if (Math.abs(data.priceChange) > 5) {
          console.log(
            `🚨 ALERT: ${competitor.name} price changed by ${data.priceChange.toFixed(1)}%`
          );

          // Generate counter-offer
          const { data: ourProduct } = await supabase
            .from('products')
            .select('price, cost')
            .eq('competitor_tracked', competitor.id)
            .single();

          if (ourProduct) {
            const counterOffer = await generateCounterOffer(
              data.currentPrice,
              ourProduct.price,
              ourProduct.cost
            );

            // Save alert
            await supabase.from('competitor_alerts').insert({
              competitor_id: competitor.id,
              alert_type: 'price_change',
              message: counterOffer.reasoning,
              urgency: counterOffer.urgency,
              suggested_action: JSON.stringify(counterOffer),
              created_at: new Date().toISOString(),
            });

            console.log(`💡 Counter-offer generated:`, counterOffer);
          }
        }
      } catch (error) {
        console.error(`Error monitoring ${competitor.name}:`, error);
      }
    }
  };

  // Run immediately
  await monitorLoop();

  // Schedule periodic runs
  setInterval(monitorLoop, intervalMinutes * 60 * 1000);
}

/**
 * Close browser on shutdown
 */
export async function closeBrowser() {
  if (browser) {
    await browser.close();
    browser = null;
  }
}
