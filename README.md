# 🛒 E-Commerce Sales & Customer Analytics Dashboard

A single-file **Streamlit + Plotly** dashboard that turns an orders CSV into sales trends, product performance, customer segmentation (RFM), and operations insights.

The dashboard uses an orders CSV supplied by the user. No synthetic dataset is bundled with the project.

## 1. Files

```text
01_ecommerce_dashboard/
├── main.py
├── requirements.txt
└── README.md
```

## 2. Requirements

* Python 3.9 or newer
* Libraries:

  * `streamlit`
  * `pandas`
  * `numpy`
  * `plotly`

Install the required libraries:

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install streamlit pandas numpy plotly
```

## 3. Run

```bash
streamlit run main.py
```

Streamlit normally opens the dashboard at:

```text
http://localhost:8501
```

If the port is busy:

```bash
streamlit run main.py --server.port 8502
```

## 4. How It Works

`main.py` is organized into three main sections:

### 1. Settings

Configures:

* Streamlit page settings
* Currency symbol
* Application settings

### 2. Data & Analytics

The application:

* Reads the uploaded CSV
* Checks that required columns exist
* Converts dates and numeric values
* Creates analytical helper columns
* Applies sidebar filters
* Calculates KPIs
* Performs RFM customer segmentation
* Generates summary tables for the dashboard

Helper columns may include:

```text
order_month
weekday
age_group
is_revenue
net_revenue
```

### 3. Dashboard

The dashboard follows this workflow:

```text
User CSV
   ↓
Data Validation
   ↓
Data Cleaning
   ↓
Sidebar Filters
   ↓
KPI Calculations
   ↓
Analytics
   ↓
Plotly Visualizations
   ↓
