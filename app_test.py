import os
import streamlit as st
import pandas as pd
import joblib
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Company branding
st.sidebar.title("AfriCredit AI")
st.sidebar.title("Note: This is a prototype for demonstration purposes.Model is ony 83.3% accurate.Model behaviour depends on quality of data")
st.sidebar.write("Helping customers without traditional bank accounts access fair credit.")

# Display feature ranges and descriptions in the sidebar
st.sidebar.subheader("Feature Ranges and Descriptions")
st.sidebar.markdown("""
### Feature Descriptions
**All amounts are in USD.**  

- **Income**: 300.00 to 1,200.00  
  *Monthly income of the customer.*
- **Account Age**: 10 to 72 months  
  *Duration of the customer's account with the platform.*
- **Employment Status**: Employed or Unemployed  
  *Current employment status of the customer.*
- **Loan Amount**: 100.00 to 1,000.00  
  *Amount of loan requested by the customer.*
- **Average Mobile Money Balance**: 150.00 to 2,070.00  
  *Average balance in the customer's mobile money account.*
- **Monthly Data Usage**: 2.30 GB to 5.50 GB  
  *Average monthly data usage by the customer.*
- **Average Monthly Calls**: 170 to 290  
  *Average number of calls made by the customer per month.*
- **Total Mobile Money Amount**: 50.00 to 500.00  
  *Total amount transacted through mobile money.*
""")
st.sidebar.title("Note:Still Under Development.CI/CD.")

# Database connection
# engine = create_engine("mysql+mysqlconnector://root:Danieledem_7@localhost/credit")
# connection = engine.connect()



# Access environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")  # Redshift cluster endpoint
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")  # Default Redshift port


# Check if all credentials are set
if None in [DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT]:
    st.error("Database environment variables are not set correctly.")
    st.stop()

# Create the Redshift connection
try:
    connection_url = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    
    engine = create_engine(connection_url, connect_args={"options": "-c search_path=public"})


    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        st.write("✅ Database connection successful!")

except Exception as e:
    st.write(f"❌ Connection failed: {e}")
    engine = None  # Prevent further errors if the connection fails

# Load data only if connection is successful
if engine:
    try:
        with engine.connect() as conn:
            customers_df = pd.read_sql_query("SELECT * FROM customers", con=conn.connection)
            creditscorehistory_df = pd.read_sql_query("SELECT * FROM creditscorehistory", con=conn.connection)
            loanapplications_df = pd.read_sql_query("SELECT * FROM loanapplications", con=conn.connection)
            mobileusage_df = pd.read_sql_query("SELECT * FROM mobileusage", con=conn.connection)
            transactions_df = pd.read_sql_query("SELECT * FROM transactions", con=conn.connection)
            mobilemoney_df = pd.read_sql_query("SELECT * FROM mobilemoneytransactions", con=conn.connection)
        
        st.write("✅ Data loaded successfully!")

    except Exception as e:
        st.write(f"❌ Data loading failed: {e}")

# Feature engineering
mobilemoney_features = mobilemoney_df.groupby('customerid').agg({'amount': ['sum', 'mean', 'count'], 'balance': 'mean'}).reset_index()
mobilemoney_features.columns = ['customerid', 'totalmobilemoneyamount', 'averagemobilemoneyamount', 'mobilemoneytransactioncount', 'averagemobilemoneybalance']

# Merge data
approval_rates = loanapplications_df.merge(customers_df, on='customerid')
approval_rates = approval_rates.merge(mobilemoney_features, on='customerid')
approval_rates = approval_rates.merge(mobileusage_df, on='customerid')

#print(approval_rates.columns)

# One-hot encoding
#approval_rates = pd.get_dummies(approval_rates, columns=['EmploymentStatus'], drop_first=True)

# Load the trained model
model = joblib.load('83.3%_credit_scoring_model.pkl')

