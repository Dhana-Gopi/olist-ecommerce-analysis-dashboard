# 🛒 Olist E-Commerce Performance Analysis

An end-to-end **Data Analytics and Business Intelligence project** using
the Brazilian Olist E-Commerce dataset to analyze sales, customers,
products, sellers, delivery performance, payments, and customer
satisfaction.

The project follows a complete analytics workflow:

**Raw Data → Data Quality → Data Cleaning → MySQL Database → Feature
Engineering → EDA → Statistical Analysis → SQL Analysis → Streamlit
Dashboard → Business Insights**

------------------------------------------------------------------------

## 📌 Project Overview

E-commerce platforms generate large volumes of data through customer
orders, products, sellers, payments, deliveries, and customer reviews.
These datasets are stored across multiple related tables, making it
difficult to understand overall business performance and customer
behavior from raw data alone.

The objective of this project is to analyze the Olist e-commerce data
and uncover meaningful business insights related to:

-   Sales and revenue
-   Customer behavior
-   Product performance
-   Seller performance
-   Payment methods
-   Delivery performance
-   Customer satisfaction
-   Operational efficiency

The final output is an interactive **Streamlit dashboard connected to a
MySQL database**, supported by exploratory analysis and statistical
hypothesis testing.

------------------------------------------------------------------------

## 🎯 Problem Statement

An e-commerce platform generates a large amount of data through customer
orders, products, sellers, payments, deliveries, and customer reviews.
This information is stored across multiple related datasets, making it
difficult to understand overall business performance and customer
behavior from raw data alone.

The objective of this project is to **analyze the e-commerce data and
uncover meaningful business insights** related to sales, customers,
products, sellers, payments, delivery performance, and customer
satisfaction.

------------------------------------------------------------------------

## 💼 Business Use Cases

This project addresses the following business use cases:

-   📊 E-Commerce Performance Monitoring
-   👥 Customer Behavior & Segmentation
-   💰 Sales & Revenue Optimization
-   📦 Product & Seller Performance Analysis
-   🚚 Delivery & Operational Optimization
-   ⭐ Customer Experience Improvement
-   📈 Data-Driven Business Decision Making

------------------------------------------------------------------------

## 🗂️ Dataset

The project uses the **Brazilian Olist E-Commerce dataset**, which
contains multiple related tables representing different parts of the
e-commerce ecosystem.

### Main Tables

  -------------------------------------------------------------------------
  Table                                 Description
  ------------------------------------- -----------------------------------
  `customers`                           Customer information and location

  `orders`                              Order details, timestamps, status,
                                        and delivery dates

  `order_items`                         Products purchased in each order,
                                        price and seller

  `products`                            Product details and categories

  `sellers`                             Seller information and location

  `order_payments`                      Payment method and payment
                                        information

  `order_reviews`                       Customer review scores and comments

  `geolocation`                         Brazilian zip-code/geographical
                                        information

  `product_category_name_translation`   Product category translation
                                        information
  -------------------------------------------------------------------------

------------------------------------------------------------------------

## 🔗 ER Diagram

The relationships between the nine datasets were studied using an Entity
Relationship Diagram.

**ER Diagram:**\
https://shadiyapp.github.io/Decoding-E-Commerce-Performance/

The ER diagram was used to understand:

-   Primary keys
-   Foreign keys
-   One-to-many relationships
-   Table dependencies
-   Appropriate SQL joins

------------------------------------------------------------------------

## 🧰 Technologies & Tools

### Programming & Analysis

-   Python
-   Pandas
-   NumPy
-   SciPy
-   Jupyter Notebook

### Database

-   MySQL
-   SQLAlchemy
-   PyMySQL

### Visualization & Dashboard

-   Streamlit
-   Streamlit charts

### Data & Documentation

-   CSV
-   Excel
-   Data Dictionary
-   Cleaning Log
-   ER Diagram
-   README documentation

------------------------------------------------------------------------

