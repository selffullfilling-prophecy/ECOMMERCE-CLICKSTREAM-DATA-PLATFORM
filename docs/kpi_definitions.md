# KPI Definitions

## 1. General Notes

This project analyzes e-commerce clickstream events with three main event types:

- `view`
- `cart`
- `purchase`

Unless otherwise stated:

- `views` means the number of rows where `event_type = 'view'`.
- `carts` means the number of rows where `event_type = 'cart'`.
- `purchases` means the number of rows where `event_type = 'purchase'`.
- `revenue` means `sum(price)` for purchase events only.

The dataset does not contain `order_id`, so standard Average Order Value (AOV) should not be used directly. This project uses `average_purchase_price` or `revenue_per_purchasing_user` instead.

Important interpretation notes:

- Most conversion rates in this project are event-level ratios, not user-level conversion rates.
- For example, `view_to_purchase_rate = purchases / views` means purchase events divided by view events. It should not be interpreted as “X% of users who viewed purchased.”
- In implementation, the column name `revenue_share` can be reused across Gold tables. Its meaning depends on the table level:
  - In `gold_brand_performance`, it means brand revenue share.
  - In `gold_category_performance`, it means category revenue share.
  - In `gold_product_performance`, it means product revenue share.

## 2. Funnel and Conversion KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Views | `count(*) where event_type = 'view'` | Number of product view events | `gold_event_funnel`, `gold_category_performance`, `gold_brand_performance` |
| Carts | `count(*) where event_type = 'cart'` | Number of add-to-cart events | `gold_event_funnel`, `gold_category_performance`, `gold_brand_performance` |
| Purchases | `count(*) where event_type = 'purchase'` | Number of purchase events | `gold_event_funnel`, `gold_category_performance`, `gold_brand_performance` |
| View-to-cart event rate | `carts / views` | Ratio of cart events to view events | `gold_event_funnel` |
| Cart-to-purchase event rate | `purchases / carts` | Ratio of purchase events to cart events | `gold_event_funnel` |
| View-to-purchase event rate | `purchases / views` | Ratio of purchase events to view events | `gold_event_funnel` |

### Interpretation Notes

A low view-to-cart event rate may indicate weak product appeal, pricing issues, poor product information, or low purchase intent.

A low cart-to-purchase event rate may indicate checkout friction, price sensitivity, shipping concerns, or lack of trust.

Because these are event-level ratios, they should be interpreted as behavioral signals, not exact user conversion percentages.

## 3. Sales Trend KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Daily views | `count(view events) group by event_date` | Daily browsing demand | `gold_daily_sales_trend` |
| Daily carts | `count(cart events) group by event_date` | Daily product consideration | `gold_daily_sales_trend` |
| Daily purchases | `count(purchase events) group by event_date` | Daily purchase volume | `gold_daily_sales_trend` |
| Daily revenue | `sum(price) where event_type = 'purchase' group by event_date` | Estimated daily revenue | `gold_daily_sales_trend` |
| Daily view-to-purchase event rate | `daily_purchases / daily_views` | Daily purchase-to-view ratio | `gold_daily_sales_trend` |
| Daily cart-to-purchase event rate | `daily_purchases / daily_carts` | Daily purchase-to-cart ratio | `gold_daily_sales_trend` |
| Daily average purchase price | `daily_revenue / daily_purchases` | Average purchase price per day | `gold_daily_sales_trend` |

### Purchase Lag Analytical Metrics

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| First view before purchase lag | `purchase_time - first_prior_view_time` within same user/product/session or user/product | Time between first product view and purchase | future enhancement |
| Last cart before purchase lag | `purchase_time - last_prior_cart_time` within same user/product/session or user/product | Time between cart action and purchase | future enhancement |
| Lagged view signal | Compare previous-day views with later purchases or revenue | Whether product interest tends to appear before revenue | `gold_daily_sales_trend` |
| Lagged cart signal | Compare previous-day carts with later purchases or revenue | Whether cart activity tends to appear before revenue | `gold_daily_sales_trend` |

### Interpretation Notes

Purchase lag analysis requires multiple days of data. A one-day sample is not enough to determine whether users view or cart products 2–3 days before purchasing.

