import streamlit as st
from auth import auth
from payment import payment
from utils import check_subscription, initialize_db
from tabula.io import read_pdf, convert_into
import pandas as pd

def main_app():
    st.title("PDF to CSV Converter")
    st.sidebar.header("Upload PDF File")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        tables = read_pdf(uploaded_file, pages='all', multiple_tables=True)

        csv_path = "temp.csv"
        convert_into(uploaded_file, csv_path, output_format="csv", pages='all')

        df = pd.read_csv(csv_path, skip_blank_lines=True)
        df.dropna(how='all', inplace=True)

        column_names = df.iloc[0]
        column_names = [name if 'Unnamed' not in str(name) else '' for name in column_names]
        df.columns = column_names

        second_column_name = column_names[1]
        agg_functions = {}

        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                agg_functions[column] = 'sum'
            else:
                agg_functions[column] = 'first'

        grouped_df = df.groupby(second_column_name, as_index=False).agg(agg_functions)
        st.write("Grouped DataFrame:")
        st.write(grouped_df)

        grouped_csv_path = "grouped_statement.csv"
        grouped_df.to_csv(grouped_csv_path, index=False)
        st.success(f"Grouped data saved to {grouped_csv_path}")

if __name__ == "__main__":
    initialize_db()  # Ensure the database schema is created
    auth()
    if st.session_state.logged_in:
        if payment():
            if check_subscription(st.session_state.user_email):
                main_app()
            else:
                st.sidebar.error("Your subscription has expired. Please renew your subscription.")
