import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# MYSQL DATABASE CONNECTION
# ============================================================

username = "root"
password = "Ammu@181296"
host = "localhost"
port = 3306
database = "olist_ecommerce"

encoded_password = quote_plus(password)

engine = create_engine(
    f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}"
)

# ============================================================
# FUNCTION TO RUN SQL QUERIES
# ============================================================


@st.cache_data
def run_query(query):
    return pd.read_sql(query, engine)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown("## 🔎 Dashboard Filters")
st.sidebar.caption("Filter the dashboard by order year")

year_query = """
SELECT DISTINCT
    YEAR(order_purchase_timestamp) AS order_year
FROM orders
WHERE order_purchase_timestamp IS NOT NULL
ORDER BY order_year;
"""

years = run_query(year_query)

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + years["order_year"].astype(str).tolist()
)
# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🛒 Olist E-Commerce Dashboard")

st.caption(
    "Brazilian E-Commerce Performance Analysis | "
    "Sales • Customers • Sellers • Delivery • Reviews"
)

st.markdown("---")

st.markdown("## 📊 Business Overview")


# ============================================================
# KPI 1 — TOTAL REVENUE
# ============================================================

revenue_query = """
SELECT ROUND(SUM(price), 2) AS total_revenue
FROM order_items;
"""

revenue = run_query(revenue_query)["total_revenue"].iloc[0]


# ============================================================
# KPI 2 — TOTAL ORDERS
# ============================================================

orders_query = """
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM orders;
"""

total_orders = run_query(orders_query)["total_orders"].iloc[0]


# ============================================================
# KPI 3 — TOTAL CUSTOMERS
# ============================================================

customers_query = """
SELECT COUNT(DISTINCT customer_unique_id) AS total_customers
FROM customers;
"""

total_customers = run_query(customers_query)["total_customers"].iloc[0]


# ============================================================
# KPI 4 — TOTAL SELLERS
# ============================================================

sellers_query = """
SELECT COUNT(DISTINCT seller_id) AS total_sellers
FROM sellers;
"""

total_sellers = run_query(sellers_query)["total_sellers"].iloc[0]


# ============================================================
# KPI 5 — AVERAGE ORDER VALUE
# ============================================================

aov_query = """
WITH order_totals AS (
    SELECT
        order_id,
        SUM(price) AS order_value
    FROM order_items
    GROUP BY order_id
)

SELECT ROUND(AVG(order_value), 2) AS average_order_value
FROM order_totals;
"""

aov = run_query(aov_query)["average_order_value"].iloc[0]


# ============================================================
# KPI 6 — AVERAGE REVIEW SCORE
# ============================================================

review_query = """
SELECT ROUND(AVG(review_score), 2) AS average_review_score
FROM order_reviews;
"""

average_review = run_query(review_query)["average_review_score"].iloc[0]


# ============================================================
# DISPLAY KPI CARDS
# ============================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="💰 Revenue",
        value=f"₹{revenue / 10000000:.2f} Cr"
    )

with col2:
    st.metric(
        label="🛒 Orders",
        value=f"{total_orders:,}"
    )

with col3:
    st.metric(
        label="👥 Customers",
        value=f"{total_customers:,}"
    )

with col4:
    st.metric(
        label="🏪 Sellers",
        value=f"{total_sellers:,}"
    )

with col5:
    st.metric(
        label="💳 AOV",
        value=f"₹{aov:,.2f}"
    )

with col6:
    st.metric(
        label="⭐ Avg Review",
        value=f"{average_review:.2f} / 5"
    )

    st.markdown("")
st.markdown("---")
    # ============================================================
# SALES ANALYSIS
# ============================================================

st.header("📈 Sales Analysis")


st.subheader("Monthly Revenue Trend")

monthly_revenue_query = """
SELECT
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
"""

if selected_year != "All":
    monthly_revenue_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

monthly_revenue_query += """
GROUP BY
    YEAR(o.order_purchase_timestamp),
    MONTH(o.order_purchase_timestamp)
ORDER BY
    order_year,
    order_month;
"""

monthly_revenue = run_query(monthly_revenue_query)

# ============================================================
# PREPARE MONTHLY REVENUE DATA FOR CHART
# ============================================================

monthly_revenue["month"] = pd.to_datetime(
    monthly_revenue["order_year"].astype(str)
    + "-"
    + monthly_revenue["order_month"].astype(str)
    + "-01"
)

