-- Business Question 2
-- Top 10 Vendors by Procurement Spend
-- Objective: Identify vendors receiving the highest procurement investment
-- and evaluate their operational risk.

WITH vendor_summary AS (
    SELECT
        vendor_id,
        vendor_name,
        SUM(procurement_spend_usd) AS total_procurement_spend,
        AVG(vris_score) AS vris_score,
        MAX(risk_category) AS risk_category
    FROM read_csv_auto('Data/cleaned/vendors_cleaned.csv')
    GROUP BY
        vendor_id,
        vendor_name
),

financial_transactions AS (
    SELECT
        vendor_id,
        COUNT(finance_record_id) AS number_of_transactions
    FROM read_csv_auto('Data/cleaned/financials_cleaned.csv')
    GROUP BY
        vendor_id
)

SELECT
    v.vendor_name,
    ROUND(v.total_procurement_spend, 2) AS total_procurement_spend,
    ROUND(v.vris_score, 2) AS vris_score,
    v.risk_category,
    COALESCE(f.number_of_transactions, 0) AS number_of_transactions
FROM vendor_summary v
LEFT JOIN financial_transactions f
    ON v.vendor_id = f.vendor_id
ORDER BY
    v.total_procurement_spend DESC
LIMIT 10;


-- Business Question 3
-- Product Categories with Highest Stockout Rate
-- Objective: Determine which product categories experience the highest
-- inventory shortages across warehouses.

WITH category_stockout_summary AS (
    SELECT
        product_category,
        COUNT(DISTINCT product_id) AS total_products,
        COUNT(DISTINCT CASE
            WHEN stock_on_hand <= 0 THEN product_id
        END) AS stockout_count,
        COUNT(DISTINCT warehouse_id) AS warehouse_distribution
    FROM read_csv_auto('Data/cleaned/inventory_cleaned.csv')
    GROUP BY
        product_category
)

SELECT
    product_category,
    total_products,
    stockout_count,
    ROUND(
        (stockout_count * 100.0) / NULLIF(total_products, 0),
        2
    ) AS stockout_percentage,
    warehouse_distribution
FROM category_stockout_summary
ORDER BY
    stockout_percentage DESC,
    stockout_count DESC;



 -- Business Question 5
-- Cash Conversion Cycle (CCC)
-- Objective: Evaluate working capital efficiency by identifying fiscal quarters
-- with poor liquidity performance.

WITH quarterly_ccc AS (
    SELECT
        fiscal_year,
        fiscal_quarter,

        AVG(days_sales_outstanding) AS days_sales_outstanding,

        AVG(
            cash_conversion_cycle
            - days_sales_outstanding
            + days_payable_outstanding
        ) AS days_inventory_outstanding,

        AVG(days_payable_outstanding) AS days_payable_outstanding,

        AVG(cash_conversion_cycle) AS cash_conversion_cycle
    FROM read_csv_auto('Data/cleaned/financials_cleaned.csv')
    GROUP BY
        fiscal_year,
        fiscal_quarter
)

SELECT
    fiscal_year,
    fiscal_quarter,
    ROUND(days_sales_outstanding, 2) AS days_sales_outstanding,
    ROUND(days_inventory_outstanding, 2) AS days_inventory_outstanding,
    ROUND(days_payable_outstanding, 2) AS days_payable_outstanding,
    ROUND(cash_conversion_cycle, 2) AS cash_conversion_cycle
FROM quarterly_ccc
ORDER BY
    cash_conversion_cycle DESC;

-- Business Question 6
-- Customer Segment Profitability
-- Objective: Determine which customer segments generate the highest gross margins.

WITH segment_profitability AS (
    SELECT
        customer_segment,

        COUNT(DISTINCT order_id) AS total_orders,
        SUM(order_value_usd) AS revenue,
        SUM(gross_margin_usd) AS gross_margin,

        ROUND(
            AVG(profit_margin_pct),
            2
        ) AS profit_margin_percentage,

        ROUND(
            SUM(order_value_usd) / NULLIF(COUNT(DISTINCT order_id), 0),
            2
        ) AS average_order_value
    FROM read_csv_auto('Data/cleaned/orders_cleaned.csv')
    GROUP BY
        customer_segment
)

