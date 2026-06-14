
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, date

# ---------------- FILES ---------------- #

expense_file = "expenses.csv"
savings_file = "savings.csv"
borrowed_file = "borrowed.csv"
budget_file = "budget.txt"
carry_file = "carry_forward.txt"


# ---------------- CREATE FILES IF NOT EXIST ---------------- #

if not os.path.exists(expense_file):
    df = pd.DataFrame(
        columns=["Date", "Name", "Category", "Amount"]
    )
    df.to_csv(expense_file, index=False)


if not os.path.exists(savings_file):
    df = pd.DataFrame(
        columns=["Date", "SavedAmount"]
    )
    df.to_csv(savings_file, index=False)


if not os.path.exists(borrowed_file):
    df = pd.DataFrame(
        columns=[
            "Name",
            "Amount",
            "Reason",
            "BorrowDate",
            "DueDate",
            "Status",
            "ReturnDate"
        ]
    )

    df.to_csv(borrowed_file, index=False)


if not os.path.exists(budget_file):

    with open(budget_file, "w") as f:

        f.write("10000")

# ---------------- CARRY FORWARD ---------------- #

def get_carry_forward():
    if not os.path.exists(carry_file):
        return 0.0
    with open(carry_file, "r") as f:
        return float(f.read())


def set_carry_forward(amount):
    with open(carry_file, "w") as f:
        f.write(str(amount))

# ---------------- EXPENSE FUNCTIONS ---------------- #
def load_expenses():

    try:

        return pd.read_csv(expense_file)

    except:

        df = pd.DataFrame(
            columns=["Date", "Name", "Category", "Amount"]
        )

        df.to_csv(expense_file, index=False)

        return df


def save_expense(date_, name, category, amount):

    df = load_expenses()

    new_row = pd.DataFrame(

        [[date_, name, category, amount]],

        columns=["Date", "Name", "Category", "Amount"]

    )

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(expense_file, index=False)

# ---------------- SAVINGS FUNCTIONS ---------------- #
def load_savings():

    try:

        return pd.read_csv(savings_file)

    except:

        df = pd.DataFrame(

            columns=["Date", "SavedAmount"]

        )

        df.to_csv(savings_file, index=False)

        return df

def save_saving(amount):

    df = load_savings()

    new_row = pd.DataFrame(

        [[datetime.now().strftime("%Y-%m-%d"), amount]],

        columns=["Date", "SavedAmount"]

    )

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(savings_file, index=False)

# ---------------- BORROWED MONEY ---------------- #
def load_borrowed():

    try:

        return pd.read_csv(borrowed_file)

    except:

        df = pd.DataFrame(

            columns=[

                "Name",
                "Amount",
                "Reason",
                "BorrowDate",
                "DueDate",
                "Status",
                "ReturnDate"
            ]
        )

        df.to_csv(borrowed_file, index=False)

        return df



def save_borrowed(

        name,
        amount,
        reason,
        due_date

):

    df = load_borrowed()

    borrow_date = datetime.now().strftime("%Y-%m-%d")

    new_row = pd.DataFrame(

        [[

            name,
            amount,
            reason,
            borrow_date,
            due_date,

            "Unpaid",

            "-"

        ]],

        columns=[

            "Name",
            "Amount",
            "Reason",
            "BorrowDate",
            "DueDate",
            "Status",
            "ReturnDate"

        ]

    )

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(borrowed_file, index=False)

def mark_as_paid(index):

    df = load_borrowed()
    df.at[index, "Status"] = "Paid"
    df.at[index, "ReturnDate"] = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(borrowed_file, index=False)

# ---------------- BUDGET ---------------- #

def get_budget():
    with open(budget_file, "r") as f:
        return float(f.read())

def set_budget(amount):
    with open(budget_file, "w") as f:
        f.write(str(amount))

# ---------------- ANOMALY DETECTION ---------------- #
def detect_anomalies(df, budget):

    anomalies = []

    if df.empty:
        return anomalies

    for _, row in df.iterrows():

        amount = row["Amount"]

        if amount > budget * 0.2:

            anomalies.append({
                "Date": row["Date"],
                "Name": row["Name"],
                "Category": row["Category"],
                "Amount": amount,
                "Threshold": budget * 0.2
            })

    return anomalies