# 🔄 Project Approach

## Step 1 --- Understand the Business Problem

The first step was to understand the business context and identify the
questions that the analysis should answer.

Key objectives included:

-   How is the business performing?
-   Which product categories generate the most revenue?
-   Which customers and sellers contribute the most?
-   How does delivery performance affect customer satisfaction?
-   Are customers mostly one-time or repeat buyers?
-   Does spending differ across product categories?
-   Is payment method associated with order status?

------------------------------------------------------------------------

## Step 2 --- Understand the Dataset & ER Diagram

The nine related tables were studied to understand:

-   Columns and data types
-   Primary keys
-   Foreign keys
-   Relationships between tables
-   Business meaning of each field

A **data dictionary** was also prepared to document the datasets and
their columns.

------------------------------------------------------------------------

## Step 3 --- Load the Raw Data

The raw CSV files were loaded into Python using Pandas.

Initial checks included:

-   Dataset shape
-   Column names
-   Data types
-   Sample records
-   Missing values
-   Duplicate records

------------------------------------------------------------------------

## Step 4 --- Data Quality Analysis

The datasets were examined for common data-quality issues:

-   Missing values
-   Duplicate records
-   Incorrect data types
-   Invalid values
-   Inconsistent categorical values
-   Potential outliers
-   Primary-key uniqueness

A **data quality report** and **cleaning log** were maintained to
document the transformation process.

------------------------------------------------------------------------

## Step 5 --- Data Cleaning & Preprocessing

The following preprocessing activities were performed where required:

-   Handling missing values
-   Removing duplicate records
-   Correcting data types
-   Converting date/time columns
-   Standardizing categorical values
-   Handling invalid records
-   Renaming columns where required

The cleaned datasets were then prepared for database loading and
analysis.

------------------------------------------------------------------------

## Step 6 --- Store Cleaned Data in MySQL

The cleaned datasets were loaded into a MySQL database named:

``` text
olist_ecommerce
```

The database was structured according to the relationships identified in
the ER diagram.

SQL was then used as the primary analytical layer for the dashboard.

------------------------------------------------------------------------

# 🧮 Step 7 --- Feature Engineering

Meaningful business features were created to support analysis.

Examples include:

-   Total order value
-   Delivery days
-   Delivery delay
-   Customer order count
-   Customer total spending
-   Average Order Value
-   Seller revenue
-   Seller order count
-   Repeat customer indicator
-   Delivery performance classification

### Delivery Performance

Orders were classified into:

-   **On Time**
-   **Late**
-   **Not Delivered**

This classification was later used to analyze the relationship between
delivery experience and customer reviews.

### Customer Type

Customers were classified based on order count:

-   **One-Time Customer**
-   **Repeat Customer**

------------------------------------------------------------------------

# 📊 Step 8 --- Exploratory Data Analysis

Exploratory analysis was performed using Python and SQL.

The analysis included:

-   Univariate analysis
-   Bivariate analysis
-   Multivariate analysis
-   Trend analysis
-   Distribution analysis
-   Correlation analysis
-   Aggregation and grouping

The analysis focused on sales, customers, products, sellers, delivery,
payments, and reviews.

------------------------------------------------------------------------

# 📐 Step 9 --- Statistical Analysis

Three hypothesis-testing techniques were performed to answer important
business questions.

------------------------------------------------------------------------

## 1. T-Test --- Delivery Performance & Customer Satisfaction

### Business Question

**Do delayed orders receive significantly different review scores
compared to orders delivered on time?**

### Hypotheses

**H₀:** The mean review score for on-time and late orders is the same.

**H₁:** The mean review score for on-time and late orders is different.

### Method

Welch's Independent Two-Sample T-Test

Welch's test was used with:

``` python
equal_var=False
```

### Result

``` text
T-statistic: 89.55081413351807
P-value: < 0.001
```

