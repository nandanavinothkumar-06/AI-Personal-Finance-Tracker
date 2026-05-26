import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import date

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(page_title="AI Personal Finance Tracker",layout="wide")
st.title("💰 AI Personal Finance Tracker")
st.markdown(
    "Track expenses, analyze spending habits, "
    "and gain AI-powered financial insights."
)

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect("finance_tracker.db")
cursor = conn.cursor()

# ---------------- CREATE TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    expense_date TEXT,
    description TEXT
)
""")
conn.commit()

# ---------------- FETCH DATA ---------------- #

cursor.execute("SELECT * FROM expenses")
rows = cursor.fetchall()
df = pd.DataFrame(rows,columns=["ID", "Amount", "Category", "Date", "Description"])

# ---------------- GLOBAL METRICS ---------------- #

if not df.empty:
    total_expense = df["Amount"].sum()
    total_transactions = len(df)
    highest_expense = df["Amount"].max()
    average_expense = df["Amount"].mean()

else:

    total_expense = 0
    total_transactions = 0
    highest_expense = 0
    average_expense = 0

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("💳 Finance Tracker")
menu = st.sidebar.selectbox("Navigation",["Dashboard", "Add Expense", "Analytics"])

# Monthly Budget in Sidebar

st.sidebar.subheader("💸 Monthly Budget")
budget = st.sidebar.number_input("Set Monthly Budget",min_value=0.0,value=10000.0)

# ---------------- ADD EXPENSE ---------------- #

if menu == "Add Expense":
    st.subheader("➕ Add Expense")
    amount = st.number_input("Enter Amount",min_value=0.0)
    category = st.selectbox("Select Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health"
        ]
    )

    expense_date = st.date_input("Select Date",value=date.today())
    description = st.text_input("Description")
    if st.button("Add Expense"):
        cursor.execute("""
        INSERT INTO expenses (
            amount,
            category,
            expense_date,
            description
        )
        VALUES (?, ?, ?, ?)
        """, (
            amount,
            category,
            str(expense_date),
            description
        ))
        conn.commit()
        st.success("✅ Expense Added Successfully!")

# ---------------- DASHBOARD ---------------- #

if menu == "Dashboard":
    st.subheader("📊 Financial Overview")
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses",f"₹ {total_expense:.2f}")
    col2.metric("Total Transactions",total_transactions)
    col3.metric("Highest Expense",f"₹ {highest_expense:.2f}")

    # Budget Alerts
    st.subheader("💸 Budget Status")
    if total_expense > budget:
        st.error("⚠️ Budget Limit Exceeded!")

    elif total_expense > (0.8 * budget):
        st.warning("⚠️ You have used more than 80% of your budget.")

    else:
        st.success("✅ Your spending is within budget.")

    # Expense History
    st.subheader("📋 Expense History")
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No expenses added yet.")

    # Delete Expense
    st.subheader("🗑️ Delete Expense")
    expense_id = st.number_input("Enter Expense ID to Delete",min_value=1,step=1)

    if st.button("Delete Expense"):
        cursor.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )
        conn.commit()

        st.success("✅ Expense Deleted Successfully!")
        st.rerun()

    # Download CSV
    st.subheader("📥 Download Expense Report")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV Report",data=csv,file_name="expense_report.csv",mime="text/csv")

# ---------------- ANALYTICS ---------------- #

if menu == "Analytics":
    if not df.empty:
        # Expense by Category
        st.subheader("📈 Expense by Category")
        category_expense = df.groupby("Category")["Amount"].sum()
        st.bar_chart(category_expense)

        # Pie Chart
        fig = px.pie(
            values=category_expense.values,
            names=category_expense.index,
            title="Category Distribution"
            )
        st.plotly_chart(fig,use_container_width=True)

        # Monthly Trend
        st.subheader("📅 Monthly Expense Trend")
        df["Date"] = pd.to_datetime(df["Date"])
        monthly_expense = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        monthly_expense.index = (monthly_expense.index.astype(str))
        st.line_chart(monthly_expense)

        # AI Insights
        st.subheader("🤖 AI Financial Insights")
        highest_category = (category_expense.idxmax())
        highest_amount = (category_expense.max())

        st.info(
            f"💡 Your highest spending category is "
            f"{highest_category} "
            f"with total spending of "
            f"₹{highest_amount:.2f}"
        )

        st.info(
            f"📊 Your average transaction amount is "
            f"₹{average_expense:.2f}"
        )

        # Budget AI Insight
        if total_expense > budget:
            st.error(
                "⚠️ Your expenses exceed your monthly budget. "
                "Consider reducing unnecessary spending."
            )

        elif total_expense > (0.8 * budget):
            st.warning(
                "⚠️ You are nearing your monthly budget limit."
            )

        else:
            st.success(
                "✅ Your spending habits are currently healthy."
            )

    else:
        st.warning(
            "No data available for analytics."
        )

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.caption(
    "Built with Streamlit, SQLite, and Python"
)

# ---------------- CLOSE DATABASE ---------------- #

conn.close()