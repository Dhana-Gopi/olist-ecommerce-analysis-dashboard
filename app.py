import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import plotly.express as px
from pathlib import Path

# ============================================================
# OLIST E-COMMERCE EXECUTIVE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Olist E-Commerce Executive Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DATABASE CONNECTION
# ============================================================

USERNAME = "root"
PASSWORD = "Ammu@181296"
HOST = "localhost"
PORT = 3306
DATABASE = "olist_ecommerce"
CATEGORY_TRANSLATION_FILE = "/Users/dhanalakshmi/o_list_ecommerce_data_analysis/product_category_name_translation.csv"

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}",
    pool_pre_ping=True,
)

# ============================================================
# DESIGN
# ============================================================

YELLOW = "#F2C300"
DARK = "#222222"
GREY = "#666666"
PALE_YELLOW = "#FFFBE6"
WHITE = "#FFFFFF"

# Approximate geographic centroids used for the Brazil state heat map.
STATE_COORDS = {
    "AC": (-9.02, -70.81), "AL": (-9.57, -36.78), "AP": (1.41, -51.77),
    "AM": (-3.47, -65.10), "BA": (-12.58, -41.70), "CE": (-5.20, -39.53),
    "DF": (-15.79, -47.88), "ES": (-19.18, -40.31), "GO": (-15.83, -49.84),
    "MA": (-5.42, -45.44), "MG": (-18.51, -44.56), "MS": (-20.77, -54.79),
    "MT": (-12.64, -55.42), "PA": (-3.79, -52.48), "PB": (-7.24, -36.78),
    "PE": (-8.38, -37.86), "PI": (-7.72, -42.73), "PR": (-24.89, -51.55),
    "RJ": (-22.25, -42.66), "RN": (-5.81, -36.59), "RO": (-10.83, -63.34),
    "RR": (2.74, -61.42), "RS": (-30.17, -53.50), "SC": (-27.33, -50.44),
    "SE": (-10.57, -37.45), "SP": (-22.19, -48.79), "TO": (-10.17, -48.33),
}