# Create a readable month label
monthly_revenue["month_label"] = monthly_revenue["month"].dt.strftime("%b %Y")


# ============================================================
# MONTHLY REVENUE CHART
# ============================================================

st.line_chart(
    monthly_revenue.set_index("month_label")["monthly_revenue"],
    height=450
)

# ============================================================
# REVENUE BY PRODUCT CATEGORY
# ============================================================


st.subheader("📊 Revenue by Product Category")

category_revenue_query = """
SELECT
    p.product_category_name AS product_category,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
"""

if selected_year != "All":
    category_revenue_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

category_revenue_query += """
GROUP BY
    p.product_category_name
ORDER BY
    total_revenue DESC
LIMIT 10;
"""

category_revenue = run_query(category_revenue_query)

# ============================================================
# REVENUE BY PRODUCT CATEGORY CHART
# ============================================================

st.bar_chart(
    category_revenue.set_index("product_category")["total_revenue"],
    height=450
)

# ============================================================
# TOP-SELLING PRODUCTS
# ============================================================

st.subheader("🏆 Top 10 Best-Selling Products")

top_products_query = """
SELECT
    oi.product_id,
    p.product_category_name AS product_category,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS product_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
"""

if selected_year != "All":
    top_products_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

top_products_query += """
GROUP BY
    oi.product_id,
    p.product_category_name
ORDER BY
    units_sold DESC
LIMIT 10;
"""

top_products = run_query(top_products_query)

# Create short product labels for presentation
top_products["product_label"] = (
    top_products["product_id"].str[:8] + "..."
)

st.bar_chart(
    top_products.set_index("product_label")["units_sold"],
    height=400
)

# ============================================================
# SALES BY CUSTOMER STATE
# ============================================================

st.subheader("📍 Sales by Customer State")

sales_state_query = """
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
"""

if selected_year != "All":
    sales_state_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

sales_state_query += """
GROUP BY
    c.customer_state
ORDER BY
    total_revenue DESC;
"""

sales_state = run_query(sales_state_query)

# ============================================================
# SALES BY CUSTOMER STATE CHART
# ============================================================

st.bar_chart(
    sales_state.set_index("customer_state")["total_revenue"],
    height=450
)
# ============================================================
# CUSTOMER ANALYSIS
# ============================================================


st.header("👥 Customer Analysis")

st.subheader("👥 Customer Distribution by State")

customer_state_query = """
SELECT
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) AS customer_count
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
"""

if selected_year != "All":
    customer_state_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

customer_state_query += """
GROUP BY
    c.customer_state
ORDER BY
    customer_count DESC;
"""

customer_state = run_query(customer_state_query)

# ============================================================
# CUSTOMER DISTRIBUTION BY STATE CHART
# ============================================================

st.bar_chart(
    customer_state.set_index("customer_state")["customer_count"],
    height=450
)
# ============================================================
# TOP 10CUSTOMERS BY SPENDING
# ============================================================
st.subheader("💰 Top 10 Customers by Spending")

top_customers_query = """
WITH order_totals AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS order_value
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
"""

if selected_year != "All":
    top_customers_query += f"""
    WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

top_customers_query += """
    GROUP BY oi.order_id
)

SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(ot.order_value), 2) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_totals ot
    ON o.order_id = ot.order_id
GROUP BY
    c.customer_unique_id
ORDER BY
    total_spending DESC
LIMIT 10;
"""

top_customers = run_query(top_customers_query)

# ============================================================
# TOP 10 CUSTOMERS BY SPENDING CHART
# ============================================================

# Create short customer labels for presentation
top_customers["customer_label"] = (
    top_customers["customer_unique_id"].str[:8] + "..."
)

st.bar_chart(
    top_customers.set_index("customer_label")["total_spending"],
    height=450
)

# ============================================================
# REPEAT VS ONE-TIME CUSTOMERS
# ============================================================

st.subheader("🔁 Repeat vs One-Time Customers")

repeat_customer_query = """
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END AS customer_type,
    COUNT(*) AS customer_count