Streamlit Dashboard
```

## Business Rules

| Metric                   | Definition                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **Net revenue**          | Sum of `total_amount` for orders that are Delivered, Shipped, or Processing. Cancelled and Returned orders are excluded. |
| **Average order value**  | Mean `total_amount` of revenue-generating orders.                                                                        |
| **Repeat-customer rate** | Share of customers with more than one order in the selected range.                                                       |
| **Cancellation rate**    | Cancelled orders divided by all orders.                                                                                  |
| **Return rate**          | Returned orders divided by all orders.                                                                                   |
| **RFM segment**          | Customers are scored on Recency, Frequency, and Monetary value using quartile-based scores.                              |

### RFM Segments

```text
10–12 → Champions
8–9   → Loyal
6–7   → Promising
3–5   → At Risk
```

## Dashboard Tabs

| Tab                 | What You See                                                                                 |
| ------------------- | -------------------------------------------------------------------------------------------- |
| 📈 **Sales Trends** | Monthly revenue, order trends, category revenue, weekday revenue                             |
| 🛍️ **Products**    | Category revenue, discounts, product treemap, top products                                   |
| 👥 **Customers**    | RFM segments, frequency vs. spending, new vs. returning customers, age groups, top customers |
| 🚚 **Operations**   | Order status, payment methods, acquisition channels, locations, delivery time, ratings       |
| 🗂️ **Data**        | Filtered data table and CSV download                                                         |

## 5. Data Dictionary

Your CSV should contain the following columns:

| Column                | Description                              |
| --------------------- | ---------------------------------------- |
| `order_id`            | Unique order number                      |
| `order_date`          | Date the order was placed (`YYYY-MM-DD`) |
| `customer_id`         | Unique customer identifier               |
| `customer_name`       | Customer name                            |
| `gender`              | Customer gender                          |
| `age`                 | Customer age                             |
| `city`                | Delivery city                            |
| `state`               | Delivery state                           |
| `product_category`    | Product category                         |
| `product_name`        | Product name                             |
| `quantity`            | Number of units ordered                  |
| `unit_price`          | Price per unit in ₹                      |
| `discount_pct`        | Discount percentage                      |
| `shipping_fee`        | Shipping fee in ₹                        |
| `total_amount`        | Final order amount                       |
| `payment_method`      | Payment method                           |
| `device`              | Device used for the order                |
| `acquisition_channel` | Customer acquisition channel             |
| `order_status`        | Order status                             |
| `delivery_days`       | Number of days required for delivery     |
| `rating`              | Customer rating from 1–5                 |
| `customer_type`       | New or Returning customer                |

## 6. Using Your Own Data

Upload your own e-commerce CSV using the **CSV uploader in the Streamlit sidebar**.

Your CSV should contain the required columns listed in the data dictionary.

Extra columns are allowed.

If required columns are missing, the application displays an error explaining which columns are missing.

### Date Format

The recommended date format is:

```text
YYYY-MM-DD
```

Example:

```text
2026-08-15
```

### Order Status

Typical order statuses include:

```text
Delivered
Shipped
Processing
Cancelled
Returned
```

### Payment Methods

Examples include:

```text
UPI
Credit/Debit Card
Net Banking
Cash on Delivery
Wallet
```

### Customer Type

```text
New
Returning
```

A customer is considered **New** when the order represents their first recorded order in the dataset. Subsequent orders are classified as **Returning**.

## 7. RFM Analysis

RFM analysis is used to understand customer purchasing behavior.

### Recency

Measures how recently a customer placed an order.

```text
Lower number of days = More recent customer
```

### Frequency

Measures how frequently the customer orders.

```text
Higher number of orders = Higher frequency
```

### Monetary

Measures the customer's spending.

```text
Higher spending = Higher monetary value
```

The three measures are converted into scores and combined to create customer segments.

## 8. Customer Analytics

The dashboard provides:

* Customer count
* Repeat-customer rate
* RFM segmentation
* Customer frequency
* Customer spending
* New vs. returning customers
* Age-group analysis
* Top customers
* Customer revenue contribution

## 9. Product Analytics

Product analysis includes:

* Revenue by category
* Revenue by product
* Top-selling products
* Average discount
* Product performance
* Product treemap
* Quantity analysis

## 10. Sales Analytics

Sales analysis includes:

* Monthly revenue
* Monthly order count
* Revenue trends
* Category revenue trends
* Weekday sales
* Average order value
* Net revenue

## 11. Operations Analytics

The operations section analyzes:

* Order status
* Payment methods
* Acquisition channels
* Delivery locations
* Delivery duration
* Customer ratings
* Cancellation and return patterns

## 12. Data Processing

The application performs several data-processing operations using Pandas and NumPy.

Examples include:

```python
pd.read_csv()
```

for loading the CSV.

```python
pd.to_datetime()
```

for processing order dates.

```python
groupby()
```

for aggregating sales and customer information.

```python
merge()
```

when combining analytical datasets.

```python
numpy
```

for numerical calculations and transformations.

## 13. Visualization

The dashboard uses Plotly for interactive visualizations, including:

* Bar charts
* Line charts
* Pie charts
* Scatter plots
* Treemaps
* Histograms
* Interactive tables

Users can hover over charts to inspect individual values and interact with the visualizations.

## 14. CSV Download

After applying filters, users can download the filtered dataset using:

```text
⬇️ Download Filtered CSV
```

The downloaded file contains the currently filtered records.

## 15. Project Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Pandas
* NumPy
* Exploratory Data Analysis
* Data Cleaning
* Data Transformation
* RFM Analysis
* Customer Segmentation
* Sales Analytics
* E-Commerce Analytics
* Business Intelligence
* Data Visualization
* Plotly
* Streamlit
* CSV Data Processing
* Interactive Dashboard Development

## 16. Project Objective

The objective of this project is to transform e-commerce order data into an interactive analytics dashboard that helps analyze:

```text
Sales
  +
Products
  +
Customers
  +
RFM Segmentation
  +
Operations
  +
Business KPIs
      ↓
Interactive E-Commerce Dashboard
```

## 17. Project Type

**Domain:** E-Commerce

**Project Category:** Data Analytics & Business Intelligence

**Application:** Interactive Sales & Customer Analytics Dashboard

**Data Source:** User-provided CSV

**Synthetic Data:** Not included

**Machine Learning:** Not required

**Dashboard Framework:** Streamlit

**Visualization:** Plotly

## 18. Troubleshooting

### `ModuleNotFoundError`

Install the required packages:

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install streamlit pandas numpy plotly
```

### No Data Displayed

Make sure that a CSV file has been uploaded through the Streamlit sidebar.

### Missing Column Error

Check that your CSV contains all required column names listed in the **Data Dictionary**.

### Blank Charts

Your sidebar filters may exclude all available orders.

Clear or change the selected filters and try again.

### Streamlit Port Error

Run the application using another port:

```bash
streamlit run main.py --server.port 8502
```

---

## 👨‍💻 Author

**Dokuri Shilish Reddy**

Data Analyst | Python | SQL | Power BI | Data Analytics