## 4. Revenue and Customer Value KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Revenue | `sum(price) where event_type = 'purchase'` | Estimated revenue from purchase events | `gold_daily_sales_trend`, `gold_brand_performance`, `gold_category_performance` |
| Average purchase price | `revenue / purchases` | Average price per purchase event | `gold_brand_performance`, `gold_category_performance`, `gold_product_performance` |
| Revenue per purchasing user | `revenue / distinct purchasing users` | Average revenue generated per purchasing user | `gold_rfm_segments` |

### Interpretation Notes

Revenue share is not listed as a generic KPI here to avoid duplication. It is defined specifically at each analysis level in the Market Preference and Product Performance sections.

## 5. Market Preference KPIs

### 5.1 Brand Performance KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Brand views | `count(view events) group by brand` | Brand interest | `gold_brand_performance` |
| Brand carts | `count(cart events) group by brand` | Brand consideration | `gold_brand_performance` |
| Brand purchases | `count(purchase events) group by brand` | Brand purchase volume | `gold_brand_performance` |
| Brand revenue | `sum(price) where purchase group by brand` | Brand revenue contribution | `gold_brand_performance` |
| Brand average purchase price | `brand_revenue / brand_purchases` | Premium or low-price purchase profile | `gold_brand_performance` |
| Brand view-to-purchase event rate | `brand_purchases / brand_views` | Brand purchase-to-view ratio | `gold_brand_performance` |
| Brand revenue share | `brand_revenue / total_revenue` | Percentage contribution of each brand to total revenue | `gold_brand_performance` |
### 5.2 Category Performance KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Category views | `count(view events) group by category` | Category interest | `gold_category_performance` |
| Category carts | `count(cart events) group by category` | Category consideration | `gold_category_performance` |
| Category purchases | `count(purchase events) group by category` | Category purchase volume | `gold_category_performance` |
| Category revenue | `sum(price) where purchase group by category` | Category revenue contribution | `gold_category_performance` |
| Category average purchase price | `category_revenue / category_purchases` | Average purchase price for each category | `gold_category_performance` |
| Category view-to-purchase event rate | `category_purchases / category_views` | Category purchase-to-view ratio | `gold_category_performance` |
| Category revenue share | `category_revenue / total_revenue` | Percentage contribution of each category to total revenue | `gold_category_performance` |

### Interpretation Notes

A brand can lead in purchase count but not revenue if its average purchase price is lower.

A brand can lead in revenue but not purchase count if it sells higher-priced products.

Revenue share and average purchase price are different:

- Revenue share measures contribution to total revenue.
- Average purchase price measures value per purchase event.

## 6. Product Performance KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Product views | `count(view events) group by product_id` | Product interest | `gold_product_performance` |
| Product carts | `count(cart events) group by product_id` | Product consideration | `gold_product_performance` |
| Product purchases | `count(purchase events) group by product_id` | Product sales volume | `gold_product_performance` |
| Product revenue | `sum(price) where purchase group by product_id` | Product revenue contribution | `gold_product_performance` |
| Product view-to-purchase event rate | `product_purchases / product_views` | Product purchase-to-view ratio | `gold_product_performance` |
| Product revenue share | `product_revenue / total_revenue` | Percentage contribution of each product to total revenue | `gold_product_performance` |
| High-view low-purchase flag | high product views and low product purchases/conversion | Products with possible conversion issues | `gold_product_performance` |

### Interpretation Notes

The high-view low-purchase flag is a business rule, not a universal KPI. The threshold should be adjusted after reviewing the actual distribution of product views and conversion rates.

## 7. Time Behavior KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Views by hour | `count(view events) group by hour(event_time)` | Peak browsing hours | `gold_hourly_behavior` |
| Carts by hour | `count(cart events) group by hour(event_time)` | Peak consideration hours | `gold_hourly_behavior` |
| Purchases by hour | `count(purchase events) group by hour(event_time)` | Peak buying hours | `gold_hourly_behavior` |
| Revenue by hour | `sum(price) where purchase group by hour(event_time)` | Peak revenue hours | `gold_hourly_behavior` |
| Hourly view-to-purchase event rate | `hourly_purchases / hourly_views` | Purchase-to-view ratio by hour | `gold_hourly_behavior` |

### Interpretation Notes

