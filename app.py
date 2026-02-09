import streamlit as st
import pandas as pd
import plotly.express as px
from db_config import get_connection

# ----------------------------------
# STATE NAME MAPPING (REQUIRED FOR INDIA MAP)
# ----------------------------------
STATE_NAME_MAPPING = {
    "andaman-&-nicobar-islands": "Andaman and Nicobar Islands",
    "andhra-pradesh": "Andhra Pradesh",
    "arunachal-pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra-&-nagar-haveli-&-daman-&-diu": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal-pradesh": "Himachal Pradesh",
    "jammu-&-kashmir": "Jammu and Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya-pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "puducherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil-nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar-pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west-bengal": "West Bengal"
}

def show_sample_data(table_name, conn):
    query = f"SELECT * FROM {table_name} LIMIT 5"
    df = pd.read_sql(query, conn)
    st.markdown("**Sample Data (First 5 Rows):**")
    st.dataframe(df)

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config("PhonePe Pulse | Insights", layout="wide")

# ----------------------------------
# PURPLE THEME
# ----------------------------------
st.markdown("""
<style>
.metric-box {
    background:#2b014f;
    padding:20px;
    border-radius:12px;
    color:white;
    text-align:center;
}
.metric-title {color:#cfc6ff; font-size:16px;}
.metric-value {color:#00e5ff; font-size:28px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# HELPERS
# ----------------------------------
def to_crore(val):
    return round(val / 1e7, 2)

def to_lakh(val):
    return round(val / 1e5, 2)

# ----------------------------------
# DB CONNECTION
# ----------------------------------
conn = get_connection()

# ----------------------------------
# SIDEBAR
# ----------------------------------
st.sidebar.title("📊 PhonePe Pulse")
page = st.sidebar.radio("Navigate", ["Home", "Business Case Analysis", "Reports", "Database", "About", "Creator"])

years = pd.read_sql("SELECT DISTINCT Year FROM aggregated_transaction ORDER BY Year", conn)["Year"]
quarters = pd.read_sql("SELECT DISTINCT Quarter FROM aggregated_transaction ORDER BY Quarter", conn)["Quarter"]

year = st.sidebar.selectbox("Year", years)
quarter = st.sidebar.selectbox("Quarter", quarters)

# ==================================
# HOME PAGE
# ==================================
if page == "Home":
    st.title("🇮🇳 PhonePe Pulse – India Overview")

    category = st.selectbox(
        "Select Category",
        ["Transactions", "Users", "Insurance"]
    )

    # =================================================
    # TRANSACTIONS
    # =================================================
    if category == "Transactions":

        # ---------- KPI METRICS ----------
        q = f"""
        SELECT 
            SUM(Transaction_Count) AS total_txn,
            SUM(Transaction_Amount) AS total_amt
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        """
        m = pd.read_sql(q, conn)

        c1, c2 = st.columns(2)
        c1.markdown(
            f"<div class='metric-box'><div class='metric-title'>Total Transactions</div>"
            f"<div class='metric-value'>{int(m.total_txn[0]):,}</div></div>",
            unsafe_allow_html=True
        )
        c2.markdown(
            f"<div class='metric-box'><div class='metric-title'>Total Value (₹ Cr)</div>"
            f"<div class='metric-value'>₹ {round(m.total_amt[0]/1e7,2)}</div></div>",
            unsafe_allow_html=True
        )

        # ---------- INDIA MAP ----------
        map_q = f"""
        SELECT State, SUM(Transaction_Amount) AS value
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        """
        df_map = pd.read_sql(map_q, conn)

        df_map["State"] = df_map["State"].map(STATE_NAME_MAPPING)
        df_map["Value_Display"] = df_map["value"].apply(
            lambda x: f"₹ {round(x/1e7,2)} Cr"
        )
        df_map["value_plot"] = df_map["value"] / 1e7

        fig = px.choropleth(
            df_map,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/india_states.geojson",
            featureidkey="properties.ST_NM",
            locations="State",
            color="value_plot",
            hover_name="State",
            hover_data={"Value_Display": True, "value_plot": False},
            color_continuous_scale="Plasma",
            title=f"State-wise Transaction Value – Q{quarter} {year}"
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=650)
        st.plotly_chart(fig, use_container_width=True)

        # ---------- TOP 10 STATES ----------
        st.subheader("🏆 Top 10 States by Transaction Value (₹ Cr)")
        q1 = f"""
        SELECT State, SUM(Transaction_Amount) amt
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        ORDER BY amt DESC
        LIMIT 10
        """
        df = pd.read_sql(q1, conn)
        df["Amount (₹ Cr)"] = df["amt"].apply(lambda x: round(x/1e7,2))
        st.bar_chart(df.set_index("State")["Amount (₹ Cr)"])

        # ---------- TOP 10 DISTRICTS ----------
        st.subheader("🏙️ Top 10 Districts by Transaction Value (₹ Lakh)")
        q2 = f"""
        SELECT District, SUM(Transaction_Amount) amt
        FROM map_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY District
        ORDER BY amt DESC
        LIMIT 10
        """
        df2 = pd.read_sql(q2, conn)
        df2["Amount (₹ Lakh)"] = df2["amt"].apply(lambda x: round(x/1e5,2))
        st.table(df2[["District", "Amount (₹ Lakh)"]])

    # =================================================
    # USERS
    # =================================================
    elif category == "Users":

        # ---------- INDIA MAP ----------
        map_q = f"""
        SELECT State, SUM(User_Count) AS value
        FROM aggregated_user
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        """
        df_map = pd.read_sql(map_q, conn)

        df_map["State"] = df_map["State"].map(STATE_NAME_MAPPING)
        df_map["Value_Display"] = df_map["value"].apply(lambda x: f"{int(x):,} Users")

        fig = px.choropleth(
            df_map,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/india_states.geojson",
            featureidkey="properties.ST_NM",
            locations="State",
            color="value",
            hover_name="State",
            hover_data={"Value_Display": True, "value": False},
            color_continuous_scale="Purples",
            title=f"State-wise Registered Users – Q{quarter} {year}"
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=650)
        st.plotly_chart(fig, use_container_width=True)

        # ---------- DEVICE DISTRIBUTION ----------
        st.subheader("📱 Device-wise User Distribution")
        q = f"""
        SELECT User_Device, SUM(User_Count) users
        FROM aggregated_user
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY User_Device
        ORDER BY users DESC
        """
        df = pd.read_sql(q, conn)
        st.bar_chart(df.set_index("User_Device"))

    # =================================================
    # INSURANCE
    # =================================================
    else:
        st.subheader("🛡️ Insurance Overview")

        # ---------- INDIA MAP ----------
        map_q = f"""
        SELECT State, SUM(Insurance_Amount) AS value
        FROM aggregated_insurance
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        """
        df_map = pd.read_sql(map_q, conn)

        # Map PhonePe state names → GeoJSON state names
        df_map["State"] = df_map["State"].map(STATE_NAME_MAPPING)

        # Prepare display & plot values
        df_map["value_plot"] = df_map["value"] / 1e5   # for color scale
        df_map["Value_Display"] = df_map["value_plot"].apply(
            lambda x: f"₹ {x:.2f} Lakh"
        )

        fig = px.choropleth(
            df_map,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/india_states.geojson",
            featureidkey="properties.ST_NM",
            locations="State",
            color="value_plot",
            hover_name="State",
            hover_data={
                "Value_Display": True,
                "value_plot": False
            },
            color_continuous_scale="Oranges",
            title=f"State-wise Insurance Transaction Value – Q{quarter} {year}"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=650)

        st.plotly_chart(fig, use_container_width=True)

        # ---------- TOP 10 STATES ----------
        st.subheader("🏥 Top 10 States by Insurance Value (₹ Lakh)")

        top_q = f"""
        SELECT State, SUM(Insurance_Amount) AS amt
        FROM aggregated_insurance
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        ORDER BY amt DESC
        LIMIT 10
        """
        df_top = pd.read_sql(top_q, conn)
        df_top["Amount (₹ Lakh)"] = df_top["amt"].apply(
            lambda x: round(x / 1e5, 2)
        )

        st.bar_chart(df_top.set_index("State")["Amount (₹ Lakh)"])



# ==================================
# BUSINESS CASE ANALYSIS (CLEAN TABS)
# ==================================
elif page == "Business Case Analysis":
    st.title("📘 Business Case Studies")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1️⃣ Transaction Dynamics",
        "2️⃣ Device Dominance",
        "3️⃣ Insurance Growth",
        "4️⃣ Market Expansion",
        "5️⃣ User Engagement"
    ])

    # ---------- CASE 1 ----------
    with tab1:
        st.markdown("### Decoding Transaction Dynamics on PhonePe")
        st.markdown("**Table used:** `aggregated_transaction` (state + transaction type trends)")

        q = f"""
        SELECT Transaction_Type, SUM(Transaction_Count) count
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY Transaction_Type
        """
        st.code(q)
        df = pd.read_sql(q, conn)
        st.dataframe(df)
        st.bar_chart(df.set_index("Transaction_Type"))
        

    # ---------- CASE 2 ----------
    with tab2:
        st.markdown("### Device Dominance and User Engagement Analysis")
        st.markdown("**Table used:** `aggregated_user` (device-wise user distribution)")

        q = f"""
        SELECT User_Device, SUM(User_Count) users
        FROM aggregated_user
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY User_Device
        ORDER BY users DESC
        """
        st.code(q)
        df = pd.read_sql(q, conn)
        st.dataframe(df)
        st.bar_chart(df.set_index("User_Device"))
        

    # ---------- CASE 3 ----------
    with tab3:
        st.markdown("### Insurance Penetration and Growth Potential Analysis")
        st.markdown("**Table used:** `aggregated_insurance` (state-level insurance value)")

        q = f"""
        SELECT State, SUM(Insurance_Amount) amt
        FROM aggregated_insurance
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        ORDER BY amt DESC
        """
        st.code(q)
        df = pd.read_sql(q, conn)
        df["₹ Lakh"] = df["amt"].apply(to_lakh)
        st.dataframe(df[["State", "₹ Lakh"]])
        

    # ---------- CASE 4 ----------
    with tab4:
        st.markdown("### Transaction Analysis for Market Expansion")
        st.markdown("**Table used:** `map_transaction` (district-level transaction value)")

        q = f"""
        SELECT District, SUM(Transaction_Amount) amt
        FROM map_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY District
        ORDER BY amt DESC
        LIMIT 10
        """
        st.code(q)
        df = pd.read_sql(q, conn)
        df["₹ Lakh"] = df["amt"].apply(to_lakh)
        st.table(df[["District", "₹ Lakh"]])
        

    # ---------- CASE 5 ----------
    with tab5:
        st.markdown("### User Engagement and Growth Strategy")
        st.markdown("**Table used:** `map_user` (district-wise user count)")

        q = f"""
        SELECT District, User_Count
        FROM map_user
        WHERE Year={year} AND Quarter={quarter}
        ORDER BY User_Count DESC
        LIMIT 10
        """
        st.code(q)
        df = pd.read_sql(q, conn)
        st.table(df)
        

# ==================================
# REPORTS PAGE (REAL PDF REPORT)
# ==================================
elif page == "Reports":
    st.title("📄 Quarterly Analytics Report")

    st.markdown("""
This report summarizes **what happened in the selected quarter**,  
based on **PhonePe Pulse data**, similar to real-world analytics reports.
""")

    # ---------------------------
    # REPORT FILTERS
    # ---------------------------
    report_category = st.selectbox(
        "Select Report Category",
        ["Transactions", "Users", "Insurance"]
    )

    st.markdown(f"""
**Selected Period:**  
📅 Year: **{year}**  
📊 Quarter: **Q{quarter}**
""")

    # ---------------------------
    # DATA EXTRACTION BASED ON CATEGORY
    # ---------------------------
    if report_category == "Transactions":

        st.subheader("🔍 Transaction Summary")

        summary_query = f"""
        SELECT 
            SUM(Transaction_Count) AS total_txn,
            SUM(Transaction_Amount) AS total_amt
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        """
        summary_df = pd.read_sql(summary_query, conn)

        st.dataframe(summary_df)

        top_states_query = f"""
        SELECT State, SUM(Transaction_Amount) AS amt
        FROM aggregated_transaction
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        ORDER BY amt DESC
        LIMIT 10
        """
        top_states_df = pd.read_sql(top_states_query, conn)
        st.subheader("🏆 Top 10 States by Transaction Value")
        st.dataframe(top_states_df)

        narrative = (
            f"In Q{quarter} {year}, PhonePe recorded "
            f"{int(summary_df.total_txn[0]):,} transactions "
            f"with a total value of ₹{round(summary_df.total_amt[0]/1e7,2)} Cr. "
            "Transaction activity was concentrated in top-performing states."
        )

    elif report_category == "Users":

        st.subheader("🔍 User Engagement Summary")

        summary_query = f"""
        SELECT SUM(User_Count) AS total_users
        FROM aggregated_user
        WHERE Year={year} AND Quarter={quarter}
        """
        summary_df = pd.read_sql(summary_query, conn)
        st.dataframe(summary_df)

        device_query = f"""
        SELECT User_Device, SUM(User_Count) AS users
        FROM aggregated_user
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY User_Device
        ORDER BY users DESC
        """
        device_df = pd.read_sql(device_query, conn)
        st.subheader("📱 Device-wise User Distribution")
        st.dataframe(device_df)

        narrative = (
            f"In Q{quarter} {year}, PhonePe had "
            f"{int(summary_df.total_users[0]):,} registered users. "
            "Android devices continued to dominate user adoption."
        )

    else:  # Insurance

        st.subheader("🔍 Insurance Adoption Summary")

        summary_query = f"""
        SELECT COALESCE(SUM(Insurance_Amount), 0) AS total_amt
        FROM aggregated_insurance
        WHERE Year = {year} AND Quarter = {quarter}


        """
        summary_df = pd.read_sql(summary_query, conn)
        st.dataframe(summary_df)

        top_states_query = f"""
        SELECT State, SUM(Insurance_Amount) AS amt
        FROM aggregated_insurance
        WHERE Year={year} AND Quarter={quarter}
        GROUP BY State
        ORDER BY amt DESC
        LIMIT 10
        """
        top_states_df = pd.read_sql(top_states_query, conn)
        st.subheader("🏥 Top 10 States by Insurance Value")
        st.dataframe(top_states_df)

        narrative = (
            f"In Q{quarter} {year}, insurance transactions reached "
            f"₹{round(summary_df.total_amt[0]/1e5,2)} Lakh in value. "
            "Adoption remains concentrated in select states."
        )

    # ---------------------------
    # GENERATE PDF
    # ---------------------------
    if st.button("📥 Generate & Download PDF Report"):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            c = canvas.Canvas(tmp.name, pagesize=A4)
            text = c.beginText(40, 800)
            text.setFont("Helvetica", 11)

            text.textLine("PhonePe Pulse – Quarterly Analytics Report")
            text.textLine("-" * 50)
            text.textLine(f"Category: {report_category}")
            text.textLine(f"Year: {year}, Quarter: Q{quarter}")
            text.textLine("")
            text.textLine("Executive Summary:")
            text.textLine(narrative)
            text.textLine("")
            text.textLine("This report is generated automatically using")
            text.textLine("MySQL + Python + Streamlit from PhonePe Pulse data.")

            c.drawText(text)
            c.showPage()
            c.save()

            with open(tmp.name, "rb") as f:
                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name=f"PhonePe_{report_category}_Q{quarter}_{year}.pdf",
                    mime="application/pdf"
                )
# ==================================
# DATABASE PAGE
# ==================================
elif page == "Database":
    st.title("🗄️ Database Design & Tables")

    st.markdown("""
This project uses a **MySQL relational database** designed for analytical workloads.
Each table serves a specific purpose in enabling multi-level insights.
""")

    tabs = st.tabs([
        "Aggregated Transaction",
        "Aggregated User",
        "Aggregated Insurance",
        "Map Transaction",
        "Map User",
        "Map Insurance",
        "Top Transaction",
        "Top User",
        "Top Insurance"
    ])

    # ------------------------------------------------
    with tabs[0]:
        st.subheader("📊 aggregated_transaction")
        st.markdown("""
**Purpose:** State-level transaction metrics by year, quarter, and transaction type.
""")
        show_sample_data("aggregated_transaction", conn)

    # ------------------------------------------------
    with tabs[1]:
        st.subheader("👥 aggregated_user")
        st.markdown("""
**Purpose:** Device-wise user distribution at state level.
""")
        show_sample_data("aggregated_user", conn)

    # ------------------------------------------------
    with tabs[2]:
        st.subheader("🛡️ aggregated_insurance")
        st.markdown("""
**Purpose:** State-level insurance transaction metrics.
""")
        show_sample_data("aggregated_insurance", conn)

    # ------------------------------------------------
    with tabs[3]:
        st.subheader("🗺️ map_transaction")
        st.markdown("""
**Purpose:** District-level transaction insights.
""")
        show_sample_data("map_transaction", conn)

    # ------------------------------------------------
    with tabs[4]:
        st.subheader("👤 map_user")
        st.markdown("""
**Purpose:** District-wise registered user counts.
""")
        show_sample_data("map_user", conn)

    # ------------------------------------------------
    with tabs[5]:
        st.subheader("🛡️ map_insurance")
        st.markdown("""
**Purpose:** District-level insurance adoption data.
""")
        show_sample_data("map_insurance", conn)

    # ------------------------------------------------
    with tabs[6]:
        st.subheader("🏆 top_transaction")
        st.markdown("""
**Purpose:** Top-performing regions based on transaction value.
""")
        show_sample_data("top_transaction", conn)

    # ------------------------------------------------
    with tabs[7]:
        st.subheader("👥 top_user")
        st.markdown("""
**Purpose:** Regions with highest registered users.
""")
        show_sample_data("top_user", conn)

    # ------------------------------------------------
    with tabs[8]:
        st.subheader("🛡️ top_insurance")
        st.markdown("""
**Purpose:** Regions leading in insurance transactions.
""")
        show_sample_data("top_insurance", conn)

    st.success("✅ Each table is validated with live sample data from the database.")

# ==================================
# ABOUT PAGE
# ==================================
elif page == "About":
    st.title("ℹ️ About PhonePe Pulse")

    st.markdown("""
**PhonePe Pulse** is an open data analytics initiative by PhonePe that provides
deep insights into how digital payments are transforming India.

This project is a **data-driven replica** of the PhonePe Pulse platform,
built using **Python, MySQL, SQL analytics, and Streamlit** to demonstrate
real-world data science and analytics workflows.
""")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📌 Aim", "🎯 Mission", "🔭 Vision", "🌍 Scope", "🛠️ Tools & Technologies"]
    )

    # ---------- AIM ----------
    with tab1:
        st.subheader("📌 Aim")
        st.markdown("""
The aim of this project is to analyze and visualize PhonePe transaction data
to understand **digital payment trends across India**.

Key goals include:
- Understanding transaction behavior across states and districts
- Identifying top-performing regions and categories
- Presenting insights through interactive dashboards
""")

    # ---------- MISSION ----------
    with tab2:
        st.subheader("🎯 Mission")
        st.markdown("""
The mission of the PhonePe Pulse platform is to:

- Promote **data transparency** in digital payments
- Enable businesses and analysts to make **data-backed decisions**
- Showcase the rapid growth of **cashless transactions** in India
""")

    # ---------- VISION ----------
    with tab3:
        st.subheader("🔭 Vision")
        st.markdown("""
The vision behind PhonePe Pulse is to become a **single source of truth**
for understanding India's digital payment ecosystem.

This project reflects that vision by:
- Providing clear, structured insights
- Making complex data easy to understand
- Encouraging data literacy and analytical thinking
""")

    # ---------- SCOPE ----------
    with tab4:
        st.subheader("🌍 Scope")
        st.markdown("""
The scope of this project includes:

- Analysis of transactions, users, and insurance data
- State-level and district-level insights
- Business case-driven SQL analysis
- Interactive visualizations using Streamlit
- Generation of professional analytical reports

This project can be extended further with:
- Real-time data pipelines
- Predictive analytics
- Fraud detection models
""")

    # ---------- TOOLS & TECHNOLOGIES ----------
    with tab5:
        st.subheader("🛠️ Tools & Technologies Used")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
**Programming & Libraries**
- Python  
- Pandas  
- NumPy  
""")

        with col2:
            st.markdown("""
**Database & Analytics**
- MySQL  
- SQL (Joins, Aggregations, Filters)  
- ETL Pipelines  
""")

        with col3:
            st.markdown("""
**Visualization & Tools**
- Streamlit  
- Plotly  
- Matplotlib  
- Git & GitHub  
""")

        st.markdown("""
**Why these tools?**

These technologies were chosen to build a **scalable, analytics-ready system**
that mirrors real-world data science workflows:
- Python for data processing  
- MySQL for structured storage and querying  
- Streamlit for interactive dashboards  
- Plotly for rich visualizations  
""")