The p-value was displayed by SciPy as `0.0` because it is smaller than
the floating-point precision displayed by the calculation.

### Decision

Reject H₀ at the 5% significance level.

### Business Interpretation

There is a statistically significant difference in review scores between
on-time and late deliveries.

This indicates that **delivery performance is strongly associated with
customer satisfaction**.

> Note: Statistical significance establishes a difference between the
> groups; the group means should be used to state which delivery group
> has the higher review score.

------------------------------------------------------------------------

## 2. ANOVA --- Product Category & Order Value

### Business Question

**Does average order value differ significantly across product
categories?**

### Hypotheses

**H₀:** All product categories have the same mean order value.

**H₁:** At least one product category has a different mean order value.

### Method

One-Way ANOVA

### Result

``` text
F-statistic: 153.92853382116843
P-value: < 0.001
```

The p-value was displayed as `0.0` because it is extremely small.

### Decision

Reject H₀ at the 5% significance level.

### Business Interpretation

There is a statistically significant difference in average order value
across product categories.

This suggests that **customer spending behavior varies substantially
across product categories**.

> ANOVA establishes that at least one category differs. A post-hoc test
> such as Tukey's HSD would be required to determine exactly which
> category pairs differ.

------------------------------------------------------------------------

## 3. Chi-Square --- Payment Method & Order Status

### Business Question

**Is there a significant association between payment method and order
status?**

### Hypotheses

**H₀:** Payment method and order status are independent.

**H₁:** Payment method and order status are associated.

### Method

Chi-Square Test of Independence

### Result

``` text
Chi-Square Statistic: 677.0831369637666
P-value: 1.2047397488650834e-124
Degrees of Freedom: 28
```

### Decision

Reject H₀ at the 5% significance level.

### Business Interpretation

There is a statistically significant association between **payment
method and order status**.

This suggests that order outcomes are not distributed independently of
the payment method used.

> Association does not imply that the payment method causes a particular
> order outcome.

------------------------------------------------------------------------

# 🗄️ Step 10 --- SQL Analysis & Streamlit Dashboard

The cleaned data was stored in MySQL and queried from Python using
SQLAlchemy.

The dashboard uses SQL concepts including:

-   `SELECT`
-   `WHERE`
-   `ORDER BY`
-   `GROUP BY`
-   `HAVING`
-   Aggregations
-   Joins
-   Subqueries
-   CTEs

The final Streamlit dashboard provides an interactive year filter and
multiple analytical sections.

------------------------------------------------------------------------

# 📊 Dashboard

## 1. 📊 Business Overview

The dashboard provides high-level KPIs:

-   💰 Total Revenue
-   🛒 Total Orders
-   👥 Total Customers
-   🏪 Total Sellers
-   💳 Average Order Value
-   ⭐ Average Review Score

Example overall dashboard values from the analysis:

  KPI                         Value
  ---------------------- ----------
  Total Revenue            ₹1.36 Cr
  Total Orders               99,441
  Total Customers            96,096
  Total Sellers               3,095
  Average Order Value       ₹137.75
  Average Review Score     4.09 / 5

------------------------------------------------------------------------

## 2. 📈 Sales Analysis

The dashboard includes:

### Monthly Revenue Trend

Tracks revenue across months and years to identify:

-   Growth trends
-   Seasonal patterns
-   High-revenue periods
-   Low-performing periods

### Revenue by Product Category

Identifies the top product categories by revenue.

### Top 10 Best-Selling Products

Ranks products based on units sold.

### Sales by Customer State

Shows how sales are distributed geographically across Brazilian states.

------------------------------------------------------------------------

## 3. 👥 Customer Analysis

### Customer Distribution by State

Identifies the geographical distribution of customers.

### Top 10 Customers by Spending

Highlights customers with the highest total spending.

### Repeat vs One-Time Customers

Classifies customers according to their number of orders.

This helps understand customer retention and repeat purchasing behavior.

------------------------------------------------------------------------