st.markdown(
    f"""
    <style>
    .stApp {{ background: {WHITE}; }}
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 0.45rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        overflow: visible !important;
    }}

    .section {{
        font-size: 17px;
        font-weight: 900;
        font-style: italic;
        text-decoration: underline;
        margin: 5px 0 4px 0;
        color: {DARK};
    }}

    h2 {{
        color: {DARK} !important;
        font-size: 19px !important;
        font-weight: 900 !important;
        margin-top: 8px !important;
        margin-bottom: 6px !important;
        line-height: 1.2 !important;
    }}

    .chart-title {{
        font-size: 12px;
        font-weight: 800;
        margin: 0 0 2px 0;
        color: {DARK};
    }}

    .insight {{
        background: {PALE_YELLOW};
        border-left: 3px solid {YELLOW};
        border-radius: 5px;
        padding: 5px 7px;
        margin: 2px 0 6px 0;
        font-size: 10px;
        line-height: 1.35;
        color: {DARK};
    }}

    .takeaway-box {{
    background: #FFF8D9;
    border-left: 4px solid #F4C430;
    border-radius: 6px;
    padding: 10px 12px;
    margin-bottom: 8px;
    font-size: 10px;
    line-height: 1.45;
    color: #222222;
}}

.takeaway-box b {{
    color: #222222;
}}
    [data-testid="stMetric"] {{
        background: {PALE_YELLOW};
        border: 1px solid #E6E6E6;
        border-radius: 8px;
        padding: 7px 9px;
    }}

    [data-testid="stMetricLabel"] {{
        font-size: 10px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stMetricValue"] {{
        font-size: 21px !important;
        font-weight: 900 !important;
    }}

    div[data-baseweb="select"] > div {{
        min-height: 38px;
        border-radius: 7px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

@st.cache_data(ttl=300)
def run_query(query):
    try:
        return pd.read_sql(query, engine)
    except Exception as exc:
        st.error(f"Database query failed: {exc}")
        return pd.DataFrame()


def sql_list(values):
    return ",".join("'" + str(v).replace("'", "''") + "'" for v in values)


def currency(value):
    if value is None or pd.isna(value):
        return "₹0"

    value = float(value)

    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"

    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f} L"

    if abs(value) >= 1_000:
        return f"₹{value / 1_000:.1f}K"

    return f"₹{value:,.0f}"


def number(value):
    if value is None or pd.isna(value):
        return "0"

    return f"{int(round(float(value))):,}"


def rating(value):
    if value is None or pd.isna(value):
        return "0.00"

    return f"{float(value):.2f}"


def chart_style(fig, height=220):
    fig.update_layout(
        height=height,
        margin=dict(l=35, r=10, t=10, b=35),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=DARK, size=9),
        showlegend=False,
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
    )

    return fig


def show_insight(text):
    st.markdown(
        f'<div class="insight">{text}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# PRODUCT CATEGORY ENGLISH TRANSLATION
# ============================================================

CATEGORY_TRANSLATION_FILE = (
    Path(__file__).resolve().parent.parent
    / "product_category_name_translation.csv"
)

category_translation = pd.read_csv(
    CATEGORY_TRANSLATION_FILE
)

category_translation = category_translation[
    ["product_category_name", "product_category_name_english"]
].drop_duplicates()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        width:100%;
        padding-top:45px;
        padding-bottom:4px;
        margin:0;
        color:#222222;
        font-size:30px;
        font-weight:900;
        font-style:italic;
        text-decoration:underline;
        line-height:1.3;
    ">
        🛒 OLIST E-COMMERCE EXECUTIVE DASHBOARD
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
        text-align:center;
        width:100%;
        color:#666666;
        font-size:13px;
        font-weight:500;
        margin:4px 0 10px 0;
        line-height:1.4;
    ">
        Brazilian E-Commerce Performance | Sales • Customers • Products • Sellers • Delivery • Reviews
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
        background:#FFFBE6;
        border-left:4px solid #F2C300;
        border-radius:6px;
        padding:9px 12px;
        margin:4px 0 12px 0;
        color:#222222;
        font-size:12px;
        line-height:1.5;
    ">
        <strong>🎯 Objective:</strong>
        Evaluate sales growth, customer behaviour, product and seller performance,
        delivery efficiency and customer satisfaction to identify business
        strengths and improvement opportunities.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FILTER OPTIONS
# ============================================================

year_df = run_query("""
    SELECT DISTINCT YEAR(order_purchase_timestamp) AS year
    FROM orders
    WHERE order_purchase_timestamp IS NOT NULL
    ORDER BY year;
""")

years = (
    year_df["year"].dropna().astype(int).astype(str).tolist()
    if not year_df.empty
    else []
)

# ============================================================
# MAIN DASHBOARD LAYOUT
# ============================================================

# Reserve the Business Overview position
business_overview_placeholder = st.empty()

# Right panel + main chart area
dashboard_col, right_col = st.columns(
    [3.1, 0.9],
    gap="medium"
)

# YEAR FILTER - TOP OF Right PANEL
with right_col:
    selected_year = st.selectbox(
        "Year",
        ["All"] + years,
        key="year_filter"
    )


# ============================================================
# FILTER SQL
# ============================================================

item_conditions = []

if selected_year != "All":
    item_conditions.append(
        f"YEAR(o.order_purchase_timestamp) = {int(selected_year)}"
    )


def make_filter(extra=None):
    conditions = list(item_conditions)

    if extra:
        conditions.extend(extra)

    if not conditions:
        return ""

    return " AND " + " AND ".join(conditions)


FILTER = make_filter()


# Order-level filters
order_conditions = []

if selected_year != "All":
    order_conditions.append(
        f"YEAR(o.order_purchase_timestamp) = {int(selected_year)}"
    )


ORDER_FILTER = (
    " AND " + " AND ".join(order_conditions)
    if order_conditions
    else ""
)
# ============================================================
# KPI QUERIES
# ============================================================

revenue_df = run_query(f"""
    SELECT SUM(oi.price) AS revenue
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE 1=1
    {FILTER};
""")

revenue = (
    revenue_df["revenue"].iloc[0]
    if not revenue_df.empty
    else 0
)

orders_df = run_query(f"""
    SELECT COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE 1=1
    {FILTER};
""")

total_orders = (
    orders_df["orders"].iloc[0]
    if not orders_df.empty
    else 0
)

customers_df = run_query(f"""
    SELECT COUNT(DISTINCT c.customer_unique_id) AS customers
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE 1=1
    {FILTER};
""")

total_customers = (
    customers_df["customers"].iloc[0]
    if not customers_df.empty
    else 0
)

sellers_df = run_query(f"""
    SELECT COUNT(DISTINCT oi.seller_id) AS sellers
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE 1=1
    {FILTER};
""")

total_sellers = (
    sellers_df["sellers"].iloc[0]
    if not sellers_df.empty
    else 0
)

aov_df = run_query(f"""
    SELECT AVG(order_value) AS aov
    FROM (
        SELECT
            o.order_id,
            SUM(oi.price) AS order_value
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE 1=1
        {FILTER}
        GROUP BY o.order_id
    ) x;
""")

aov = (
    aov_df["aov"].iloc[0]
    if not aov_df.empty
    else 0
)

review_df = run_query(f"""
    SELECT AVG(r.review_score) AS avg_review
    FROM order_reviews r
    JOIN orders o
        ON r.order_id = o.order_id
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE 1=1
    {ORDER_FILTER};
""")

average_review = (
    review_df["avg_review"].iloc[0]
    if not review_df.empty
    else 0
)

delivery_df = run_query(f"""
    SELECT AVG(
        DATEDIFF(
            o.order_delivered_customer_date,
            o.order_purchase_timestamp
        )
    ) AS avg_delivery
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_delivered_customer_date IS NOT NULL
    {ORDER_FILTER};
""")

avg_delivery = (
    delivery_df["avg_delivery"].iloc[0]
    if not delivery_df.empty
    else 0
)

# ============================================================
# BUSINESS OVERVIEW
# ============================================================


with business_overview_placeholder.container():

    st.markdown("## 📊 Business Overview")

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.metric(
            "💰 Revenue",
            currency(revenue)
        )

    with k2:
        st.metric(
            "🛒 Orders",
            number(total_orders)
        )

    with k3:
        st.metric(
            "👥 Customers",
            number(total_customers)
        )

    with k4:
        st.metric(
            "🏪 Sellers",
            number(total_sellers)
        )

    with k5:
        st.metric(
            "🚚 Avg Delivery",
            f"{float(avg_delivery or 0):.1f} days"
        )

    with k6:
        st.metric(
            "⭐ Avg Review",
            f"{rating(average_review)}/5"
        )


# ============================================================
# KEY TAKEAWAYS
# ============================================================

with right_col:

    st.markdown("### 💡 Key Takeaways")

    st.markdown("""
<div class="takeaway-box">
    <h2> About </h2>
    <p>
        This is an executive-level analysis of the Olist e-commerce business.
        It helps understand sales, customers, products, sellers, delivery
        performance and customer satisfaction using historical order data.
    </p>
    <p>
        <b>Data Duration:</b> 2016 – 2018
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="takeaway-box">
    <h2>
        The dashboard provides insights into:
    </h2>
    <ul>
        <li>Sales & Revenue Performance</li>
        <li>Product & Category Performance</li>
        <li>Customer & Geographic Analysis</li>
        <li>Seller Performance</li>
        <li>Repeat vs One-Time Customers</li>
        <li>Delivery & Logistics Performance</li>
        <li>Customer Reviews & Ratings</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    # --------------------------------------------------------
    # TOP CATEGORY
    # --------------------------------------------------------

    top_category_df = run_query(f"""
        SELECT
            p.product_category_name AS category,
            SUM(oi.price) AS revenue
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE 1=1
        {FILTER}
          AND p.product_category_name IS NOT NULL
        GROUP BY p.product_category_name
        ORDER BY revenue DESC
        LIMIT 1;
    """)
    if not top_category_df.empty:

        top_category = top_category_df.iloc[0]["category"]
        top_category_revenue = top_category_df.iloc[0]["revenue"]

        # Translate category to English
        translation_match = category_translation[
            category_translation["product_category_name"] == top_category
        ]

        if not translation_match.empty:
            top_category = translation_match.iloc[0][
                "product_category_name_english"
            ]

    else:
        top_category = "N/A"
        top_category_revenue = 0

    # --------------------------------------------------------
    # LOWEST CATEGORY
    # --------------------------------------------------------

    lowest_category_df = run_query(f"""
        SELECT
            p.product_category_name AS category,
            SUM(oi.price) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE 1=1
        {FILTER}
          AND p.product_category_name IS NOT NULL
        GROUP BY p.product_category_name
        ORDER BY revenue ASC
        LIMIT 1;
    """)

    if not lowest_category_df.empty:

        lowest_category = lowest_category_df.iloc[0]["category"]
        lowest_category_revenue = lowest_category_df.iloc[0]["revenue"]

        translation_match = category_translation[
            category_translation["product_category_name"] == lowest_category
        ]

        if not translation_match.empty:
            lowest_category = translation_match.iloc[0][
                "product_category_name_english"
            ]

    else:
        lowest_category = "N/A"
        lowest_category_revenue = 0

    # --------------------------------------------------------
    # TOP STATE
    # --------------------------------------------------------

    top_state_df = run_query(f"""
        SELECT
            c.customer_state AS state,
            SUM(oi.price) AS revenue
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE 1=1
        {FILTER}
        GROUP BY c.customer_state
        ORDER BY revenue DESC
        LIMIT 1;
    """)

    if not top_state_df.empty:
        top_state = top_state_df.iloc[0]["state"]
        top_state_revenue = top_state_df.iloc[0]["revenue"]
    else:
        top_state = "N/A"
        top_state_revenue = 0

    # --------------------------------------------------------
    # LOWEST STATE
    # --------------------------------------------------------

    lowest_state_df = run_query(f"""
        SELECT
            c.customer_state AS state,
            SUM(oi.price) AS revenue
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE 1=1
        {FILTER}
        GROUP BY c.customer_state
        ORDER BY revenue ASC
        LIMIT 1;
    """)

    if not lowest_state_df.empty:
        lowest_state = lowest_state_df.iloc[0]["state"]
        lowest_state_revenue = lowest_state_df.iloc[0]["revenue"]
    else:
        lowest_state = "N/A"
        lowest_state_revenue = 0

    # --------------------------------------------------------
    # PEAK MONTH
    # --------------------------------------------------------

    peak_month_df = run_query(f"""
        SELECT
            DATE_FORMAT(
                o.order_purchase_timestamp,
                '%%Y-%%m'
            ) AS month,
            SUM(oi.price) AS revenue
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE 1=1
        {FILTER}
        GROUP BY month
        ORDER BY revenue DESC
        LIMIT 1;
    """)

    if not peak_month_df.empty:
        peak_month = peak_month_df.iloc[0]["month"]
        peak_month_revenue = peak_month_df.iloc[0]["revenue"]
    else:
        peak_month = "N/A"
        peak_month_revenue = 0

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    late_df = run_query(f"""
        SELECT
            SUM(
                CASE
                    WHEN o.order_delivered_customer_date IS NOT NULL
                     AND o.order_delivered_customer_date >
                         o.order_estimated_delivery_date
                    THEN 1
                    ELSE 0
                END
            ) AS late_orders,
            SUM(
                CASE
                    WHEN o.order_delivered_customer_date IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            ) AS delivered_orders
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE 1=1
        {ORDER_FILTER};
    """)

    late_orders = (
        late_df.iloc[0]["late_orders"]
        if not late_df.empty
        else 0
    )

    delivered_orders = (
        late_df.iloc[0]["delivered_orders"]
        if not late_df.empty
        else 0
    )

    late_rate = (
        float(late_orders) / float(delivered_orders) * 100
        if delivered_orders
        else 0
    )

    on_time_rate = 100 - late_rate

    # --------------------------------------------------------
    # REPEAT CUSTOMERS
    # --------------------------------------------------------

    repeat_df = run_query(f"""
        SELECT
            SUM(
                CASE
                    WHEN order_count > 1 THEN 1
                    ELSE 0
                END
            ) AS repeat_customers,
            COUNT(*) AS customer_count
        FROM (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            WHERE 1=1
            {ORDER_FILTER}
            GROUP BY c.customer_unique_id
        ) x;
    """)

    repeat_customers = (
        repeat_df.iloc[0]["repeat_customers"]
        if not repeat_df.empty
        else 0
    )

    customer_count = (
        repeat_df.iloc[0]["customer_count"]
        if not repeat_df.empty
        else 0
    )

    repeat_pct = (
        float(repeat_customers) / float(customer_count) * 100
        if customer_count
        else 0
    )

    # --------------------------------------------------------
    # FIVE STAR
    # --------------------------------------------------------

    five_star_df = run_query(f"""
        SELECT
            SUM(
                CASE
                    WHEN r.review_score = 5 THEN 1
                    ELSE 0
                END
            ) AS five_star,
            COUNT(*) AS review_count
        FROM order_reviews r
        JOIN orders o
            ON r.order_id = o.order_id
        JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE 1=1
        {ORDER_FILTER};
    """)

    five_star = (
        five_star_df.iloc[0]["five_star"]
        if not five_star_df.empty
        else 0
    )

    review_count = (
        five_star_df.iloc[0]["review_count"]
        if not five_star_df.empty
        else 0
    )

    five_star_pct = (
        float(five_star) / float(review_count) * 100
        if review_count
        else 0
    )

       # ============================================================
    # KEY TAKEAWAYS
    # ============================================================

    takeaways = [

        f"""
        <b>💰 Sales Performance</b><br>
        <b>Total:</b> {currency(revenue)} generated from {number(total_orders)} orders,
        with an average product value per order of {currency(aov)}.<br>
        <b>Insight:</b> Sales are concentrated across specific categories and customer
        markets, indicating clear areas of stronger demand.<br>
        <b>Action:</b> Focus marketing, inventory and promotional efforts on consistently
        high-performing categories and markets.
        """,

        f"""
        <b>📈 Revenue Peak</b><br>
        <b>Highest:</b> {peak_month} generated {currency(peak_month_revenue)} in revenue.<br>
        <b>Insight:</b> Revenue shows clear periods of stronger demand, which can help
        identify seasonal and promotional opportunities.<br>
        <b>Action:</b> Use peak-period patterns to plan campaigns, inventory availability
        and seller capacity in advance.
        """,

        f"""
        <b>📦 Product Demand</b><br>
        <b>Highest:</b> {top_category} — {currency(top_category_revenue)} revenue.<br>
        <b>Lowest:</b> {lowest_category} — {currency(lowest_category_revenue)} revenue.<br>
        <b>Insight:</b> Product-category performance varies significantly, with a small
        group of categories contributing substantially more revenue.<br>
        <b>Action:</b> Prioritize high-performing categories while reviewing pricing,
        product availability and promotional strategies for weaker categories.
        """,

        f"""
        <b>📍 Customer Market</b><br>
        <b>Highest:</b> {top_state} — {currency(top_state_revenue)} revenue.<br>
        <b>Lowest:</b> {lowest_state} — {currency(lowest_state_revenue)} revenue.<br>
        <b>Insight:</b> Customer demand is highly concentrated geographically, with
        São Paulo (SP) representing the strongest market in the dataset.<br>
        <b>Action:</b> Strengthen marketing and seller coverage in high-value states
        while evaluating growth opportunities in lower-performing regions.
        """,

        f"""
        <b>🚚 Delivery Performance</b><br>
        <b>On Time:</b> {on_time_rate:.1f}%<br>
        <b>Late:</b> {late_rate:.1f}%<br>
        <b>Insight:</b> Most orders are delivered on time, but late deliveries remain
        a measurable customer-experience risk.<br>
        <b>Action:</b> Investigate high-delay states and seller/logistics performance
        to identify the major causes of delivery delays.
        """,

        f"""
        <b>🔁 Customer Retention</b><br>
        <b>Repeat Customers:</b> {repeat_pct:.1f}%<br>
        <b>One-Time Customers:</b> {100 - repeat_pct:.1f}%<br>
        <b>Insight:</b> The customer base is dominated by one-time purchasers,
        indicating a significant opportunity to increase repeat purchases.<br>
        <b>Action:</b> Introduce personalized offers, loyalty incentives,
        post-purchase engagement and targeted campaigns to encourage customers to return.
        """,

        f"""
        <b>⭐ Customer Satisfaction</b><br>
        <b>Average Rating:</b> {rating(average_review)}/5<br>
        <b>5-Star Reviews:</b> {five_star_pct:.1f}%<br>
        <b>Insight:</b> Overall customer satisfaction is positive, with more than
        half of reviews receiving five stars.<br>
        <b>Action:</b> Maintain service quality while analyzing lower-rated reviews
        to identify recurring product, seller or delivery issues.
        """
    ]

    # Render each takeaway as ONE complete HTML element.
    # Do not add markdown/code fences around the HTML.
    for item in takeaways:
        card_html = f"""
<div class="takeaway-box">
{item.strip()}
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    st.markdown("### 🎯 Conclusion")

    st.markdown("""
    <div class="takeaway-box">

    <b>• Revenue:</b> The business generated ₹1.36 Cr across 98,666 orders, 
    with revenue concentrated among specific product categories and geographic markets.<br><br>
    
    <b>• Growth Opportunities:</b> High-performing categories and states can be 
    prioritized for continued growth, while underperforming segments should 
    be evaluated for pricing, product and marketing improvements.<br><br>

    <b>• Customer Retention:</b> With 3.1% repeat customers and 96.9% one-time customers, 
    customer retention represents the largest opportunity for 
    improving long-term customer value.<br><br>

    <b>• Delivery:</b> With 91.9% of orders delivered on time, delivery performance 
    is generally strong. However, reducing delays in high-risk states can further 
    improve customer experience.<br><br>

    <b>• Customer Satisfaction:</b> An average rating of 4.09/5 and 57.8% five-star reviews 
    indicate positive overall customer sentiment, while lower-rated reviews can help 
    identify areas for operational improvement.<br><br>
    
    <b>Business Priority:</b> The key opportunity is to retain existing customers while 
    protecting high-performing categories and markets, supported 
    by improved delivery performance and data-driven customer engagement.<br><br>

    <b>• Overall:</b> The analysis shows a business with strong sales activity, 
    broad geographic reach and positive customer satisfaction, but with significant 
    potential to improve repeat purchases, regional performance and delivery efficiency.

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CHART DASHBOARD
# 3 CHARTS PER ROW
# ============================================================

with dashboard_col:

    # ========================================================
    # ROW 1 — SALES
    # ========================================================

    st.markdown("## 📈 Sales Performance")

    r1c1, r1c2, r1c3 = st.columns(3)

    # --------------------------------------------------------
    # 1. MONTHLY REVENUE
    # --------------------------------------------------------

    with r1c1:

        st.markdown(
            '<div class="chart-title">Monthly Revenue Trend</div>',
            unsafe_allow_html=True,
        )

        monthly = run_query(f"""
            SELECT
                DATE_FORMAT(
                    o.order_purchase_timestamp,
                    '%%Y-%%m'
                ) AS month,
                SUM(oi.price) AS revenue
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY month
            ORDER BY month;
        """)

        if not monthly.empty:

            monthly["month"] = pd.to_datetime(monthly["month"])
            monthly["label"] = monthly["month"].dt.strftime("%b %Y")

            fig = px.line(
                monthly,
                x="label",
                y="revenue",
                markers=True,
            )
            fig.update_xaxes(title_text="")

            fig.update_traces(
                line=dict(color=YELLOW, width=3),
                marker=dict(color=YELLOW, size=5),
            )

            peak = monthly.loc[monthly["revenue"].idxmax()]

            fig.add_annotation(
                x=peak["label"],
                y=peak["revenue"],
                text=currency(peak["revenue"]),
                showarrow=True,
                arrowhead=2,
                font=dict(size=8),
            )

            fig = chart_style(fig)
            fig.update_yaxes(tickprefix="₹")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_1",
            )

            show_insight(
                f"Revenue peaked at <b>{currency(peak['revenue'])}</b> in <b>{peak['label']}</b>."
            )

    # --------------------------------------------------------
    # 2. CATEGORY REVENUE
    # --------------------------------------------------------

    with r1c2:

        st.markdown(
            '<div class="chart-title">Top 10 Categories by Revenue</div>',
            unsafe_allow_html=True,
        )

        category_data = run_query(f"""
            SELECT
                p.product_category_name AS category,
                SUM(oi.price) AS revenue
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
              AND p.product_category_name IS NOT NULL
            GROUP BY p.product_category_name
            ORDER BY revenue DESC
            LIMIT 10;
        """)

                # Translate Portuguese category names to English
        category_data = category_data.merge(
            category_translation,
            left_on="category",
            right_on="product_category_name",
            how="left"
        )

        category_data["category"] = (
            category_data["product_category_name_english"]
            .fillna(category_data["category"])
        )

        if not category_data.empty:

            category_data["share"] = (
                category_data["revenue"]
                / category_data["revenue"].sum()
                * 100
            )

            display_data = category_data.sort_values("revenue")

            fig = px.bar(
                display_data,
                x="revenue",
                y="category",
                orientation="h",
                text=display_data["revenue"].apply(currency),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)
            fig.update_xaxes(tickprefix="₹")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_2",
            )

            show_insight(
                f"<b>{category_data.iloc[0]['category']}</b> leads the displayed categories with {category_data.iloc[0]['share']:.1f}% of their combined revenue."
            )

    # --------------------------------------------------------
    # 3. TOP PRODUCTS
    # --------------------------------------------------------

    with r1c3:

        st.markdown(
            '<div class="chart-title">Top 10 Products by Units Sold</div>',
            unsafe_allow_html=True,
        )

        products_data = run_query(f"""
            SELECT
                oi.product_id,
                COUNT(*) AS units
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY oi.product_id
            ORDER BY units DESC
            LIMIT 10;
        """)

        if not products_data.empty:

            products_data["label"] = (
                products_data["product_id"]
                .astype(str)
                .str[:8]
                + "…"
            )

            display_data = products_data.sort_values("units")

            fig = px.bar(
                display_data,
                x="units",
                y="label",
                orientation="h",
                text="units",
            )
            fig.update_yaxes(title_text="Product_id")

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
            )

            fig = chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_3",
            )

            show_insight(
                f"Best-selling product sold <b>{number(products_data.iloc[0]['units'])} units</b>."
            )

        # ========================================================
    # ROW 2 — CUSTOMER
    # ========================================================

    st.markdown("## 👥 Customer Analysis")

    r2c1, r2c2, r2c3 = st.columns(3)

    # --------------------------------------------------------
    # 4. SALES BY STATE
    # --------------------------------------------------------

    with r2c1:

        st.markdown(
            '<div class="chart-title">Top 10 Customer States by Revenue</div>',
            unsafe_allow_html=True,
        )

        state_sales = run_query(f"""
            SELECT
                c.customer_state AS state,
                SUM(oi.price) AS revenue
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY c.customer_state
            ORDER BY revenue DESC
            LIMIT 10;
        """)

        if not state_sales.empty:

            display_data = state_sales.sort_values("revenue")

            fig = px.bar(
                display_data,
                x="revenue",
                y="state",
                orientation="h",
                text=display_data["revenue"].apply(currency),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)
            fig.update_xaxes(tickprefix="₹")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="chart_4",
            )

            show_insight(
                f"<b>{state_sales.iloc[0]['state']}</b> is the highest-revenue customer location."
            )

    # --------------------------------------------------------
    # 5. CUSTOMER REVENUE MAP BY BRAZILIAN STATE
    # --------------------------------------------------------

    with r2c2:

        st.markdown(
            '<div class="chart-title">Customer Revenue Heat Map by State</div>',
            unsafe_allow_html=True,
        )

        location_heatmap = run_query(f"""
            SELECT
                c.customer_state AS state,
                SUM(oi.price) AS revenue,
                COUNT(DISTINCT c.customer_unique_id) AS customers
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY c.customer_state
            ORDER BY revenue DESC;
        """)

        if not location_heatmap.empty:

            BRAZIL_STATES_GEOJSON = (
                "https://raw.githubusercontent.com/"
                "codeforamerica/click_that_hood/master/public/data/"
                "brazil-states.geojson"
            )

            fig = px.choropleth(
                location_heatmap,
                geojson=BRAZIL_STATES_GEOJSON,
                locations="state",
                featureidkey="properties.sigla",
                color="revenue",
                color_continuous_scale=[
                    "#FFFBE6",
                    "#F9DC4A",
                    "#F2C300",
                    "#C99F00",
                    "#8F7000",
                ],
                hover_name="state",
                hover_data={
                    "revenue": ":,.0f",
                    "customers": ":,",
                },
            )

            fig.update_geos(
                fitbounds="locations",
                visible=False,
                showcountries=True,
                countrycolor="#888888",
                showcoastlines=True,
                coastlinecolor="#888888",
                showland=True,
                landcolor="#FFFFFF",
            )

            fig.update_layout(
                height=220,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor=WHITE,
                plot_bgcolor=WHITE,
                coloraxis_colorbar=dict(
                    title="Revenue",
                    thickness=10,
                    len=0.65,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="chart_location_heatmap",
            )

            top_location = location_heatmap.iloc[0]

            show_insight(
                f"<b>{top_location['state']}</b> is the strongest customer market "
                f"in the filtered view, generating "
                f"<b>{currency(top_location['revenue'])}</b> from "
                f"<b>{number(top_location['customers'])}</b> customers."
            )

    # --------------------------------------------------------
    # 6. TOP CUSTOMERS
    # --------------------------------------------------------

    with r2c3:

        st.markdown(
            '<div class="chart-title">Top 10 Customers by Spending</div>',
            unsafe_allow_html=True,
        )

        top_customers = run_query(f"""
            SELECT
                c.customer_unique_id,
                SUM(oi.price) AS spending
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY c.customer_unique_id
            ORDER BY spending DESC
            LIMIT 10;
        """)

        if not top_customers.empty:

            top_customers["label"] = (
                top_customers["customer_unique_id"]
                .astype(str)
                .str[:8]
                + "…"
            )

            display_data = top_customers.sort_values("spending")

            fig = px.bar(
                display_data,
                x="spending",
                y="label",
                orientation="h",
                text=display_data["spending"].apply(currency),
            )

            # Hide Y-axis title
            fig.update_yaxes(title_text="")

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)
            fig.update_xaxes(tickprefix="₹")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="chart_6",
            )

            show_insight(
                f"Highest customer spend in the filtered view is "
                f"<b>{currency(top_customers.iloc[0]['spending'])}</b>."
            )
    # ========================================================
    # ROW 3 — SELLER & RETENTION
    # ========================================================

    st.markdown("## 🏪 Seller & Customer Retention")

    r3c1, r3c2, r3c3 = st.columns(3)

    # --------------------------------------------------------
    # 7. REPEAT VS ONE-TIME
    # --------------------------------------------------------

    with r3c1:

        st.markdown(
            '<div class="chart-title">Repeat vs One-Time Customers</div>',
            unsafe_allow_html=True,
        )

        repeat_data = run_query(f"""
            SELECT
                CASE
                    WHEN order_count = 1 THEN 'One-Time'
                    ELSE 'Repeat'
                END AS customer_type,
                COUNT(*) AS customers
            FROM (
                SELECT
                    c.customer_unique_id,
                    COUNT(DISTINCT o.order_id) AS order_count
                FROM customers c
                JOIN orders o
                    ON c.customer_id = o.customer_id
                WHERE 1=1
                {ORDER_FILTER}
                GROUP BY c.customer_unique_id
            ) x
            GROUP BY customer_type;
        """)

        if not repeat_data.empty:

            fig = px.pie(
                repeat_data,
                names="customer_type",
                values="customers",
                hole=0.45,
            )

            fig.update_traces(
                marker=dict(
                    colors=[YELLOW, "#FFF4A8"],
                    line=dict(color=WHITE, width=2),
                ),
                textinfo="percent+label",
            )

            fig.update_layout(
                height=220,
                margin=dict(l=5, r=5, t=5, b=5),
                paper_bgcolor=WHITE,
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_7",
            )

            show_insight(
                f"Repeat customers account for <b>{repeat_pct:.1f}%</b> of the filtered customer base."
            )

    # --------------------------------------------------------
    # 8. TOP SELLERS
    # --------------------------------------------------------

    with r3c2:

        st.markdown(
            '<div class="chart-title">Top 10 Sellers by Revenue</div>',
            unsafe_allow_html=True,
        )

        seller_revenue = run_query(f"""
            SELECT
                oi.seller_id,
                SUM(oi.price) AS revenue
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE 1=1
            {FILTER}
            GROUP BY oi.seller_id
            ORDER BY revenue DESC
            LIMIT 10;
        """)

        if not seller_revenue.empty:

            seller_revenue["label"] = (
                seller_revenue["seller_id"]
                .astype(str)
                .str[:8]
                + "…"
            )

            display_data = seller_revenue.sort_values("revenue")

            fig = px.bar(
                display_data,
                x="revenue",
                y="label",
                orientation="h",
                text=display_data["revenue"].apply(currency),
            )
            fig.update_yaxes(title_text="seller_id")

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)
            fig.update_xaxes(tickprefix="₹")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_8",
            )

            show_insight(
                f"Leading seller generated <b>{currency(seller_revenue.iloc[0]['revenue'])}</b> in the filtered view."
            )

    # --------------------------------------------------------
    # 9. RATING BY CATEGORY
    # --------------------------------------------------------

    with r3c3:

        st.markdown(
            '<div class="chart-title">Average Rating by Product Category</div>',
            unsafe_allow_html=True,
        )

        category_reviews = run_query(f"""
            SELECT
                x.category,
                AVG(x.review_score) AS rating
            FROM (
                SELECT DISTINCT
                    o.order_id,
                    p.product_category_name AS category,
                    r.review_score
                FROM order_reviews r
                JOIN orders o
                    ON r.order_id = o.order_id
                JOIN customers c
                    ON o.customer_id = c.customer_id
                JOIN order_items oi
                    ON o.order_id = oi.order_id
                JOIN products p
                    ON oi.product_id = p.product_id
                WHERE 1=1
                {FILTER}
                  AND p.product_category_name IS NOT NULL
            ) x
            GROUP BY x.category
            HAVING COUNT(DISTINCT x.order_id) >= 20
            ORDER BY rating DESC
            LIMIT 10;
        """)

                # Translate Portuguese category names to English
        if not category_reviews.empty:

            category_reviews = category_reviews.merge(
                category_translation,
                left_on="category",
                right_on="product_category_name",
                how="left"
            )

            category_reviews["category"] = (
                category_reviews["product_category_name_english"]
                .fillna(category_reviews["category"])
            )

            category_reviews["rating"] = (
                category_reviews["rating"].round(2)
            )

            display_data = category_reviews.sort_values("rating")

            fig = px.bar(
                display_data,
                x="rating",
                y="category",
                orientation="h",
                text=display_data["rating"].apply(
                    lambda x: f"{x:.2f}"
                ),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)

            fig.update_xaxes(
                range=[0, 5],
                dtick=1,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="chart_9",
            )

            show_insight(
                f"Highest-rated categories provide an indication of strong customer satisfaction."
            )
    # ========================================================
    # ROW 4 — DELIVERY
    # ========================================================

    st.markdown("## 🚚 Delivery Performance")

    r4c1, r4c2, r4c3 = st.columns(3)

    # --------------------------------------------------------
    # 10. ON-TIME VS LATE DELIVERY — PIE CHART
    # --------------------------------------------------------

    with r4c1:

        st.markdown(
            '<div class="chart-title">On-Time vs Late Delivery</div>',
            unsafe_allow_html=True,
        )

        delivery_pie = pd.DataFrame({
            "performance": ["On Time", "Late"],
            "orders": [
                max(float(delivered_orders) - float(late_orders), 0),
                float(late_orders),
            ],
        })

        delivery_pie = delivery_pie[delivery_pie["orders"] > 0]

        if not delivery_pie.empty:

            fig = px.pie(
                delivery_pie,
                names="performance",
                values="orders",
                hole=0.45,
            )

            fig.update_traces(
                textinfo="percent+label",
                texttemplate="%{label}<br>%{percent:.1%}",
                marker=dict(
                    colors=[YELLOW, "#F3E7A0"],
                    line=dict(color=WHITE, width=2),
                ),
            )

            fig.update_layout(
                height=220,
                margin=dict(l=5, r=5, t=5, b=5),
                paper_bgcolor=WHITE,
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="chart_delivery_pie",
            )

            show_insight(
                f"<b>{on_time_rate:.1f}%</b> of delivered orders arrived on time; "
                f"<b>{late_rate:.1f}%</b> were late."
            )

    # --------------------------------------------------------
    # 11. LATE DELIVERY BY STATE
    # --------------------------------------------------------

    with r4c2:

        st.markdown(
            '<div class="chart-title">Top 10 States by Late-Delivery Rate</div>',
            unsafe_allow_html=True,
        )

        late_state = run_query(f"""
            SELECT
                c.customer_state AS state,
                100 *
                SUM(
                    CASE
                        WHEN o.order_delivered_customer_date IS NOT NULL
                         AND o.order_delivered_customer_date >
                             o.order_estimated_delivery_date
                        THEN 1
                        ELSE 0
                    END
                )
                /
                NULLIF(
                    SUM(
                        CASE
                            WHEN o.order_delivered_customer_date IS NOT NULL
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS late_rate
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            WHERE 1=1
            {ORDER_FILTER}
            GROUP BY c.customer_state
            HAVING SUM(
                CASE
                    WHEN o.order_delivered_customer_date IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            ) > 0
            ORDER BY late_rate DESC
            LIMIT 10;
        """)

        if not late_state.empty:

            display_data = late_state.sort_values("late_rate")

            fig = px.bar(
                display_data,
                x="late_rate",
                y="state",
                orientation="h",
                text=display_data["late_rate"].apply(
                    lambda x: f"{x:.1f}%"
                ),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
            )

            fig = chart_style(fig)
            max_rate = float(display_data["late_rate"].max())

            fig.update_xaxes(
                range=[0, max(25, max_rate * 1.15)],
                ticksuffix="%",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_11",
            )

            show_insight(
                f"<b>{late_state.iloc[0]['state']}</b> has the highest late-delivery rate at <b>{late_state.iloc[0]['late_rate']:.1f}%</b> among the displayed states."
            )

    # --------------------------------------------------------
    # 12. DELIVERY TREND
    # --------------------------------------------------------

    with r4c3:

        st.markdown(
            '<div class="chart-title">Average Delivery Time by Year</div>',
            unsafe_allow_html=True,
        )

        delivery_by_year = run_query(f"""
            SELECT
                YEAR(o.order_purchase_timestamp) AS year,
                AVG(
                    DATEDIFF(
                        o.order_delivered_customer_date,
                        o.order_purchase_timestamp
                    )
                ) AS days
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE o.order_delivered_customer_date IS NOT NULL
            {ORDER_FILTER}
            GROUP BY YEAR(o.order_purchase_timestamp)
            ORDER BY year;
        """)

        if not delivery_by_year.empty:

            fig = px.bar(
                delivery_by_year,
                x="year",
                y="days",
                text=delivery_by_year["days"].round(1),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
            )

            fig = chart_style(fig)
            fig.update_yaxes(title="Days")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_delivery_by_year",
            )

            show_insight(
                f"Average delivery time for the current selection is <b>{float(avg_delivery):.1f} days</b>."
            )

    # ========================================================
    # ROW 5 — CUSTOMER EXPERIENCE
    # ========================================================

    st.markdown("## ⭐ Customer Experience")

    r5c1, r5c2, r5c3 = st.columns(3)

    # --------------------------------------------------------
    # 13. REVIEW DISTRIBUTION
    # --------------------------------------------------------

    with r5c1:

        st.markdown(
            '<div class="chart-title">Review Score Distribution</div>',
            unsafe_allow_html=True,
        )

        review_distribution = run_query(f"""
            SELECT
                r.review_score,
                COUNT(*) AS reviews
            FROM order_reviews r
            JOIN orders o
                ON r.order_id = o.order_id
            JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE 1=1
            {ORDER_FILTER}
            GROUP BY r.review_score
            ORDER BY r.review_score DESC;
        """)

        if not review_distribution.empty:

            desired = [5, 4, 3, 2, 1]

            review_distribution = (
                review_distribution
                .set_index("review_score")
                .reindex(desired)
                .fillna(0)
                .reset_index()
            )

            total_reviews = review_distribution["reviews"].sum()

            review_distribution["share"] = (
                review_distribution["reviews"]
                / total_reviews
                * 100
                if total_reviews
                else 0
            )

            fig = px.bar(
                review_distribution,
                x="review_score",
                y="reviews",
                text=review_distribution.apply(
                    lambda x:
                    f"{int(x['reviews']):,}<br>{x['share']:.1f}%",
                    axis=1,
                ),
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
                textfont=dict(size=7),
            )

            fig = chart_style(fig)
            fig.update_xaxes(dtick=1)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_13",
            )

            show_insight(
                f"<b>{five_star_pct:.1f}%</b> of reviews are 5-star."
            )

    # --------------------------------------------------------
    # 14. CATEGORY REVIEWS
    # --------------------------------------------------------

    with r5c2:

        st.markdown(
            '<div class="chart-title">Average Review by Product Category</div>',
            unsafe_allow_html=True,
        )

        category_reviews_2 = run_query(f"""
            SELECT
                x.category,
                AVG(x.review_score) AS rating
            FROM (
                SELECT DISTINCT
                    o.order_id,
                    p.product_category_name AS category,
                    r.review_score
                FROM order_reviews r
                JOIN orders o
                    ON r.order_id = o.order_id
                JOIN customers c
                    ON o.customer_id = c.customer_id
                JOIN order_items oi
                    ON o.order_id = oi.order_id
                JOIN products p
                    ON oi.product_id = p.product_id
                WHERE 1=1
                {FILTER}
                  AND p.product_category_name IS NOT NULL
            ) x
            GROUP BY x.category
            HAVING COUNT(DISTINCT x.order_id) >= 20
            ORDER BY rating DESC
            LIMIT 10;
        """)

        if not category_reviews_2.empty:
            category_reviews_2 = category_reviews_2.merge(
                category_translation,
                left_on="category",
                right_on="product_category_name",
                how="left"
            )

            category_reviews_2["category"] = (
                category_reviews_2["product_category_name_english"]
                .fillna(category_reviews_2["category"])
            )

            display_data = category_reviews_2.sort_values("rating")

            fig = px.bar(
                display_data,
                x="rating",
                y="category",
                orientation="h",
                text="rating",
            )

            fig.update_traces(
                marker_color=YELLOW,
                textposition="outside",
            )

            fig = chart_style(fig)
            fig.update_xaxes(
                range=[0, 5],
                dtick=1,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            key="chart_14",
            )

            show_insight(
                f"<b>{category_reviews_2.iloc[0]['category']}</b> has the highest displayed rating at <b>{category_reviews_2.iloc[0]['rating']:.2f}/5</b>."
            )

    # --------------------------------------------------------
    # 15. Business Health Snapshot
    # --------------------------------------------------------

    with r5c3:

        st.markdown(
            '<div class="chart-title">Business Health Snapshot</div>',
            unsafe_allow_html=True,
        )

        health = pd.DataFrame(
            {
                "Metric": [
                    "On-Time Delivery",
                    "Repeat Customers",
                    "5-Star Reviews",
                    "Avg Rating",
                ],
                "Value": [
                    on_time_rate,
                    repeat_pct,
                    five_star_pct,
                    float(average_review or 0) * 20,
                ],
            }
        )

        display_health = health.sort_values("Value")

        fig = px.bar(
            display_health,
            x="Value",
            y="Metric",
            orientation="h",
            text=display_health["Value"].apply(
                lambda x: f"{x:.1f}%"
            ),
        )

        fig.update_traces(
            marker_color=YELLOW,
            textposition="outside",
        )

        fig = chart_style(fig)
        fig.update_xaxes(
            range=[0, 100],
            ticksuffix="%",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        key="chart_15",
        )

        show_insight(
            f"Overall view: <b>{on_time_rate:.1f}%</b> on-time delivery, "
            f"<b>{repeat_pct:.1f}%</b> repeat customers and "
            f"<b>{rating(average_review)}/5</b> average rating."
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Olist E-Commerce Executive Analytics | "
    "Interactive analysis of sales, customers, products, sellers, delivery and reviews."
)
