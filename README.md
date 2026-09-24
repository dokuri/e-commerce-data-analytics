# 🛒 E-Commerce Sales & Customer Analytics Dashboard

A single-file **Streamlit + Plotly** dashboard that turns an orders CSV into sales trends, product performance,
customer segmentation (RFM) and operations insights.

The bundled dataset is **300 synthetic orders** from 102 customers across 14 Indian cities
(1 Oct 2025 – 20 Sep 2026, amounts in ₹). No real people or businesses are represented.

## 1. Files

```
01_ecommerce_dashboard/
├── main.py                    # the whole app: data + analytics + dashboard
├── requirements.txt           # Python libraries to install
├── data/ecommerce_sales.csv   # 300 orders × 22 columns
└── README.md
```

## 2. Requirements

* Python 3.9 or newer
* Libraries: `streamlit`, `pandas`, `numpy`, `plotly`

```bash
pip install -r requirements.txt
```

(Equivalent to `pip install streamlit pandas numpy plotly`.)

## 3. Run

```bash
streamlit run main.py
```

Streamlit opens the dashboard at <http://localhost:8501>. (If the port is busy: `streamlit run main.py --server.port 8502`.)

## 4. How it works

`main.py` is organised in three sections, top to bottom:

1. **Settings** – page configuration, path to the CSV, currency symbol.
2. **Data & analytics** – plain pandas functions, no Streamlit calls:
   * `load_data()` reads the CSV, checks that all required columns exist, and adds helper columns
     (`order_month`, `weekday`, `age_group`, `is_revenue`, `net_revenue`).
   * `apply_filters()` narrows the orders using the sidebar choices.
   * `compute_kpis()` and the `*_summary()` / `rfm_table()` functions produce every number and table behind a chart.
3. **Dashboard (UI)** – sidebar filters → KPI cards → five tabs of Plotly charts. The default CSV is cached with
   `st.cache_data`; you can also upload your own CSV from the sidebar.

```
data/ecommerce_sales.csv → load_data() → apply_filters(sidebar) → KPIs + summaries → Plotly charts
```

### Business rules
| Metric | Definition |
|---|---|
| **Net revenue** | Sum of `total_amount` for orders that are *Delivered, Shipped or Processing*. Cancelled and Returned orders are excluded. |
| **Average order value** | Mean `total_amount` of those revenue orders. |
| **Repeat-customer rate** | Share of customers with more than one order in the selected range. |
| **Cancellation / return rate** | Cancelled (or Returned) orders ÷ all orders. |
| **RFM segment** | Each customer is scored 1–4 on **R**ecency, **F**requency and **M**onetary value (quartile ranks). Sum 10–12 = *Champions*, 8–9 = *Loyal*, 6–7 = *Promising*, 3–5 = *At Risk*. |

### Dashboard tabs
| Tab | What you see |
|---|---|
| 📈 Sales trends | Monthly revenue & orders, revenue by category over time, revenue by weekday |
| 🛍️ Products | Category revenue, average discount, product treemap, top-10 products |
| 👥 Customers | RFM segments, frequency-vs-spend scatter, new vs. returning revenue, age groups, top customers |
| 🚚 Operations | Order-status and payment mix, acquisition channels, top states, delivery-time histogram, ratings |
| 🗂️ Data | Filtered table + CSV download |

## 5. Data dictionary (`data/ecommerce_sales.csv`)

| Column | Description |
|---|---|
| `order_id` | Unique order number (ORD100001…) |
| `order_date` | Date the order was placed (YYYY-MM-DD) |
| `customer_id`, `customer_name` | Customer identifiers (synthetic) |
| `gender`, `age` | Customer demographics |
| `city`, `state` | Delivery location |
| `product_category`, `product_name` | 7 categories, 30 products |
| `quantity`, `unit_price` | Units ordered and price per unit (₹) |
| `discount_pct` | Discount applied (0–40 %), higher during Diwali / Republic-Day / year-end sales |
| `shipping_fee` | ₹0 if the discounted subtotal ≥ ₹499, else ₹49 |
| `total_amount` | `quantity × unit_price × (1 − discount) + shipping_fee` |
| `payment_method` | UPI, Credit/Debit Card, Net Banking, Cash on Delivery, Wallet |
| `device` | Mobile, Desktop, Tablet |
| `acquisition_channel` | Organic Search, Social Media, Email Campaign, Referral, Paid Ads, Direct |
| `order_status` | Delivered, Shipped, Processing, Cancelled, Returned |
| `delivery_days` | Days to deliver (blank if not delivered/returned) |
| `rating` | 1–5 customer rating (blank if not rated) |
| `customer_type` | `New` = customer's first order in the dataset, otherwise `Returning` |

### Sanity check
With no filters you should see: **300 orders · 102 customers · ₹6,29,686 net revenue · AOV ₹2,350 ·
repeat rate 72.5 % · cancellation 5.7 % · returns 5.0 % · avg rating 3.78**.

## 6. Using your own data
Provide a CSV with the same 22 column names (extra columns are fine; missing ones show a clear error) and upload it
from the sidebar, or replace `data/ecommerce_sales.csv`. Dates must be `YYYY-MM-DD`.

## 7. Troubleshooting
* `ModuleNotFoundError` → run the `pip install` line in section 2 (inside your virtual environment, if you use one).
* Blank charts → your sidebar filters exclude every order; clear them.