# ---------------- STREAMLIT TITLE ---------------- #

st.set_page_config(

    page_title="Xpenzoo",
    page_icon="💰",
    layout="wide"

)
st.title("💰 Xpenzoo")
st.markdown(
    "Track Expenses | Savings | Borrowed Money | Budget"
)

# ---------------- MENU ---------------- #
menu = [

    "Add Expense",
    "Summary",
    "Piggy Bank",
    "Borrowed Money",
    "Change Budget"
]

choice = st.sidebar.radio(
    "Select Menu",
    menu
)

# ---------------- ADD EXPENSE ---------------- #
if choice == "Add Expense":
    st.header("➕ Add New Expense")
    expense_date = st.date_input(
        "Expense Date",
        value=date.today()

    )

    name = st.text_input(
        "Expense Name"
    )

    category = st.selectbox(
        "Category",
        [

            "🍔 Food",
            "🏠 Home",
            "📚 Study",
            "🎉 Fun",
            "👕 Clothes",
            "🚕 Travel",
            "💊 Health",
            "📱 Others"
        ]
    )
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=100.0
    )
    if st.button("Save Expense"):
        if name and amount > 0:
            save_expense(
                str(expense_date),
                name,
                category,
                amount
            )
            st.success(
                f"✅ Saved : {name} - ₹{amount}"
            )
        else:
            st.error(
                "Please enter valid details"
            )

# ---------------- SUMMARY ---------------- #
elif choice == "Summary":

    st.header("📊 Expense Summary")

    expense_df = load_expenses()

    savings_df = load_savings()

    borrowed_df = load_borrowed()

    budget = get_budget()

    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")

    current_month = datetime.now().strftime("%Y-%m")

    monthly_expenses = expense_df[
    expense_df["Date"].dt.strftime("%Y-%m") == current_month
]

    large_transactions = expense_df[
    expense_df["Amount"] > budget * 0.2
    ]

    if not large_transactions.empty:

           st.subheader("🚨 Large Transaction Alert")

           for _, row in large_transactions.iterrows():

            st.warning(
                f"""
                 🚨 Large Transaction Alert

                   Expense : {row['Name']}

                  Amount : ₹{row['Amount']}

                This expense exceeds 20% of your monthly budget.
                 """    
        )

    else:

        st.success(

        "✅ No unusual spending detected"

    )

   

    # ---------------- EXPENSE TABLE ---------------- #
    st.subheader("All Expenses")
    if expense_df.empty:
        st.info(
            "No expenses added yet"
        )
    else:
        st.dataframe(
            expense_df,
            use_container_width=True
        )



    # ---------------- CALCULATIONS ---------------- #

    budget = get_budget()



    total_expense = 0

    total_savings = 0

    unpaid_borrowed = 0



    if not expense_df.empty:

        total_expense = monthly_expenses["Amount"].sum() if not monthly_expenses.empty else 0



    if not savings_df.empty:

        total_savings = savings_df["SavedAmount"].sum()



    if not borrowed_df.empty:


        unpaid_borrowed = borrowed_df[

            borrowed_df["Status"] == "Unpaid"

        ]["Amount"].sum()
         
        carry_forward = get_carry_forward()

        effective_budget = budget + carry_forward

        remaining_balance = (
        effective_budget
        - total_expense
        - total_savings
        - unpaid_borrowed
)


    # ---------------- FINANCIAL OVERVIEW ---------------- #


    st.subheader("💰 Financial Overview")


    col1, col2 = st.columns(2)


    with col1:
        st.metric(
           "Monthly Budget",
            f"₹{effective_budget:.2f}"
)


       


        st.metric(

            "Expenses",

            f"₹{total_expense:.2f}"

        )



    with col2:


        st.metric(

            "Savings",

            f"₹{total_savings:.2f}"

        )


        st.metric(

            "Borrowed Out",

            f"₹{unpaid_borrowed:.2f}"

        )



    st.metric(

        "Available Balance",

        f"₹{remaining_balance:.2f}"

    )



    # ---------------- BUDGET STATUS ---------------- #


    used_money = (
        total_expense
        + total_savings
        + unpaid_borrowed
)

    limit = effective_budget



    if used_money < limit * 0.8:


        st.success(

            "✅ You are well within budget!"

        )



    elif used_money <= limit:


        st.warning(

            "⚠️ You are close to your budget!"

        )



    else:


        st.error(

            "🚨 Budget Exceeded!"

        )



    # ---------------- PIE CHART ---------------- #


    if not expense_df.empty:


        st.subheader(

            "📈 Expenses By Category"

        )



        category_summary = monthly_expenses.groupby("Category")["Amount"].sum()


        fig, ax = plt.subplots(


            figsize=(6, 6)

        )



        ax.pie(

            category_summary,

            labels=category_summary.index,

            autopct="%1.1f%%"

        )



        ax.set_title(

            "Expense Distribution"

        )



        st.pyplot(fig)



    # ---------------- ANOMALIES ---------------- #


    if not expense_df.empty:
        anomalies = detect_anomalies(expense_df, budget)
        st.subheader(

            "🚨 Anomaly Detection"

        )

        if anomalies:
            for anomaly in anomalies:

                st.error(

                    f"""

            ⚠️ {anomaly['Name']}

            Category : {anomaly['Category']}

             Amount : ₹{anomaly['Amount']}

            Threshold : ₹{anomaly['Threshold']}

             Date : {anomaly['Date']}

"""

                )
        else:
            st.success(

                "✅ No unusual spending detected"
            )
            # ---------------- PIGGY BANK ---------------- #

