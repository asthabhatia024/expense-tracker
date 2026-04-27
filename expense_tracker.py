
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, date

# -------------------- Files --------------------
expense_file = "expenses.csv"
savings_file = "savings.csv"
borrowed_file = "borrowed.csv"
budget_file = "budget.txt"   # ✅ New file for budget

# Ensure files exist
if not os.path.exists(expense_file):
    df = pd.DataFrame(columns=["Date", "Name", "Category", "Amount"])
    df.to_csv(expense_file, index=False)

if not os.path.exists(savings_file):
    df = pd.DataFrame(columns=["Date", "SavedAmount"])
    df.to_csv(savings_file, index=False)

if not os.path.exists(borrowed_file):
    df = pd.DataFrame(columns=["Name", "Amount", "Reason", "DueDate", "Status"])
    df.to_csv(borrowed_file, index=False)

if not os.path.exists(budget_file):
    with open(budget_file, "w") as f:
        f.write("10000")  # Default budget = ₹10,000

# -------------------- Expense Functions --------------------
def load_expenses():
    try:
        df = pd.read_csv(expense_file)
        return df
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Date", "Name", "Category", "Amount"])
        df.to_csv(expense_file, index=False)
        return df


def save_expense(name, category, amount):
    df = load_expenses()
    new_exp = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, category, amount]],
                           columns=["Date", "Name", "Category", "Amount"])
    df = pd.concat([df, new_exp], ignore_index=True)
    df.to_csv(expense_file, index=False)

# -------------------- Savings Functions --------------------
def load_savings():
    try:
        return pd.read_csv(savings_file)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Date", "SavedAmount"])
        df.to_csv(savings_file, index=False)
        return df
def save_saving(amount):
    df = load_savings()
    new_save = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), amount]],
                            columns=["Date", "SavedAmount"])
    df = pd.concat([df, new_save], ignore_index=True)
    df.to_csv(savings_file, index=False)

# -------------------- Borrowed Money Functions --------------------
def load_borrowed():
    try:
        return pd.read_csv(borrowed_file)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Name", "Amount", "Reason", "DueDate", "Status"])
        df.to_csv(borrowed_file, index=False)
        return df