SELECT
    customer_segment,
    total_orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(gross_margin, 2) AS gross_margin,
    profit_margin_percentage,
    average_order_value
FROM segment_profitability
ORDER BY
    gross_margin DESC;

    -- Business Question 8
-- Warehouse Excess Inventory Analysis
-- Objective: Identify warehouses holding inventory above maximum stock levels.

WITH warehouse_excess_inventory AS (
    SELECT
        warehouse_id,

        SUM(
            CASE
                WHEN stock_on_hand > max_stock_level
                THEN stock_on_hand - max_stock_level
                ELSE 0
            END
        ) AS excess_units,

        SUM(
            CASE
                WHEN stock_on_hand > max_stock_level
                THEN (stock_on_hand - max_stock_level) * unit_cost_usd
                ELSE 0
            END
        ) AS excess_value
    FROM read_csv_auto('Data/cleaned/inventory_cleaned.csv')
    GROUP BY
        warehouse_id
)

SELECT
    warehouse_id,
    excess_units,
    ROUND(excess_value, 2) AS excess_value,
    RANK() OVER (
        ORDER BY excess_value DESC
    ) AS warehouse_ranking
FROM warehouse_excess_inventory
WHERE excess_units > 0
ORDER BY
    warehouse_ranking;


    -- Business Question 9
-- Vendors with Contract Expiry
-- Objective: Identify vendors whose contracts expire within six months.

WITH vendor_contracts AS (
    SELECT
        vendor_id,
        vendor_name,
        CAST(contract_expiry_date AS DATE) AS expiry_date,
        risk_category,
        procurement_spend_usd
    FROM read_csv_auto('Data/cleaned/vendors_cleaned.csv')
)

SELECT
    vendor_name AS vendor,
    expiry_date,
    risk_category,
    ROUND(procurement_spend_usd, 2) AS procurement_spend
FROM vendor_contracts
WHERE expiry_date >= CURRENT_DATE
  AND expiry_date <= CURRENT_DATE + INTERVAL 6 MONTH
ORDER BY
    expiry_date ASC,
    procurement_spend DESC;

-- Business Question 10
-- Weekly Cash Flow Volatility
-- Objective: Evaluate fluctuations in operational cash flow.

WITH weekly_cash_flow AS (
    SELECT
        fiscal_year,
        fiscal_week,
        SUM(cash_flow_usd) AS weekly_cash_flow
    FROM read_csv_auto('Data/cleaned/financials_cleaned.csv')
    GROUP BY
        fiscal_year,
        fiscal_week
),

cash_flow_volatility AS (
    SELECT
        fiscal_year,
        fiscal_week,
        weekly_cash_flow,

        STDDEV_SAMP(weekly_cash_flow) OVER (
            ORDER BY fiscal_year, fiscal_week
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_cash_flow_stddev,

        AVG(ABS(weekly_cash_flow)) OVER (
            ORDER BY fiscal_year, fiscal_week
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_average_cash_flow
    FROM weekly_cash_flow
)

SELECT
    fiscal_year,
    fiscal_week,
    ROUND(weekly_cash_flow, 2) AS weekly_cash_flow,
    ROUND(rolling_cash_flow_stddev, 2) AS standard_deviation,

    ROUND(
        rolling_cash_flow_stddev
        / NULLIF(rolling_average_cash_flow, 0),
        4
    ) AS volatility_ratio,

    CASE
        WHEN rolling_cash_flow_stddev IS NULL THEN 'Insufficient History'
        WHEN rolling_cash_flow_stddev / NULLIF(rolling_average_cash_flow, 0) >= 0.75
            THEN 'High Volatility'
        WHEN rolling_cash_flow_stddev / NULLIF(rolling_average_cash_flow, 0) >= 0.35
            THEN 'Medium Volatility'
        ELSE 'Low Volatility'
    END AS volatility_trend
FROM cash_flow_volatility
ORDER BY
    fiscal_year,
    fiscal_week;