## 4. 🏪 Seller & Product Analysis

### Top 10 Sellers by Revenue

Identifies the highest-revenue sellers.

### Top 10 Sellers by Average Rating

Identifies highly rated sellers while applying a minimum order threshold
to avoid misleading ratings from very small numbers of orders.

### Product Category Performance

Compares product categories based on:

-   Items sold
-   Total orders
-   Revenue
-   Average item price

------------------------------------------------------------------------

## 5. 🚚 Delivery Analysis

### Average Delivery Time

The dashboard calculates the average number of days between:

-   Order purchase
-   Customer delivery

Current overall analysis shows an average delivery time of
approximately:

**12.50 days**

### On-Time vs Late Deliveries

Orders are classified as:

-   On Time
-   Late
-   Not Delivered

### Late Delivery Rate by State

Identifies states with higher late-delivery percentages.

### Delivery Performance vs Review Score

Compares customer review scores across delivery-performance groups.

------------------------------------------------------------------------

## 6. ⭐ Customer Experience

### Review Score Distribution

Shows the distribution of customer ratings from 1 to 5.

### Average Review Score by Product Category

Identifies categories with higher average customer ratings.

### Review Score by Delivery Performance

Examines how customer satisfaction differs based on delivery
performance.

------------------------------------------------------------------------

# 💡 Business Insights

The analysis supports several important business conclusions.

### 1. Delivery performance matters for customer satisfaction

The Welch's t-test found a statistically significant difference in
review scores between on-time and late deliveries.

**Business impact:** Improving delivery reliability can be an important
part of improving customer experience.

------------------------------------------------------------------------

### 2. Customer spending varies by product category

The ANOVA result was statistically significant, showing that average
order value differs across product categories.

**Business impact:** Product categories can be analyzed separately when
designing pricing, promotions, cross-selling, and revenue-growth
strategies.

------------------------------------------------------------------------

### 3. Payment method and order status are associated

The Chi-Square test produced an extremely small p-value, indicating a
statistically significant association between payment method and order
status.

**Business impact:** Payment methods and their related order outcomes
should be monitored to identify potential operational or
payment-processing patterns.

------------------------------------------------------------------------

### 4. Customer retention is important

The repeat-vs-one-time analysis helps quantify how many customers place
multiple orders.

**Business impact:** Increasing repeat purchases through customer
retention strategies can improve long-term customer value.

------------------------------------------------------------------------

### 5. Seller performance can be evaluated using multiple dimensions

Revenue and customer ratings provide complementary views of seller
performance.

**Business impact:** Sellers should not be evaluated using revenue
alone. Combining sales volume, revenue, order count, and customer
ratings gives a more complete picture.

------------------------------------------------------------------------

### 6. Geographic analysis can identify operational opportunities

Sales and delivery performance by customer state can reveal regions with
strong demand or higher delivery delays.

**Business impact:** Regional insights can support logistics planning,
seller allocation, and delivery optimization.

------------------------------------------------------------------------

# 🏗️ Project Structure

A suggested project structure is:

``` text
Olist-E-Commerce-Analysis/
│
├── Dashboard/
│   └── app.py
│
├── Data/
│   ├── raw/
│   └── cleaned/
│
├── Notebooks/
│   ├── Data_Quality_Analysis.ipynb
│   ├── Data_Cleaning.ipynb
│   ├── EDA.ipynb
│   └── Statistical_Analysis.ipynb
│
├── Documentation/
│   ├── Data_Dictionary.xlsx
│   ├── Data_Quality_Report.xlsx
│   └── Cleaning_Log.xlsx
│
├── README.md
└── requirements.txt
```

> Update the folder names to match the exact structure of your final
> project before uploading it to GitHub.

------------------------------------------------------------------------

# ⚙️ Installation

## 1. Clone the project

``` bash
git clone <your-repository-url>
cd Olist-E-Commerce-Analysis
```

## 2. Create a Python environment