Hourly view-to-purchase event rate helps compare traffic quality by hour. A high-view hour is not always the best conversion hour.

## 8. Session Behavior KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Session start time | `min(event_time) by user_session` | When the session started | `gold_session_summary` |
| Session end time | `max(event_time) by user_session` | When the session ended | `gold_session_summary` |
| Session duration minutes | `(session_end - session_start) / 60` | How long the session lasted | `gold_session_summary` |
| Events per session | `count(*) by user_session` | Session engagement level | `gold_session_summary` |
| View count per session | `count(view events) by user_session` | Product browsing depth | `gold_session_summary` |
| Cart count per session | `count(cart events) by user_session` | Purchase consideration depth | `gold_session_summary` |
| Purchase count per session | `count(purchase events) by user_session` | Purchase activity in session | `gold_session_summary` |
| Has purchase | `purchase_count > 0` | Whether the session converted | `gold_session_summary` |
| Session revenue | `sum(price) where purchase by user_session` | Revenue generated by session | `gold_session_summary` |
| Purchase session rate | `purchase sessions / total sessions` | Percentage of sessions that contain at least one purchase event | `gold_session_summary` |

### Interpretation Notes

Purchase session rate is session-level, while view-to-purchase event rate is event-level. These two metrics answer different questions.

## 9. Weekly Cohort Retention KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| First purchase week | `week(min(purchase event_time)) by user_id` | User's first purchase cohort | `gold_cohort_retention` |
| Purchase week | `week(purchase event_time)` | Week of each purchase | `gold_cohort_retention` |
| Weeks after first purchase | `floor(datediff(purchase_date, first_purchase_date) / 7)` | Number of weeks after first purchase | `gold_cohort_retention` |
| Cohort size | `distinct users where weeks_after = 0` | Number of first-time purchasing users in cohort | `gold_cohort_retention` |
| Returning users | `distinct users in each weeks_after` | Users who purchased again after first purchase | `gold_cohort_retention` |
| Retention rate | `returning_users / cohort_size` | Percentage of users retained after first purchase | `gold_cohort_retention` |

### Interpretation Notes

Weekly cohort retention requires multiple weeks of data. A one-day sample can only validate the pipeline structure, not generate meaningful retention insights.

## 10. RFM KPIs

| KPI | Formula | Business Meaning | Main Gold Tables |
|---|---|---|---|
| Last purchase date | `max(event_date) where purchase by user_id` | Most recent purchase date | `gold_rfm_segments` |
| Recency | `analysis_date - last_purchase_date` | How recently the user purchased | `gold_rfm_segments` |
| Frequency | `count(purchase events) by user_id` | How often the user purchased | `gold_rfm_segments` |
| Monetary | `sum(price) where purchase by user_id` | Total user spending | `gold_rfm_segments` |
| R score | Quantile score where higher score means more recent purchase | Recency ranking | `gold_rfm_segments` |
| F score | Quantile score where higher score means higher purchase frequency | Frequency ranking | `gold_rfm_segments` |
| M score | Quantile score where higher score means higher monetary value | Monetary ranking | `gold_rfm_segments` |
| RFM segment | Rule-based grouping using R, F, M scores | Customer segment for business action | `gold_rfm_segments` |

### Suggested RFM Segments

| Segment | Rule Example | Business Meaning |
|---|---|---|
| Champions | High R, high F, high M | Best customers |
| Loyal Customers | Medium/high R and high F | Repeat customers |
| Potential Loyalists | High R but medium F/M | Recent customers with growth potential |
| At Risk | Low R but previously high F/M | Valuable customers who have not returned recently |
| Lost | Low R, low F, low M | Low recent value and low engagement |
| Low Value | Low F and low M | Low-value customers |

### Interpretation Notes

RFM segmentation requires a meaningful historical period. It should be interpreted carefully when using a one-day sample.

## 11. Data Limitations

The dataset does not include:

- order identifiers
- traffic source
- campaign source
- customer demographic attributes
- inventory data
- customer service tickets
- delivery or fulfillment status

As a result:

- Average Order Value should not be used as a primary metric.
- Marketing attribution is outside the current scope.
- Customer service performance analysis is outside the current scope.
- Long-term retention and RFM insights should be run on multi-week or full data.
