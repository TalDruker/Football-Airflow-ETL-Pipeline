#  Automated Football Data Pipeline & BI Dashboard

End-to-end data engineering and business intelligence project. The system automatically ingests football match metrics from MongoDB, orchestrates the ETL process using Apache Airflow and Pandas, loads the structured data into PostgreSQL, and provides a comprehensive analytical dashboard via Power BI.

---

# System Architecture & Workflow

1. **Extract:** Ingests raw match and player records from **MongoDB**.
2. **Transform:** Sanitizes, normalizes, handles missing values, and caps metric outliers using **Python & Pandas** inside an **Apache Airflow** DAG.
3. **Load:** Persists the cleaned dataset into a relational **PostgreSQL** database.
4. **Visualize:** Analyzed and explored through an interactive **Power BI** report.
