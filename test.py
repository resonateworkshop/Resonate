import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Sample data
data = {
    'Category': ['A', 'B', 'C'],
    'Value1': [10, 15, 20],
    'Value2': [5, 10, 15],
    'Value3': [8, 12, 18]
}

df = pd.DataFrame(data)

# Initial figure
fig = go.Figure()

# Add a bar trace for the initial data
fig.add_trace(go.Bar(x=df['Category'], y=df['Value1'], name='Value1'))

# Streamlit app
st.title('Drill-Down Feature')

# Drill-down button
if st.button('Drill Down'):
    # Add additional bar traces for drilled-down data
    fig.add_trace(go.Bar(x=df['Category'], y=df['Value2'], name='Value2'))
    fig.add_trace(go.Bar(x=df['Category'], y=df['Value3'], name='Value3'))

    # Update layout for better visualization
    fig.update_layout(barmode='group', title='Drilled-Down Data')

    # Display the updated figure
    st.plotly_chart(fig)
