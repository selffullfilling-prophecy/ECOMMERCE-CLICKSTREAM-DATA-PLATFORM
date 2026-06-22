# Business Questions

## 1. Business Objective

Analyze e-commerce clickstream behavior to identify business opportunities for improving revenue, conversion, customer retention, brand performance, and customer segmentation.

The analysis focuses on how users move from product views to cart additions and purchases, how sales performance changes over time, which brands and categories dominate the market, and which customer groups should be prioritized for business actions.

## 2. Target Audience

The primary audience is the Sales / E-commerce Business team.

Secondary audiences include:

- Marketing team
- Product / merchandising team
- Management team

## 3. Analysis Scope

The project uses clickstream event data with the following core fields:

- `event_time`
- `event_date`
- `event_type`: `view`, `cart`, `purchase`
- `product_id`
- `category_id`
- `category_code`
- `category_level_1`
- `category_level_2`
- `category_level_3`
- `brand`
- `price`
- `user_id`
- `user_session`

The current 1M-row Silver sample is suitable for validating the pipeline and performing funnel, brand, category, product, hourly, and session-level analysis.

For long-term analysis such as weekly cohort retention, RFM segmentation, and multi-day sales lag analysis, the analysis should be run on a broader time range or the full 67.5M-row dataset.

## 4. Core Analysis Tracks

## Track 1: Sales Trend and Purchase Lag

### Business Goal

Understand when revenue, views, carts, and purchases peak, and whether user interest usually appears before purchases.

### Business Questions

1. How do views, carts, purchases, and revenue change by day and by hour?
2. Which days or hours have unusually high views, carts, purchases, or revenue?
3. Do increases in views or carts happen before increases in purchases?
4. Is revenue growth driven more by purchase volume or by higher purchase value?
5. Are there periods where carts increase but purchases do not follow?

### Expected Outputs

- `gold_daily_sales_trend`
- `gold_hourly_behavior`
- `gold_event_funnel`

### Business Actions

- Identify peak shopping periods for promotions.
- Detect periods with high interest but weak purchase conversion.
- Support campaign timing and merchandising decisions.

---

## Track 2: Weekly Cohort Retention

### Business Goal

Measure whether customers who make their first purchase in a given week return and purchase again in later weeks.

### Business Questions

1. Which week did each purchasing user make their first purchase?
2. How many users are in each first-purchase cohort?
3. What percentage of users return to purchase in week 1, week 2, week 3, and later weeks?
4. Which cohorts retain customers better?
5. How quickly does purchase engagement decline after the first purchase?

### Expected Outputs

- `gold_cohort_retention`

### Business Actions

- Evaluate customer retention quality by acquisition period.
- Detect engagement decline after first purchase.
- Support post-purchase marketing and retention campaigns.

### Data Requirement

This analysis requires multiple weeks of purchase data. A one-day sample is not enough for reliable weekly cohort analysis.

---

## Track 3: Market Preferences

### Business Goal

Compare brand, category, and product performance to understand customer preferences and revenue drivers.

### Business Questions

1. Which brands generate the most revenue?
2. Which brands have the highest purchase volume?
3. Which brands have high views but low conversion?
4. Which categories dominate views, purchases, and revenue?
5. Do premium brands generate higher revenue because of higher purchase price or higher purchase volume?
6. How do major brands such as Apple, Samsung, and Xiaomi differ in revenue, purchase count, and average purchase price?
7. Which products are viewed frequently but purchased rarely?

### Expected Outputs

- `gold_brand_performance`
- `gold_category_performance`
- `gold_product_performance`

### Business Actions

- Identify high-value brands and categories.
- Find products with strong interest but weak conversion.
- Support pricing, promotion, and product placement decisions.

---

## Track 4: RFM Customer Segmentation

### Business Goal

Segment customers based on purchase recency, purchase frequency, and monetary value to support targeted marketing actions.

### Business Questions

1. Which users purchased most recently?
2. Which users purchase most frequently?
3. Which users generate the most revenue?
4. Which users can be classified as Champions, Loyal Customers, Potential Loyalists, At Risk, or Lost?
5. Which customer segments contribute the most revenue?
6. Which customer segments should be prioritized for retention or reactivation campaigns?

### Expected Outputs

- `gold_rfm_segments`

### Business Actions

- Prioritize high-value customers.
- Identify at-risk users for remarketing.
- Support customer segmentation and campaign targeting.

### Data Requirement

RFM analysis requires a meaningful purchase history. A one-day sample can validate the calculation logic, but full or multi-week data is needed for reliable customer segmentation.

---

## 5. Supporting Analysis

## 5.1 Funnel and Conversion

### Business Questions

1. What is the overall view → cart → purchase funnel?
2. What is the view-to-cart rate?
3. What is the cart-to-purchase rate?
4. What is the view-to-purchase rate?
5. Which categories or brands lose the most users between cart and purchase?

### Expected Output

- `gold_event_funnel`
- `gold_category_performance`
- `gold_brand_performance`

---

## 5.2 Product Performance

### Business Questions

1. Which products are most viewed?
2. Which products are most added to cart?
3. Which products are most purchased?
4. Which products have high views but low purchase conversion?
5. Which products generate the most revenue?

### Expected Output

- `gold_product_performance`

---

## 5.3 Session Behavior

### Business Questions

1. How do purchase sessions differ from non-purchase sessions?
2. Do purchase sessions contain more events than non-purchase sessions?
3. How long do purchase sessions usually last?
4. How many views and carts usually occur in purchase sessions?
5. What percentage of sessions contain at least one purchase?

### Expected Output

- `gold_session_summary`

---

## 6. Expected Gold Analytics Tables

| Gold Table | Purpose |
|---|---|
| `gold_event_funnel` | Analyze the overall view → cart → purchase funnel |
| `gold_daily_sales_trend` | Analyze daily views, carts, purchases, revenue, and conversion |
| `gold_hourly_behavior` | Analyze user behavior and revenue by hour |
| `gold_category_performance` | Compare category-level views, carts, purchases, revenue, and conversion |
| `gold_brand_performance` | Compare brand-level views, carts, purchases, revenue, and conversion |
| `gold_product_performance` | Identify top products and high-view low-purchase products |
| `gold_session_summary` | Compare purchase and non-purchase sessions |
| `gold_rfm_segments` | Segment customers by recency, frequency, and monetary value |
| `gold_cohort_retention` | Analyze weekly customer purchase retention |

---

## 7. Data Limitations

The dataset does not include:

- `order_id`
- marketing channel
- campaign source
- customer demographics
- inventory data
- customer service tickets
- delivery or fulfillment information

Because `order_id` is not available, average order value should not be used as a primary KPI. The analysis uses average purchase price or revenue per purchasing user instead.

Because marketing source data is not available, marketing attribution analysis is outside the current scope.

Because customer service data is not available, customer service performance analysis is outside the current scope.

Because the current 1M-row sample covers only one day, weekly cohort retention and long-term RFM insights should be validated on a broader time range or the full dataset.