# ==================================
# CREATOR PAGE
# ==================================
elif page == "Creator":

    # ---------- HEADER ----------
    st.markdown("""
    <div style="background:#2b014f;padding:30px;border-radius:16px;">
        <h1 style="color:#ffffff;text-align:center;">👩‍💻 Project Creator</h1>
        <p style="color:#cfc6ff;text-align:center;font-size:16px;">
            Data Science • Analytics • Visualization
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # ---------- PROFILE SECTION ----------
    col1, col2 = st.columns([1.2, 2.5])

    with col1:
        st.markdown("""
        <div style="background:#3a0168;padding:20px;border-radius:14px;">
            <h2 style="color:#ffffff;">GAYATHRI S</h2>
            <p style="color:#cfc6ff;font-size:15px;">
                Aspiring Data Scientist<br>
                📍 India
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#3a0168;padding:20px;border-radius:14px;">
            <h3 style="color:#ffffff;">🧠 About Me</h3>
            <p style="color:#e6ddff;font-size:15px;line-height:1.6;">
                I am an aspiring <b>Data Scientist</b> with a strong passion for transforming
                raw data into meaningful business insights using <b>Python, SQL, and analytics tools</b>.
                <br><br>
                This PhonePe Pulse–style project reflects my ability to work on
                <b>end-to-end data pipelines</b>, perform <b>SQL-driven analysis</b>,
                and build <b>interactive dashboards</b> for real-world business use cases.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ---------- SKILLS ----------
    st.markdown("""
    <div style="background:#2b014f;padding:25px;border-radius:16px;">
        <h3 style="color:#ffffff;">🛠️ Technical Skills</h3>
    </div>
    """, unsafe_allow_html=True)

    skill1, skill2, skill3 = st.columns(3)

    with skill1:
        st.markdown("""
        <div style="background:#3a0168;padding:20px;border-radius:14px;">
            <h4 style="color:#ffffff;">Programming</h4>
            <ul style="color:#e6ddff;">
                <li>Python</li>
                <li>SQL</li>
                <li>Pandas</li>
                <li>NumPy</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with skill2:
        st.markdown("""
        <div style="background:#3a0168;padding:20px;border-radius:14px;">
            <h4 style="color:#ffffff;">Data & Analytics</h4>
            <ul style="color:#e6ddff;">
                <li>Data Cleaning & ETL</li>
                <li>Exploratory Data Analysis</li>
                <li>SQL Analytics</li>
                <li>Business Case Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with skill3:
        st.markdown("""
        <div style="background:#3a0168;padding:20px;border-radius:14px;">
            <h4 style="color:#ffffff;">Tools & Platforms</h4>
            <ul style="color:#e6ddff;">
                <li>Streamlit</li>
                <li>Plotly</li>
                <li>MySQL</li>
                <li>Git & GitHub</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ---------- PROJECT SKILLS ----------
    st.markdown("""
    <div style="background:#2b014f;padding:25px;border-radius:16px;">
        <h3 style="color:#ffffff;">📌 Skills Demonstrated in This Project</h3>
        <ul style="color:#e6ddff;font-size:15px;line-height:1.7;">
            <li>End-to-end data ingestion from PhonePe Pulse GitHub dataset</li>
            <li>Relational database design using MySQL</li>
            <li>Optimized SQL queries for analytics</li>
            <li>India-level choropleth map visualizations</li>
            <li>Business case–driven data storytelling</li>
            <li>Interactive dashboards using Streamlit</li>
            <li>Professional report generation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    

    

   
    st.success("✨ Thank you for exploring this project!")