def save_borrowed(name, amount, reason, due_date):
    df = load_borrowed()
    new_entry = pd.DataFrame([[name, amount, reason, due_date, "Unpaid"]],
                             columns=["Name", "Amount", "Reason", "DueDate", "Status"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(borrowed_file, index=False)

def mark_as_paid(index):
    df = load_borrowed()
    df.at[index, "Status"] = "Paid"
    df.to_csv(borrowed_file, index=False)

# -------------------- Budget Functions --------------------
def get_budget():
    with open(budget_file, "r") as f:
        return float(f.read().strip())

def set_budget(new_budget):
    with open(budget_file, "w") as f:
        f.write(str(new_budget))

# -------------------- Anomaly Detection --------------------
def detect_anomalies(df):
    anomalies = []
    if df.empty:
        return anomalies

    cat_groups = df.groupby("Category")["Amount"]
    for category, values in cat_groups:
        mean = values.mean()
        std = values.std() if values.std() > 0 else 1
        threshold = mean + 2 * std

        unusual = df[(df["Category"] == category) & (df["Amount"] > threshold)]
        for _, row in unusual.iterrows():
            anomalies.append({
                "Date": row["Date"],
                "Name": row["Name"],
                "Category": category,
                "Amount": row["Amount"],
                "Threshold": round(threshold, 2)
            })
    return anomalies

# -------------------- Streamlit App --------------------
st.title("💰 Xpenzoo")

menu = ["Add Expense", "Summary", "Piggy Bank", "Borrowed Money", "Change Budget"]
choice = st.sidebar.radio("Menu", menu)

# ---------------- Add Expense ----------------
if choice == "Add Expense":
    st.header("➕ Add a new expense")
    name = st.text_input("Expense name")
    category = st.selectbox("Category", ["🍔 Food", "🏠 Home", "📚 Study", "🎊 Fun", "👗 Clothes"])
    amount = st.number_input("Amount", min_value=0.0, step=100.0)

    if st.button("Save Expense"):
        if name and amount > 0:
            save_expense(name, category, amount)
            st.success(f"Saved: {name} - {category} - ₹{amount}")
        else:
            st.error("Please enter valid details!")

# ---------------- Expense Summary ----------------
elif choice == "Summary":
    st.header("📊 Expense Summary")
    df = load_expenses()

    if df.empty:
        st.info("No expenses recorded yet!")
    else:
        st.write("### All Expenses")
        st.dataframe(df)

        # Total
        total = df["Amount"].sum()
        st.subheader(f"Total Spent: ₹{total}")

        # Budget check
        budget = get_budget()
        st.subheader(f"Current Budget: ₹{budget}")

        if total < budget * 0.8:
            st.success("✅ You are well within budget!")
        elif total <= budget:
            st.warning("⚠️ You are close to your budget limit!")
        else:
            st.error("🚨 Budget exceeded! You have overspent.")

        # Pie chart
        cat_summary = df.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots()
        ax.pie(cat_summary, labels=cat_summary.index, autopct="%1.1f%%")
        ax.set_title("Expenses by Category")
        st.pyplot(fig)

        # Detect anomalies
        anomalies = detect_anomalies(df)
        if anomalies:
            st.subheader("🚨 Anomaly Alerts")
            for anomaly in anomalies:
                st.error(
                    f"⚠️ {anomaly['Name']} ({anomaly['Category']}) spent ₹{anomaly['Amount']} "
                    f"which is higher than usual (Threshold: ₹{anomaly['Threshold']})"
                )
        else:
            st.success("✅ No unusual spending detected")

# ---------------- Piggy Bank ----------------
elif choice == "Piggy Bank":
    st.header("🐷 Piggy Bank Savings")
    savings = load_savings()
    total_savings = savings["SavedAmount"].sum()
    st.subheader(f"Total Savings: ₹{total_savings}")

    # Add to savings
    save_amt = st.number_input("Add to Savings", min_value=0.0, step=100.0, key="save_amt")
    if st.button("Save to Piggy Bank"):
        if save_amt > 0:
            save_saving(save_amt)
            st.success(f"₹{save_amt} added to Piggy Bank!")
    
    # Withdraw from savings
    withdraw_amt = st.number_input("Withdraw from Savings", min_value=0.0, step=100.0, key="withdraw_amt")
    if st.button("Withdraw"):
        if withdraw_amt > 0:
            if withdraw_amt <= total_savings:
                save_saving(-withdraw_amt)  # store negative amount for withdrawal
                st.success(f"₹{withdraw_amt} withdrawn for emergency use!")
            else:
                st.error("⚠️ Not enough savings to withdraw this amount!")

    st.write("### Savings History")
    st.dataframe(savings)

# ---------------- Borrowed Money ----------------
elif choice == "Borrowed Money":
    st.header("💸 Borrowed Money Tracker")

    # Input form
    name = st.text_input("Person's Name")
    amount = st.number_input("Amount Borrowed", min_value=0.0, step=100.0)
    reason = st.text_input("Reason")
    due_date = st.date_input("Due Date", min_value=date.today())

    if st.button("Save Borrowed Money"):
        if name and amount > 0:
            save_borrowed(name, amount, reason, str(due_date))
            st.success(f"Saved borrowed record: {name} owes ₹{amount} (Due: {due_date})")
        else:
            st.error("Please enter valid details!")

    # Show borrowed data
    df = load_borrowed()
    if not df.empty:
        st.write("### Borrowed Money Records")
        st.dataframe(df)

        today = date.today()
        for idx, row in df.iterrows():
            due = datetime.strptime(row["DueDate"], "%Y-%m-%d").date()
            days_left = (due - today).days

            if row["Status"] == "Paid":
                st.success(f"✅ {row['Name']} cleared ₹{row['Amount']} ({row['Reason']})")
            else:
                if days_left < 0:
                    st.error(f"🚨 {row['Name']} owes ₹{row['Amount']} for {row['Reason']} (Overdue by {-days_left} days!)")
                elif days_left <= 2:
                    st.warning(f"⚠️ Reminder: {row['Name']} owes ₹{row['Amount']} for {row['Reason']} (Due in {days_left} days)")
                else:
                    st.info(f"📌 {row['Name']} owes ₹{row['Amount']} for {row['Reason']} (Due in {days_left} days)")

                if st.button(f"Mark as Paid - {row['Name']}", key=f"pay_{idx}"):
                    mark_as_paid(idx)
                    st.success(f"Marked {row['Name']}'s debt as Paid ✅")

# ---------------- Change Budget ----------------
elif choice == "Change Budget":
    st.header("📝 Change Monthly Budget")
    current_budget = get_budget()
    st.subheader(f"Current Budget: ₹{current_budget}")

    new_budget = st.number_input("Enter New Budget", min_value=0.0, step=500.0)

    if st.button("Update Budget"):
        if new_budget > 0:
            set_budget(new_budget)
            st.success(f"✅ Budget updated to ₹{new_budget}")
        else:
            st.error("Please enter a valid budget amount.")


           