FROM (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
"""

if selected_year != "All":
    repeat_customer_query += f"""
    WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

repeat_customer_query += """
    GROUP BY
        c.customer_unique_id
) AS customer_orders

GROUP BY
    CASE
        WHEN order_count = 1 THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END

ORDER BY
    customer_count DESC;
"""

repeat_customers = run_query(repeat_customer_query)

# ============================================================
# REPEAT VS ONE-TIME CUSTOMERS CHART
# ============================================================

st.bar_chart(
    repeat_customers.set_index("customer_type")["customer_count"],
    height=400
)
# ============================================================
# SELLER & PRODUCT ANALYSIS
# ============================================================

st.header("🏪 Seller & Product Analysis")

st.subheader("🏆 Top 10 Sellers by Revenue")

top_sellers_query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
"""

if selected_year != "All":
    top_sellers_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

top_sellers_query += """
GROUP BY
    oi.seller_id
ORDER BY
    total_revenue DESC
LIMIT 10;
"""

top_sellers = run_query(top_sellers_query)

# ============================================================
# TOP 10 SELLERS BY REVENUE CHART
# ============================================================

# Create short seller labels for presentation
top_sellers["seller_label"] = (
    top_sellers["seller_id"].str[:8] + "..."
)

st.bar_chart(
    top_sellers.set_index("seller_label")["total_revenue"],
    height=450
)

# ============================================================
# TOP SELLERS BY RATING
# ============================================================

st.subheader("⭐ Top 10 Sellers by Average Rating")

seller_rating_query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN order_reviews r
    ON oi.order_id = r.order_id
"""

if selected_year != "All":
    seller_rating_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

seller_rating_query += """
GROUP BY
    oi.seller_id
HAVING
    COUNT(DISTINCT oi.order_id) >= 10
ORDER BY
    average_review_score DESC
LIMIT 10;
"""

seller_ratings = run_query(seller_rating_query)

# ============================================================
# TOP 10 SELLERS BY AVERAGE RATING CHART
# ============================================================

# Create short seller labels for presentation
seller_ratings["seller_label"] = (
    seller_ratings["seller_id"].str[:8] + "..."
)

st.bar_chart(
    seller_ratings.set_index("seller_label")["average_review_score"],
    height=450
)
# ============================================================
# PRODUCT CATEGORY PERFORMANCE
# ============================================================

st.subheader("📦 Product Category Performance")

category_performance_query = """
SELECT
    p.product_category_name AS product_category,
    COUNT(*) AS items_sold,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_item_price
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
"""

if selected_year != "All":
    category_performance_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

category_performance_query += """
GROUP BY
    p.product_category_name
ORDER BY
    items_sold DESC
LIMIT 10;
"""

category_performance = run_query(category_performance_query)

# ============================================================
# PRODUCT CATEGORY PERFORMANCE CHART
# ============================================================

st.bar_chart(
    category_performance.set_index("product_category")["items_sold"],
    height=450
)
# ============================================================
# DELIVERY ANALYSIS
# ============================================================


st.header("🚚 Delivery Analysis")

st.subheader("⏱️ Average Delivery Time")

average_delivery_query = """
SELECT
    ROUND(
        AVG(
            DATEDIFF(
                order_delivered_customer_date,
                order_purchase_timestamp
            )
        ),
        2
    ) AS average_delivery_days
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
"""

if selected_year != "All":
    average_delivery_query += f"""
AND YEAR(order_purchase_timestamp) = {int(selected_year)}
"""

average_delivery = run_query(average_delivery_query)

st.metric(
    label="Average Delivery Time",
    value=f"{average_delivery['average_delivery_days'].iloc[0]:.2f} days"
)
# ============================================================
# ON-TIME VS LATE DELIVERIES
# ============================================================

st.subheader("🚚 On-Time vs Late Deliveries")

delivery_performance_query = """
SELECT
    CASE
        WHEN order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN order_delivered_customer_date > order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END AS delivery_performance,

    COUNT(*) AS order_count

FROM orders
"""

if selected_year != "All":
    delivery_performance_query += f"""
WHERE YEAR(order_purchase_timestamp) = {int(selected_year)}
"""

delivery_performance_query += """
GROUP BY
    CASE
        WHEN order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN order_delivered_customer_date > order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END

ORDER BY
    order_count DESC;
"""

delivery_performance = run_query(delivery_performance_query)

# ============================================================
# ON-TIME VS LATE DELIVERIES CHART
# ============================================================

st.bar_chart(
    delivery_performance.set_index("delivery_performance")["order_count"],
    height=400
)
# ============================================================
# DELIVERY PERFORMANCE BY STATE
# ============================================================

st.subheader("📍 Late Delivery Rate by State")

delivery_state_query = """
SELECT
    c.customer_state,

    COUNT(DISTINCT o.order_id) AS delivered_orders,

    SUM(
        CASE
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 1
            ELSE 0
        END
    ) AS late_orders,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                THEN 1
                ELSE 0
            END
        ) / COUNT(DISTINCT o.order_id),
        2
    ) AS late_delivery_percentage

FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id

WHERE o.order_delivered_customer_date IS NOT NULL
"""

if selected_year != "All":
    delivery_state_query += f"""
AND YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

delivery_state_query += """
GROUP BY
    c.customer_state

ORDER BY
    late_delivery_percentage DESC;
"""

delivery_state = run_query(delivery_state_query)
# ============================================================
# LATE DELIVERY RATE BY STATE CHART
# ============================================================

st.bar_chart(
    delivery_state.set_index("customer_state")["late_delivery_percentage"],
    height=450
)
# ============================================================
# DELIVERY DELAY VS REVIEW SCORE
# ============================================================

st.subheader("⭐ Delivery Performance vs Review Score")

delivery_review_query = """
SELECT
    CASE
        WHEN o.order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END AS delivery_performance,

    COUNT(*) AS review_count,

    ROUND(AVG(r.review_score), 2) AS average_review_score

FROM orders o
JOIN order_reviews r
    ON o.order_id = r.order_id
"""

if selected_year != "All":
    delivery_review_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

delivery_review_query += """
GROUP BY
    CASE
        WHEN o.order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END

ORDER BY
    average_review_score DESC;
"""

delivery_review = run_query(delivery_review_query)

# ============================================================
# DELIVERY PERFORMANCE VS REVIEW SCORE CHART
# ============================================================

st.bar_chart(
    delivery_review.set_index("delivery_performance")["average_review_score"],
    height=400
)
# ============================================================
# CUSTOMER EXPERIENCE
# ============================================================


st.header("⭐ Customer Experience")

st.subheader("⭐ Review Score Distribution")

review_distribution_query = """
SELECT
    r.review_score,
    COUNT(*) AS review_count
FROM order_reviews r
JOIN orders o
    ON r.order_id = o.order_id
"""

if selected_year != "All":
    review_distribution_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

review_distribution_query += """
GROUP BY
    r.review_score
ORDER BY
    r.review_score;
"""

review_distribution = run_query(review_distribution_query)

# ============================================================
# REVIEW SCORE DISTRIBUTION CHART
# ============================================================

st.bar_chart(
    review_distribution.set_index("review_score")["review_count"],
    height=400
)
# ============================================================
# REVIEWS BY PRODUCT CATEGORY
# ============================================================

st.subheader("📦⭐ Average Review Score by Product Category")

category_review_query = """
SELECT
    p.product_category_name AS product_category,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
JOIN order_reviews r
    ON o.order_id = r.order_id
"""

if selected_year != "All":
    category_review_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

category_review_query += """
GROUP BY
    p.product_category_name
HAVING
    COUNT(DISTINCT r.order_id) >= 20
ORDER BY
    average_review_score DESC
LIMIT 10;
"""

category_reviews = run_query(category_review_query)

# ============================================================
# AVERAGE REVIEW SCORE BY PRODUCT CATEGORY CHART
# ============================================================

st.bar_chart(
    category_reviews.set_index("product_category")["average_review_score"],
    height=450
)
# ============================================================
# RATING VS DELIVERY PERFORMANCE
# ============================================================

st.subheader("⭐ Review Score by Delivery Performance")

delivery_review_query = """
SELECT
    CASE
        WHEN o.order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END AS delivery_performance,

    ROUND(AVG(r.review_score), 2) AS average_review_score

FROM orders o
JOIN order_reviews r
    ON o.order_id = r.order_id
"""

if selected_year != "All":
    delivery_review_query += f"""
WHERE YEAR(o.order_purchase_timestamp) = {int(selected_year)}
"""

delivery_review_query += """
GROUP BY
    CASE
        WHEN o.order_delivered_customer_date IS NULL
            THEN 'Not Delivered'
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late'
        ELSE 'On Time'
    END

ORDER BY
    average_review_score DESC;
"""

delivery_review = run_query(delivery_review_query)

# ============================================================
# REVIEW SCORE BY DELIVERY PERFORMANCE CHART
# ============================================================

st.bar_chart(
    delivery_review.set_index("delivery_performance")["average_review_score"],
    height=400
)