elif choice == "Piggy Bank":

    st.header("🐷 Piggy Bank")

    savings_df = load_savings()

    total_savings = 0

    if not savings_df.empty:

        total_savings = savings_df["SavedAmount"].sum()


    st.metric(

        "Current Savings",

        f"₹{total_savings:.2f}"

    )


    st.divider()


    st.subheader("➕ Save Money")


    save_amt = st.number_input(

        "Amount to Save",

        min_value=0.0,

        step=100.0,

        key="save"

    )


    if st.button("Save to Piggy Bank"):


        if save_amt > 0:


            save_saving(save_amt)


            st.success(

                f"₹{save_amt} added to savings"

            )


            st.rerun()



    st.divider()


    st.subheader("➖ Withdraw Savings")


    withdraw_amt = st.number_input(

        "Withdraw Amount",

        min_value=0.0,

        step=100.0,

        key="withdraw"

    )



    if st.button("Withdraw"):



        if withdraw_amt > 0:



            if withdraw_amt <= total_savings:



                save_saving(

                    -withdraw_amt

                )


                st.success(

                    f"₹{withdraw_amt} withdrawn"

                )


                st.rerun()



            else:



                st.error(

                    "Not enough savings"

                )



    st.divider()



    st.subheader("📜 Savings History")



    st.dataframe(

        savings_df,

        use_container_width=True

    )
# ---------------- BORROWED MONEY ---------------- #
elif choice == "Borrowed Money":
    st.header("💸 Borrowed Money Tracker")
    name = st.text_input(
        "Person Name"
    )
    amount = st.number_input(

        "Amount",

        min_value=0.0,

        step=100.0

    )
    reason = st.text_input(

        "Reason"

    )
    due_date = st.date_input(

        "Due Date",

        min_value=date.today()

    )
    if st.button("Save Borrow Record"):
        if name and amount > 0:
            save_borrowed(

                name,

                amount,

                reason,

                str(due_date)

            )
            st.success(

                f"{name} owes ₹{amount}"

            )
            st.rerun()
        else:
            st.error(

                "Enter valid details"

            )
    st.divider()
    borrowed_df = load_borrowed()
    st.subheader(

        "Borrowed Records"

    )
    if borrowed_df.empty:
        st.info(
            "No borrowed records"
        )
    else:
        st.dataframe(
            borrowed_df,
            use_container_width=True
        )
        st.divider()
        today = date.today()
        for idx, row in borrowed_df.iterrows():
            due = datetime.strptime(

                row["DueDate"],

                "%Y-%m-%d"

            ).date()
            days_left = (

                due - today

            ).days
            st.write("---")
            st.write(

                f"👤 **{row['Name']}**"

            )
            st.write(

                f"💰 Amount : ₹{row['Amount']}"

            )
            st.write(

                f"📝 Reason : {row['Reason']}"

            )
            st.write(

                f"📅 Due : {row['DueDate']}"

            )
            st.write(

                f"📌 Status : {row['Status']}"

            )
            if row["Status"] == "Paid":
                st.success(

                    f"Returned on {row['ReturnDate']}"

                )
            else:
                if days_left < 0:
                    st.error(

                        f"Overdue by {-days_left} days"

                    )
                elif days_left <= 2:
                    st.warning(
                        f"Due in {days_left} day(s)"
                    )
                else:
                    st.info(

                        f"{days_left} days remaining"

                    )
                if st.button(

                        f"Mark Paid - {row['Name']}",

                        key=f"paid_{idx}"

                ):
                    mark_as_paid(idx)
                    st.success(

                        f"{row['Name']} marked Paid"

                    )
                    st.rerun()
                    # ---------------- CHANGE BUDGET ---------------- #

