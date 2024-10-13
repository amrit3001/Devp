import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Set the title of the dashboard
st.markdown(
    """
    <h1 style='text-align: center; color: #4A4A4A; font-family: "Arial"; font-size: 40px;'>Imports/Exports Dashboard</h1>
    """, 
    unsafe_allow_html=True
)

# Load the dataset directly from a specified file path
data_path = r"C:\Users\amrit\Downloads\Amrit devp project\Imports_Exports_Dataset.csv"  # Modify the path as needed

@st.cache_data
def load_data(data_path):
    return pd.read_csv(data_path)

dataset = load_data(data_path)

# Sample dataset
sdset = dataset.sample(n=min(3001, len(dataset)), random_state=55004)  # Adjust to actual length

# Add Import/Export switch at the top of the sidebar
st.sidebar.header("Select Import/Export")
selected_type = st.sidebar.radio("Choose the type of Transaction:", ["Import", "Export", "Both"])

# Filter the dataset based on Import/Export selection
if selected_type != "Both":
    sdset = sdset[sdset['Import_Export'] == selected_type]

# Add a year dropdown in the sidebar allowing multiple selections
sdset['Date'] = pd.to_datetime(sdset['Date'], format='%d-%m-%Y', errors='coerce')  # Handle parsing errors
sdset['Year'] = sdset['Date'].dt.year
years = sdset['Year'].unique()
selected_years = st.sidebar.multiselect("Select year(s):", sorted(years), default=sorted(years)[:1])

# Filter the dataset based on the selected years
filtered_data = sdset[sdset['Year'].isin(selected_years)]

# Dropdown selection for charts
st.sidebar.header("Select Chart")
chart_options = [
    "Payment Method Distribution",
    "Average Transaction Value Gauge",
    "Total Transaction Value by Category",
    "Geographical Heatmap of Transaction Frequency by Country",
    "Percentage of Total Transaction Value by Shipping Method",
    "Correlation Matrix Heatmap",
    "Boxplot of Value by Top 10 Products",
    "Violin Plot of Value by Category",
    "Scatter Plot: Weight vs Value",
    "Average Total Value for Top 5 Products"
]

selected_chart = st.sidebar.radio("Select a chart to display:", chart_options)

# Visualization Logic
if selected_chart == "Payment Method Distribution":
    st.subheader('Distribution of Transactions by Payment Method')
    payment_method_totals = filtered_data.groupby('Payment_Terms').size().reset_index(name='Count')
    fig_payment = px.pie(payment_method_totals, names='Payment_Terms', values='Count', 
                          color_discrete_sequence=px.colors.qualitative.Plotly)
    fig_payment.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_color='black')
    st.plotly_chart(fig_payment)

elif selected_chart == 'Average Transaction Value Gauge':
    st.subheader('Average Transaction Value Gauge')

    if 'Value' in filtered_data.columns and not filtered_data.empty:
        average_value = filtered_data['Value'].mean()
        figa = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_value,
            title={'text': "", 'font': {'color': 'black'}},
            gauge={
                'axis': {'range': [None, filtered_data['Value'].max()], 'tickcolor': "black"},
                'bar': {'color': "lightblue"},
                'steps': [
                    {'range': [0, average_value * 0.5], 'color': "lightgray"},
                    {'range': [average_value * 0.5, average_value], 'color': "lightgray"},
                    {'range': [average_value, filtered_data['Value'].max()], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 1,
                    'value': average_value
                },
            },
            number={'font': {'color': 'black'}}
        ))

        figa.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={'color': "black"}
        )
        st.plotly_chart(figa)
    else:
        st.error("The 'Value' column is missing from the filtered dataset or no data available.")

