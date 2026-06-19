# Cleaning Rules - Week 1 

## Dataset 

Source file: `01-log-tracking.csv`

Sample used: `log_tracking_1m.csv`

## Profiling Findings

- The sample contains 1,000,000 rows.
- Event types include `view`, `cart`, and `purchase`. 
- `category_code` has about 31.70% missing values.
- `brand` has about 14.70% missing values. 
- `price` has no null values, but 973 rows have price <= 0.
- Duplicate rows based on event_time, 

## Cleaning Rules 

1. Convert `event_time` to timestamp.
2. Create `event_date` from `event_time`. 
3. Normalize `event_type` using lowercase and trim 
4. Keep only valid event types: `view`, `cart`, `purchase`.
5. Remove rows where `event_type` is null. 
6. Remove rows where `product_id` is null. 
7. Remove rows where `user_id` is null. 
8. Remove rows where `price` is null or `price` <= 0. 
9. Replace missing `brand` with `unknown`.
10. Replace missing `category_code` with `unknown`.
11. Drop duplicate rows based on:
    - event_time 
    - event_type
    - product_id
    - user_id
    - user_session
12. Split `category_code` into: 
    - category_level_1
    - category_level_2
    - category_level_3