# Function to predict credit score, risk level, and approval decision
def predict_credit_score(customer_features):
    customer_df = pd.DataFrame([customer_features], columns=model.feature_names_in_)
    approval_probability = model.predict_proba(customer_df)[:, 1][0]
    credit_score = (approval_probability * 550) + 300
    if credit_score < 580:
        risk_level = "High Risk"
    elif 580 <= credit_score < 670:
        risk_level = "Medium Risk"
    elif 670 <= credit_score < 740:
        risk_level = "Low Risk"
    else:
        risk_level = "Very Low Risk"
    if risk_level in ["Low Risk", "Very Low Risk"]:
        approval_decision = "Approved"
    elif risk_level == "Medium Risk":
        approval_decision = "Approved with Conditions"
    else:
        approval_decision = "Rejected : Will Default"
    return credit_score, risk_level, approval_decision, customer_df



def create_progress_bar(credit_score):
    # Normalize the credit score to a value between 0 and 1
    normalized_score = (credit_score - 300) / (850 - 300)

    # Display the progress bar
    st.progress(normalized_score)
    st.write(f"Credit Score: {credit_score:.2f} ({normalized_score * 100:.1f}%)")





# Streamlit app
# Add the table to your app
def main():
    st.title("AfriCredit AI - Helping Unbanked Customers Access Fair Credit")
    st.write("This web app uses a Machine Learning model with 83.3% accuracy to predict the credit score, risk level, and approval decision for a customer based on their features")

    # Add a case study or hypothetical example
    st.subheader("Case Study: Empowering Unbanked Small Business Owners")
    st.markdown("""
    **Scenario:**   
    A small business owner has no traditional credit history but has been actively using mobile money services / other fintech service for their daily transactions.  

    How AfriCredit AI Helps:  
    By leveraging non-conventional features such as mobile money transactions, mobile account activity, and etc to determine financial behaviour, AfriCredit AI assesses creditworthiness and provides access to fair credit.  
    """)
    st.divider()

    # Define credit score ranges and corresponding decisions
    credit_score_table = pd.DataFrame({
        "Credit Score Range": ["300 - 579", "580 - 669", "670 - 739", "740 - 850"],
        "Risk Level": ["High Risk", "Medium Risk", "Low Risk", "Very Low Risk"],
        "Decision": ["❌ Rejected : Will Default", "⚠️ Approved with Conditions", "✅ Approved", "✅ Approved"]
    })

    # Define colors for each risk level
    risk_colors = {
        "High Risk": "#FF4B4B",  # Red
        "Medium Risk": "#FFA07A",  # Light Orange
        "Low Risk": "#FFD700",  # Gold
        "Very Low Risk": "#90EE90"  # Light Green
    }

    # Function to apply background color to the table
    def color_row(row):
        color = risk_colors[row["Risk Level"]]
        return [f"background-color: {color}" for _ in row]

    # Apply styling to the table
    styled_table = credit_score_table.style.apply(color_row, axis=1)

    # Display the styled table
    st.subheader("Credit Score Ranges and Decisions")
    st.write("The table below shows the credit score ranges, risk levels, and corresponding decisions:")
    st.dataframe(styled_table, use_container_width=True)
    st.divider()

    # Fetch unique countries from the approval_rates DataFrame
    countries = approval_rates["Country"].unique()

    # Calculate credit scores and risk levels for each country
    # Calculate credit scores and risk levels for each country
    country_data = []
    for country in countries:
        # Filter customers by country
        country_customers = approval_rates[approval_rates["Country"] == country]
        
        # Calculate average credit score and risk level for the country
        total_credit_score = 0
        total_customers = len(country_customers)
        for _, customer in country_customers.iterrows():
            # Predict credit score for each customer
            customer_features = {
                'Income': customer['Income'],
                'AccountAge': customer['AccountAge'],
                'EmploymentStatus_Employed': 1 if customer['EmploymentStatus'] == 'Employed' else 0,
                'EmploymentStatus_Unemployed': 1 if customer['EmploymentStatus'] == 'Unemployed' else 0,                
                'Loan Amount': customer['LoanAmount'],  # Accessible from approval_rates
                'AverageMobileMoneyBalance': customer['AverageMobileMoneyBalance'],
                'MonthlyDataUsage': customer['MonthlyDataUsage'],
                'AverageMonthlyCalls': customer['AverageMonthlyCalls'],
                'TotalMobileMoneyAmount': customer['TotalMobileMoneyAmount']
            }
            credit_score, risk_level, _, _ = predict_credit_score(customer_features)
            total_credit_score += credit_score
        
        # Calculate average credit score for the country
        avg_credit_score = total_credit_score / total_customers if total_customers > 0 else 0
        
        # Determine risk level for the country
        if avg_credit_score < 580:
            risk_level = "High Risk"
        elif 580 <= avg_credit_score < 670:
            risk_level = "Medium Risk"
        elif 670 <= avg_credit_score < 740:
            risk_level = "Low Risk"
        else:
            risk_level = "Very Low Risk"
        
        # Append data for the country
        country_data.append({
            "Country": country,
            "Average Credit Score": avg_credit_score,
            "Risk Level": risk_level
        })

    # Create a DataFrame for the country data
    country_df = pd.DataFrame(country_data)

    # Define colors for each risk level
    risk_colors = {
        "High Risk": "#FF4B4B",  # Red
        "Medium Risk": "#FFA07A",  # Light Orange
        "Low Risk": "#FFD700",  # Gold
        "Very Low Risk": "#90EE90"  # Light Green
    }

    # Convert countries and credit scores to lists
    labels = country_df["Country"]
    values = country_df["Average Credit Score"]
    colors = [risk_colors[risk] for risk in country_df["Risk Level"]]

    # Create the circular barplot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Set the number of bars (one per country)
    num_bars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_bars, endpoint=False).tolist()

    # Draw bars
    ax.bar(angles, values, color=colors, alpha=0.7, width=0.4)

    # Add labels
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=8, fontweight="bold")

    # Add a title
    ax.set_title("Average Credit Scores & Risk Levels ", fontsize=10, pad=20)

    # Customize the plot
    ax.tick_params(axis='x', colors='black', labelsize=10)
    ax.tick_params(axis='y', colors='gray', labelsize=8)
    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)


    # Create a legend for the risk levels
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=risk_colors["High Risk"], label="High Risk"),
        Patch(facecolor=risk_colors["Medium Risk"], label="Medium Risk"),
        Patch(facecolor=risk_colors["Low Risk"], label="Low Risk"),
        Patch(facecolor=risk_colors["Very Low Risk"], label="Very Low Risk")
    ]

    # Add the legend to the plot
    ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.1, 1.1), title="Risk Levels", prop={'size': 5})

    # Display the plot in Streamlit
    st.pyplot(fig)
    st.divider()

    # Input fields for customer features
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Income", min_value=300.0, max_value=12000.0, value=500.0, help="Monthly income of the customer.")
        account_age = st.number_input("Account Age (in months)", min_value=10.0, max_value=720.0, value=24.0, help="Duration of the customer's account with the platform.")
        employment_status = st.selectbox("Employment Status", ["Employed", "Unemployed"], help="Current employment status of the customer.")
        loan_amount = st.number_input("Loan Amount", min_value=100.0, max_value=10000.0, value=500.0, help="Amount of loan requested by the customer.")
    with col2:
        avg_mobile_balance = st.number_input("Average Mobile Money Balance", min_value=150.0, max_value=20700.0, value=500.0, help="Average balance in the customer's mobile money account.")
        monthly_data_usage = st.number_input("Monthly Data Usage (in GB)", min_value=2.3, max_value=50.5, value=3.5, help="Average monthly data usage by the customer.")
        avg_monthly_calls = st.number_input("Average Monthly Calls", min_value=170.0, max_value=2900.0, value=200.0, help="Average number of calls made by the customer per month.")
        total_mobile_amount = st.number_input("Total Mobile Money Amount", min_value=50.0, max_value=5000.0, value=200.0, help="Total amount transacted through mobile money.")

    employment_status_employed = 1 if employment_status.lower() == "employed" else 0
    employment_status_unemployed = 1 if employment_status.lower() == "unemployed" else 0

    customer_features = {
        'Income': income,
        'Account Age': account_age,
        'Employment Status_Employed': employment_status_employed,
        'Employment Status_Unemployed': employment_status_unemployed,
        'Loan Amount': loan_amount,
        'Average Mobile Money Balance': avg_mobile_balance,
        'Monthly Data Usage': monthly_data_usage,
        'Average Monthly Calls': avg_monthly_calls,
        'Total Mobile Money Amount': total_mobile_amount
    }

    if st.button("Predict Credit Score & Loan Approval Status"):
        credit_score, risk_level, approval_decision, _ = predict_credit_score(customer_features)
        st.subheader("Results:")
        st.write(f"**Credit Score:** {credit_score:.2f}")
        st.write(f"**Risk Level:** {risk_level}")
        #st.write(f"**Approval Decision:** {approval_decision}")
        if approval_decision == "Approved":
            st.success(f"**Approval Decision:** {approval_decision}")
        elif "Rejected" in approval_decision:
            st.error(f"**Approval Decision:** {approval_decision}")
        else:
            st.info(f"**Approval Decision:** {approval_decision}")


        # Display the progress bar
        st.subheader("Credit Score Visualization")
        create_progress_bar(credit_score)    

        # Customized messages for each credit score range
        st.divider()
        if credit_score < 580:
            st.write("**Your Credit Score is below 580 - You're in the High-Risk category. Consider improving your credit score for better loan opportunities.**")
        elif 580 <= credit_score < 670:
            st.write("**Your Credit Score is between 580 and 669 - You're in the Medium-Risk category. Consider improving your credit score for better loan opportunities.**")
        elif 670 <= credit_score < 740:
            st.write("**Your Credit Score is between 670 and 739 - You're in the Low-Risk category. Congratulations! You're likely to qualify for loans with favorable terms.**")
        else:
            st.write("**Your Credit Score is 740 or above - You're in the Very Low-Risk category. Excellent! You qualify for the best loan terms and interest rates.**")

        st.divider()
        st.subheader("Feature Importance Explanation")
        st.write("""
        **What is Feature Importance?**
        Feature importance tells us how much each feature (e.g., income, account age, etc.) contributes to the model's prediction. 
        The higher the importance, the more the feature influences the model's decision.
        """)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            importances_percentage = 100 * (importances / importances.sum())
            importance_df = pd.DataFrame({
                'Feature': model.feature_names_in_,
                'Importance (%)': importances_percentage
            }).sort_values(by='Importance (%)', ascending=False)

            for index, row in importance_df.iterrows():
                feature_name = row['Feature'].replace("_", " ").title()  # Format feature names
                explanation = f"- **{feature_name}**: {row['Importance (%)']:.2f}%\n"
                if "Income" in row['Feature']:
                    explanation += "   - Higher income generally improves creditworthiness.\n"
                elif "Account Age" in row['Feature']:
                    explanation += "   - Longer history with fintech platforms such as Mobile Money increases trust in financial stability.\n"
                elif "Loan Amount" in row['Feature']:
                    explanation += "   - Higher requested loan amounts can increase risk assessment.\n"
                elif "Average Mobile Money Balance" in row['Feature']:
                    explanation += "   - Consistent mobile balance indicates financial stability.\n"
                elif "Total Mobile Money Amount" in row['Feature']:
                    explanation += "   - Frequent transactions can suggest active financial engagement.\n"
                st.write(explanation)

            fig, ax = plt.subplots()
            sns.barplot(data=importance_df, x='Importance (%)', y='Feature', color='#FF4B4B', ax=ax)
            ax.set_xlabel("Importance (%)")
            ax.set_ylabel("Feature")
            ax.set_title("Feature Importance Plot")
            st.pyplot(fig)

if __name__ == "__main__":
    main()