elif selected_chart == "Total Transaction Value by Category":
    st.subheader('Total Transaction Value by Category')
    category_totals = filtered_data.groupby('Category').agg({'Value': 'sum'}).reset_index()
    category_totals.rename(columns={'Value': 'Transaction Value'}, inplace=True)
    category_totals = category_totals.sort_values(by='Transaction Value', ascending=False)

    if not category_totals.empty:
        highest_transaction = category_totals.loc[category_totals['Transaction Value'].idxmax()]
        st.write(f"Category with the highest transaction value: {highest_transaction['Category']} - Value: {highest_transaction['Transaction Value']}")

        fig_bar = px.bar(category_totals, x='Category', y='Transaction Value', 
                         labels={'Transaction Value': 'Total Transaction Value', 'Category': 'Category'},
                         color='Category', color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_bar.update_layout(xaxis_title='Category', yaxis_title='Total Transaction Value', 
                              plot_bgcolor='white', paper_bgcolor='white', font_color='black')
        st.plotly_chart(fig_bar)
    else:
        st.error("No data available for the selected categories.")

elif selected_chart == "Percentage of Total Transaction Value by Shipping Method":
    st.subheader('Percentage of Total Transaction Value by Shipping Method')
    shipping_value_totals = filtered_data.groupby('Shipping_Method').agg({'Value': 'sum'}).reset_index()

    if not shipping_value_totals.empty:
        fig_shipping = px.pie(shipping_value_totals, names='Shipping_Method', values='Value', 
                               color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_shipping.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_color='black')
        st.plotly_chart(fig_shipping)
    else:
        st.error("No data available for the selected shipping methods.")

elif selected_chart == "Geographical Heatmap of Transaction Frequency by Country":
    st.subheader('Geographical Heatmap of Transaction Frequency by Country')
    country_totals = filtered_data['Country'].value_counts().reset_index()
    country_totals.columns = ['Country', 'Frequency']

    fig_map = go.Figure(data=go.Choropleth(
        locations=country_totals['Country'],
        locationmode='country names',
        z=country_totals['Frequency'],
        colorscale='Blues',
        showscale=False  # This hides the color bar
    ))

    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='mercator',
            lonaxis_range=[-180, 180],  # Increase the longitude range for a larger map view
            lataxis_range=[-90, 90]     # Increase the latitude range for a larger map view
        ),
        autosize=False,  # Set autosize to False to manually adjust the width
        width=1400,  # Increase width to match the white background
        height=600,  # Set height as needed
        plot_bgcolor='white', paper_bgcolor='white', font_color='black'
    )
    
    st.plotly_chart(fig_map)

elif selected_chart == "Correlation Matrix Heatmap":
    st.subheader('Correlation Matrix Heatmap')
    non_categorical_vars = filtered_data[['Quantity', 'Value', 'Weight']]
    correlation_matrix = non_categorical_vars.corr()

    if not correlation_matrix.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.5f')
        st.pyplot(plt)
    else:
        st.error("No data available for correlation matrix.")

elif selected_chart == "Boxplot of Value by Top 10 Products":
    st.subheader('Boxplot of Value by Top 10 Products')
    top_10_categories = filtered_data['Product'].value_counts().nlargest(10).index
    top_10_sample = filtered_data[filtered_data['Product'].isin(top_10_categories)]

    if not top_10_sample.empty:
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='Product', y='Value', data=top_10_sample, palette='bright', flierprops=dict(marker='o', color='red', markersize=6))
        plt.xticks(rotation=90)
        st.pyplot(plt)
    else:
        st.error("No data available for the top products.")

elif selected_chart == "Violin Plot of Value by Category":
    st.subheader('Violin Plot of Value by Category')
    plt.figure(figsize=(12, 6))
    sns.violinplot(x='Category', y='Value', data=filtered_data, palette='bright')
    plt.xticks(rotation=90)
    st.pyplot(plt)

elif selected_chart == "Scatter Plot: Weight vs Value":
    st.subheader('Scatter Plot: Weight vs Value')
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_data['Weight'], filtered_data['Value'], alpha=0.5, color='blue')
    plt.xlabel('Weight')
    plt.ylabel('Value')
    st.pyplot(plt)

elif selected_chart == "Average Total Value for Top 5 Products":
    st.subheader('Average Total Value for Top 5 Products')
    top_5_products = filtered_data.groupby('Product')['Value'].sum().nlargest(5).index
    top_5_data = filtered_data[filtered_data['Product'].isin(top_5_products)]
    avg_value_top_5 = top_5_data.groupby('Product')['Value'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Product', y='Value', data=avg_value_top_5, palette='viridis')
    plt.xlabel('Product', fontsize=14)
    plt.ylabel('Average Total Value', fontsize=14)
    plt.xticks(rotation=45)
    st.pyplot(plt)


else:
    st.error("Invalid chart selection.")
