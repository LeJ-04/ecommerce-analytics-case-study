# 📊 E-Commerce Strategic Dashboard: 5 Actionable Business Indicators


![Python](https://img.shields.io/badge/Python-3.x-blue)


This project focuses on transforming raw transactional data into strategic business insights. Using a dataset of **10,000 invoices**, I developed a comprehensive analysis and an interactive dashboard designed to support data-driven decision-making for e-commerce managers.


## 🎯 Project Objective

The goal was to move beyond simple data exploration and extract **5 key actionable indicators** to optimize sales, inventory management, and marketing targeting.


## 🚀 Key Business Indicators

1. **Strategic Product Matrix (BCG)**: Categorizes products into Stars, Premium, Volume, and Standard to prioritize stock and marketing investments.

2. **ABC/Pareto Analysis**: Identifies the high-value products responsible for 80% of the total revenue.

3. **Geographic Performance**: Maps city-level performance based on a custom "Potential Score" combining revenue, customer count, and average basket value.

4. **B2B Customer Profiling**: Analyzes purchase behavior across different professions to identify high-value industrial segments.

5. **Basket Size Distribution**: Segmenting orders (Small, Medium, Large) using Min-Max normalization to optimize shipping thresholds and cross-selling.


## 🛠️ Tech Stack

- **Language**: `Python`
- **Data Manipulation**: `Pandas`, `NumPy`
- **Visualization**: `Plotly Express`, `Plotly Graph Objects`
- **Dashboarding**: `Dash` (Flask-based web framework)


## 💡 Analytical Depth: Synthetic Data Awareness

During the Exploration phase (EDA), I identified the synthetic nature of the dataset (highly homogeneous distribution, lack of seasonality). Rather than a limitation, I used this as a methodological framework to demonstrate how these business models (BCG, ABC) should be applied and interpreted in a real-world corporate environment.


## 📂 Project Resources

- [View the Full Canva Presentation](https://github.com/LeJ-04/ecommerce-analytics-case-study/blob/main/assets/presentation.pdf) — *Summary of business recommendations*.
- `project_ds_invoices.ipynb` — *Complete data processing and visualization pipeline*.
- `invoices.csv` — *Dataset containing 10,002 transactions*.


## 🔧 Installation & Usage

1. **Clone the repo**:
```bash
git clone https://github.com/your-username/ecommerce-dashboard.git
```

2. **Install dependencies**:
```bash
pip install pandas plotly dash
```

3. Run the Dashboard:
```bash
python app.py  # or run the last cell of the notebook
```