elif choice == "Change Budget":
    st.header("📝 Change Monthly Budget")

    current_budget = get_budget()

    st.metric(
        "Current Budget",
        f"₹{current_budget:.2f}"
    )

    new_budget = st.number_input(
        "Enter New Budget",
        min_value=0.0,
        step=500.0
    )

    if st.button("Update Budget"):

        if new_budget > 0:

            # ---------------- LOAD DATA ---------------- #
            expense_df = load_expenses()
            savings_df = load_savings()
            borrowed_df = load_borrowed()

            # ---------------- CALCULATIONS ---------------- #
            total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0
            total_savings = savings_df["SavedAmount"].sum() if not savings_df.empty else 0

            unpaid_borrowed = 0
            if not borrowed_df.empty:
                unpaid_borrowed = borrowed_df[
                    borrowed_df["Status"] == "Unpaid"
                ]["Amount"].sum()

            old_budget = get_budget()

            # ---------------- CARRY FORWARD ---------------- #
            carry_forward = (
                old_budget
                - total_expense
                - total_savings
                - unpaid_borrowed
            )

            # save carry forward
            set_carry_forward(carry_forward)

            # ---------------- UPDATE BUDGET ---------------- #
            set_budget(new_budget)

            st.success(
                f"""
✅ Budget Updated Successfully!

New Budget: ₹{new_budget:.2f}
Carry Forward: ₹{carry_forward:.2f}
Effective Budget: ₹{new_budget + carry_forward:.2f}
"""
            )

            st.rerun()

        else:
            st.error("Please enter a valid budget")

    st.divider()

    st.subheader("📊 Monthly Expense Analysis")

    expense_df = load_expenses()

    if expense_df.empty:
        st.info("No expenses available")

    else:
        expense_df["Date"] = pd.to_datetime(expense_df["Date"])

        expense_df["Month"] = (
            expense_df["Date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            expense_df
            .groupby("Month")["Amount"]
            .sum()
        )

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.bar(
            monthly.index,
            monthly.values
        )

        ax.set_xlabel("Month")
        ax.set_ylabel("Expense Amount")
        ax.set_title("Monthly Expenses")

        plt.xticks(rotation=30)

        st.pyplot(fig)

    st.divider()

    st.subheader("⬇ Download Data")


    # Expense CSV
    expense_csv = load_expenses().to_csv(
        index=False

    )
    st.download_button(
        label="Download Expenses CSV",
        data=expense_csv,
        file_name="expenses.csv",
        mime="text/csv"

    )

    # Savings CSv
    savings_csv = load_savings().to_csv(
        index=False
    )
    st.download_button(
        label="Download Savings CSV",
        data=savings_csv,
        file_name="savings.csv",
        mime="text/csv"

    )

    # Borrowed CSV

    borrowed_csv = load_borrowed().to_csv(
        index=False
    )
    st.download_button(
        label="Download Borrowed CSV",
        data=borrowed_csv,
        file_name="borrowed.csv",
        mime="text/csv"
    )


           

