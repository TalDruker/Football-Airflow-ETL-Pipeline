# Football Analytics & ETL Pipeline

An end-to-end data project that automates the flow of football match data from storage to an interactive Power BI dashboard for tactical analysis.

![Main Menu Overview](mainMenu.png)

---

## About the Project
I built this project to serve as a practical decision-making tool for football coaching staffs. Instead of just crunching numbers, the goal was to turn raw statistics into clear tactical insights focusing on player performance, monthly trends, and match aggression.

## Key Features & Views
* **Main Menu Hub:** Centralized navigation with dynamic filters and quick access to individual club stats (like Beitar Jerusalem, Hapoel Tel Aviv, and Maccabi Haifa).
* **Key Players:** Highlights top performers, match impact, and individual contributions to goals and assists.
* **Seasonality Analysis:** Tracks monthly performance spikes and trends across the season.
* **Risk & Aggression:** Evaluates tactical discipline and booking trends over time.

---

## How the Pipeline Works 
1. **Extract:** Pulls raw match and player records from **MongoDB**.
2. **Transform:** Cleans, normalizes, and processes data using **Python & Pandas** inside an **Apache Airflow DAG**.
3. **Load:** Stores the structured data into a relational **PostgreSQL** database.
4. **Visualize:** Connects directly to **Power BI** for final reporting and exploration.

---

##  Interactive Dashboard Demos

### 1. Risk & Aggression Analysis
![Risk & Aggression Analysis](Risk%20&%20Aggression%20Analysis.gif)
*Dynamic tracking of tactical discipline, monthly card distributions, and quarterly trends across teams.*

### 2. Club Analysis
![Club Analysis](Club%20Analysis.gif)
*Granular tactical view showcasing club-specific performance, positional breakdowns, and monthly growth indicators.*

---

## Dashboard Static Views

### 1. Age Groups & Performance
![Age Groups & Performance](Age%20Groups%20&%20Performance.png)
*Analyzes player performance, running distance metrics, and efficiency distribution across various career age groups.*

### 2. Seasonality Analysis
![Seasonality Analysis](Seasonality%20Analysis.png)
*Examines monthly and quarterly trends, year filters, and performance behavioral patterns throughout the season.*

### 3. Team Performance Deep-Dive (Hapoel Tel Aviv)
![Hapoel Tel Aviv statistics](Hapoel%20Tel%20Aviv%20satistics.png)
*Detailed tactical and granular analysis of a specific club, showcasing key performance indicators and positional breakdowns.*


### Data Model
![View data model](View%20data%20model.png)
* **`Data_football` (Fact Table):** Stores match records, player metrics, and performance indicators.
* **`DimDate` (Dimension Table):** Linked via a one-to-many relationship for time-intelligence.
* **`!Measures`:** Centralized table organizing custom DAX logic (MoM trends, top player identification, and efficiency tracking).

## 📐 6. Advanced DAX Measures
Core custom DAX logic implemented for deep tactical analysis, grouped together:

```dax
-- 1. Month-over-Month Change in Goal & Assist Contributions
Next_Month_Change = 
VAR Current_Month_Num = SELECTEDVALUE(DimDate[Month Number])
VAR Current_Val = [Total_goals_assists]
VAR Prev_Val = 
    CALCULATE(
        [Total_goals_assists],
        ALLEXCEPT(DimDate, DimDate[Year]),
        DimDate[Month Number] = Current_Month_Num - 1
    )
RETURN
    IF(
        ISBLANK(Current_Val) || ISBLANK(Prev_Val) || Prev_Val = 0,
        BLANK(),
        DIVIDE(Current_Val - Prev_Val, Prev_Val)
    )

-- 2. Dynamic Best Player per Selected Team
Best_Player_from_team = 
VAR CurrentPlayerScore = [Total_goals_assists]
VAR CurrentTeam = SELECTEDVALUE(Data_football[Team])
VAR MaxScoreInTeam = 
    MAXX(
        FILTER(
            ALL(Data_football), 
            Data_football[Team] = CurrentTeam
        ), 
        [Total_goals_assists]
    )
RETURN
    IF(CurrentPlayerScore = MaxScoreInTeam && NOT(ISBLANK(CurrentPlayerScore)), CurrentPlayerScore, BLANK())

-- 3. Player Efficiency (Minutes per Goal/Assist)
Minutes per G/A = DIVIDE(
    SUM(Data_football[Minutes_Played]), 
    SUM(Data_football[Goals]) + SUM(Data_football[Assists])
)

-- 4. Previous Month Goals & Assists (Time Intelligence)
Previous_Month_Goals_Assists = 
CALCULATE(
    [Total_goals_assists], 
    DATEADD(DimDate[Date], -1, MONTH)
)

##  Key Insights & Conclusions

* **Player Age Impact:** Performance analysis reveals a high concentration of offensive contributions (Goals & Assists) within the *Prime Career* group, alongside significant physical workload volumes.
* **Seasonal Trends:** The data clearly highlights how metrics shift across specific months using interactive slicers, pointing to performance peaks and tactical adjustments over time.
* **Granular Team Focus:** Transitioning to individual club analysis (such as Hapoel Tel Aviv) enables the identification of micro-level strengths and weaknesses, including running distance efficiency and match outcomes.