``` bash
conda create -n olist_env python=3.11
conda activate olist_env
```

## 3. Install required libraries

``` bash
pip install pandas numpy scipy sqlalchemy pymysql streamlit openpyxl
```

------------------------------------------------------------------------

# 🗄️ MySQL Setup

Create the database:

``` sql
CREATE DATABASE olist_ecommerce;
```

Load the cleaned datasets into the appropriate tables according to the
ER diagram.

Update the database connection in `app.py`.

### ⚠️ Security Note

Do **not** commit database passwords or other credentials to GitHub.

Instead of hardcoding credentials such as:

``` python
password = "your_password"
```

use environment variables or Streamlit secrets in the final public
version.

------------------------------------------------------------------------

# ▶️ Running the Streamlit Dashboard

From the project directory:

``` bash
streamlit run Dashboard/app.py
```

The dashboard will open in your browser.

The application provides an interactive **year filter** and dynamically
updates the analytical charts based on the selected year.

------------------------------------------------------------------------

# 📈 Key Dashboard KPIs

The dashboard provides a quick executive view of:

``` text
Revenue
Orders
Customers
Sellers
Average Order Value
Average Review Score
```

These KPIs allow business stakeholders to quickly understand overall
platform performance before exploring detailed analyses.

------------------------------------------------------------------------

# 🧠 Skills Demonstrated

This project demonstrates practical knowledge of:

-   Python
-   Pandas
-   NumPy
-   SQL
-   MySQL
-   Data Cleaning
-   Data Quality Analysis
-   Exploratory Data Analysis
-   Feature Engineering
-   Statistical Hypothesis Testing
-   Data Visualization
-   Streamlit
-   Database Connectivity
-   Business Intelligence
-   Business Insight Generation

------------------------------------------------------------------------

# 🚀 Future Improvements

Potential future enhancements include:

-   Add profit and margin analysis if cost data becomes available
-   Add payment analysis to the dashboard
-   Add advanced customer segmentation
-   Add RFM analysis
-   Add interactive geographic maps
-   Add seller-level performance drilldowns
-   Add statistical post-hoc testing for ANOVA
-   Add confidence intervals and effect sizes
-   Add automated data refresh
-   Deploy the Streamlit dashboard online
-   Move database credentials to secure environment variables
-   Add automated tests for data quality

------------------------------------------------------------------------

# ✅ Project Completion Checklist

-   [x] Business problem defined
-   [x] Business use cases identified
-   [x] Dataset understanding completed
-   [x] ER diagram reviewed
-   [x] Data dictionary prepared
-   [x] Data quality analysis completed
-   [x] Data cleaning completed
-   [x] Cleaned data loaded into MySQL
-   [x] Feature engineering completed
-   [x] Exploratory data analysis completed
-   [x] T-Test completed
-   [x] ANOVA completed
-   [x] Chi-Square test completed
-   [x] SQL analysis completed
-   [x] Streamlit dashboard created
-   [x] Interactive year filter added
-   [x] Dashboard KPI cards added
-   [x] Dashboard charts added
-   [x] Dashboard presentation polished
-   [x] Business insights identified
-   [ ] Add final dashboard screenshots
-   [ ] Add final GitHub repository link
-   [ ] Remove hardcoded database credentials before public upload

------------------------------------------------------------------------

# 🏁 Conclusion

This project demonstrates an end-to-end approach to transforming raw
e-commerce data into actionable business intelligence.

By combining **Python, Pandas, SQL, MySQL, statistical analysis, and
Streamlit**, the project provides a structured view of business
performance across sales, customers, products, sellers, payments,
delivery operations, and customer experience.

The final dashboard enables stakeholders to explore the data
interactively and use evidence-based insights to support business
decisions.

------------------------------------------------------------------------

## 👩‍💻 Project

**Olist E-Commerce Performance Analysis**

Built as part of an **AI/ML & Data Analytics learning project**.
