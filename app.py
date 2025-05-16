import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MSTY Compounding Simulator", layout="wide")

st.title("📊 MSTY Compounding Simulator")

tabs = st.tabs([
    "📊 Compounding Simulator",
    "📈 Market Monitoring",
    "📐 Cost Basis Tools",
    "🛡️ Hedging Tools",
    "📤 Export Center"
])

# Tab 1: Compounding Simulator (Restored full feature set)
with tabs[0]:
    st.header("📊 Dividend Compounding Projection")

    total_shares = st.number_input("Total Share Count", min_value=0, value=10000)
    avg_cost = st.number_input("Weighted Average Cost Basis ($)", min_value=0.0, value=25.00)
    holding_months = st.slider("Holding Period (Months)", 1, 120, 24)
    avg_div = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0)

    fed_tax = st.slider("Federal Tax Rate (%)", 0, 50, 20)
    state_tax = st.slider("State Tax Rate (%)", 0, 20, 5)
    dependents = st.number_input("Number of Dependents", min_value=0, value=0)
    acct_type = st.selectbox("Account Type", ["Taxable", "Tax Deferred"])

    drip = st.checkbox("Reinvest Dividends?")
    if drip:
        reinvest_percent = st.slider("Percent of Dividends to Reinvest (%)", 0, 100, 100)
        withdrawal = 0
    else:
        reinvest_percent = 0
        withdrawal = st.number_input("Withdraw this Dollar Amount Monthly ($)", min_value=0, value=2000)

    reinvest_price = st.number_input("Average Reinvestment Share Price ($)", min_value=0.1, value=25.0)
    frequency = st.selectbox("View Results By", ["Monthly", "Yearly", "Total"])
    run = st.button("Run Simulation")

    if run:
        monthly_data = []
        shares = total_shares
        total_dividends = 0
        total_reinvested = 0
        total_taxes = 0

        for month in range(1, holding_months + 1):
            gross_div = shares * avg_div
            tax = 0 if acct_type == "Tax Deferred" else gross_div * (fed_tax + state_tax) / 100
            net_div = gross_div - tax
            if drip:
                reinvest_amount = net_div * (reinvest_percent / 100)
            else:
                reinvest_amount = max(0, net_div - withdrawal)
            new_shares = reinvest_amount / reinvest_price
            shares += new_shares
            total_dividends += net_div
            total_reinvested += reinvest_amount
            total_taxes += tax
            monthly_data.append({
                "Month": month,
                "Year": (month - 1) // 12 + 1,
                "Shares": shares,
                "Net Dividends": net_div,
                "Reinvested": reinvest_amount,
                "Taxes Paid": tax
            })

        df = pd.DataFrame(monthly_data)
        if frequency == "Monthly":
            df_view = df.copy()
            df_view["Period"] = df_view["Month"]
        elif frequency == "Yearly":
            df_view = df.groupby("Year").agg({
                "Shares": "last",
                "Net Dividends": "sum",
                "Reinvested": "sum",
                "Taxes Paid": "sum"
            }).reset_index().rename(columns={"Year": "Period"})
        else:
            df_view = pd.DataFrame([{
                "Period": "Total",
                "Shares": df["Shares"].iloc[-1],
                "Net Dividends": df["Net Dividends"].sum(),
                "Reinvested": df["Reinvested"].sum(),
                "Taxes Paid": df["Taxes Paid"].sum()
            }])

        st.success(f"📈 Final Share Count: {shares:,.2f}")
        st.success(f"💸 Total Dividends Collected: ${total_dividends:,.2f}")
        st.success(f"🔁 Total Reinvested: ${total_reinvested:,.2f}")
        st.success(f"💼 Total Taxes Paid: ${total_taxes:,.2f}")

        st.plotly_chart(px.bar(df_view, x="Period", y="Shares", title="Projected Share Growth"))
        st.subheader("📋 Projection Table")
        st.dataframe(df_view.style.format({
            "Shares": "{:,.2f}",
            "Net Dividends": "${:,.2f}",
            "Reinvested": "${:,.2f}",
            "Taxes Paid": "${:,.2f}"
        }))