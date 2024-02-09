import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
import plotly.graph_objects as go
import base64
import plotly.io as pio
from PIL import Image 
import os

### custom pallete
custom_palette = ["#ff6633", "#333366", "#0099cc", "#ffcc33", "#99cc33", "#666666"]

### load dataset
raw = pd.read_excel("Combined - Q1, Q2 and Q3 2023.xlsx")

# Replace missing values in string columns with 'NA'
string_columns = raw.select_dtypes(include=['object']).columns
raw[string_columns] = raw[string_columns].fillna('NA')

# Replace missing values in numerical columns with 0
numerical_columns = raw.select_dtypes(include=['number']).columns
raw[numerical_columns] = raw[numerical_columns].fillna(0)

### pre-process dataset
bin_edges = [10, 20, 30, 40, 50, 100]  # Define your bin edges
bin_labels = ['10-20', '20-30', '30-40', '40-50', '50+']

raw = raw.dropna(subset=['Age'])

raw['Age_bins'] = pd.cut(raw['Age'], bins=bin_edges, labels=bin_labels, right=False)

impact_columns = [col for col in raw.columns if col.startswith('Impact')]
behaviour_columns = [col for col in raw.columns if col.startswith('Behaviour')]

### streamlit main title

st.set_page_config(layout="wide", page_icon=":bar_chart:")
st.markdown("""<style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 5rem;
                }
        </style>""", unsafe_allow_html=True)

color1 = "#ff6633"
color2 = "#ffcc33"

# Create a card-style markdown for the title
st.markdown(
    f"""
    <div style="
        background: {color1};
        background: -webkit-linear-gradient(to right, {color1}, {color2});
        background: linear-gradient(to right, {color1}, {color2});
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        height: 60px;
        line-height: 60px;
        color: Black;
    ">{"Resonate Dashboard"}</div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("# Select the criterias:")
year_filter = st.sidebar.multiselect('Year Selection', options=list(raw['Year'].unique()), default=list(raw['Year'].unique()))
impact_beh_option = st.sidebar.selectbox('Organization\'s Impact or Behavioural Improvement?', ('Impact', 'Behavioural'))
age_filter = st.sidebar.multiselect('Select Age', options=list(raw['Age_bins'].unique()), default=list(raw['Age_bins'].unique()))
impact_filter = st.sidebar.multiselect('Select Impact', options=impact_columns, default=impact_columns)
behaviour_filter = st.sidebar.multiselect('Select Behaviour', options=behaviour_columns, default=behaviour_columns)

filtered_data = raw[(raw['Age_bins'].isin(age_filter))]

impact_data = raw[raw.columns[raw.columns.isin(impact_columns)].values]

behaviour_data = raw[raw.columns[raw.columns.isin(behaviour_columns)].values]
impact_filtered_data = raw[raw.columns[raw.columns.isin(impact_filter)].values]
year_filtered_data = raw[raw.columns[raw.columns.isin(year_filter)].values]
behaviour_filtered_data = raw[raw.columns[raw.columns.isin(behaviour_filter)].values]

filtered_data = filtered_data.merge(impact_filtered_data, left_index=True, right_index=True,how = 'inner', suffixes=('_x', None))
filtered_data = filtered_data.merge(behaviour_filtered_data, left_index=True, right_index=True,how = 'inner', suffixes=('_x', None))
filtered_data = filtered_data.merge(year_filtered_data, left_index=True, right_index=True,how = 'inner', suffixes=('_x', None))


result = filtered_data.groupby(['Quarter', 'Age_bins'])['Participant ID'].count().reset_index()

### sunburst plot - Age bins
fig_sunburst = px.sunburst(result, path=['Quarter', 'Age_bins'], values='Participant ID', 
                           labels={'Participant ID': 'Participant ID'}, title = "Total participants by quarter and age", 
                           color_discrete_sequence=custom_palette,  
                           )
fig_sunburst.update_traces(textinfo="label+value", )
fig_sunburst.update_layout(title=dict(font=dict(size=20), x = 0.5, xanchor= 'center'))

### stacked bar plot - Impact
result = filtered_data.groupby(['Quarter'])[impact_filter].sum().reset_index()
result_melted = pd.melt(result, id_vars=['Quarter'], var_name='Impact', value_name='Sum')
result_melted['perc_impact'] = (result_melted['Sum']/impact_filtered_data.shape[0])*100
fig_impact = px.bar(result_melted, x='Impact', y='perc_impact', color='Quarter', barmode = "stack", 
                    title = "Total Impact made each quarter", color_discrete_sequence=custom_palette,
                    labels={
                     "Impact": "Indicators of Success",
                     "perc_impact": "% of participants impacted",
                 })
fig_impact.update_layout(legend=dict(orientation='h', xanchor = "center", x = 0.5, y = 1.2))
fig_impact.update_layout(title=dict(font=dict(size=20), x = 0.5, xanchor= 'center'))
for index, row in result_melted.groupby('Impact')['perc_impact'].sum().reset_index().iterrows():
    fig_impact.add_annotation(
        x=row['Impact'],
        y=row['perc_impact'] + 15,  # Adjust the vertical position of the text
        text=str(int(row['perc_impact'])) + "%",
        showarrow=False,
    )

### line plot - behaviour
result = filtered_data.groupby(['Quarter'])[behaviour_filter].sum().reset_index()
result_melted = pd.melt(result, id_vars=['Quarter'], var_name='Behaviour', value_name='Sum')
fig_beh = px.line(result_melted, x='Quarter', y='Sum', color='Behaviour', markers = True, 
                  title='Total participants for each quarter by Behaviour', color_discrete_sequence=custom_palette,
                  labels={
                     "Sum": "# of participants",
                 })
fig_beh.update_layout(legend=dict(orientation='h', yanchor="top", xanchor = "center", x = 0.5))
fig_beh.update_layout(title=dict(font=dict(size=20), x = 0.5, xanchor= 'center'))


### bar plot - Program
result = filtered_data.groupby(['Quarter', 'Age_bins', 'Program'])['Participant ID'].count().reset_index()
fig_program = px.bar(result, x='Quarter', y='Participant ID', color='Program', facet_col='Age_bins',
              title='Count of Participants by Program and Quarter',
              labels={'Participant ID': 'Count of Participant'},
              barmode = 'group', color_discrete_sequence=custom_palette)
fig_program.update_layout(legend=dict(orientation='h', yanchor="top", y = -0.1))
fig_program.update_layout(title=dict(font=dict(size=20), x = 0.5, xanchor= 'center'))


total_impact_made = impact_filtered_data.shape[0]
total_behaviour_made = behaviour_filtered_data.shape[0]

sum_impact_made = impact_data.sum()
sum_behaviour_made = behaviour_data.sum()

impact_col1 = (sum_impact_made.values[0]/total_impact_made)*100
impact_col2 = (sum_impact_made.values[1]/total_impact_made)*100
impact_col3 = ((sum_impact_made.values[2] + sum_impact_made.values[3])/total_impact_made)*100
impact_col4 = (sum_impact_made.values[4]/total_impact_made)*100

behaviour_col1 = sum_behaviour_made.values[0]
behaviour_col2 = sum_behaviour_made.values[1]
behaviour_col3 = sum_behaviour_made.values[2]

impact_made_indicator = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = total_impact_made,
    title = {'text': "Total Participants Surveyed"},
    gauge=dict(bar=dict(color="#ff6633"),
    )))

impact_made_indicator.update_layout(margin=dict(t=100, b=0, l=20, r=20))
impact_made_indicator.update_traces(title_font_size=30)
impact_made_indicator.update_xaxes(automargin=False)
impact_made_indicator.update_yaxes(automargin=False)

# Function to generate a card-like appearance
def card_style_header(content):
    return f"""
        <div style="
            background-color: #f0f0f0;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            font-size: 30px;
            border-left: 5px solid #3498db;
            text-align: center;
            height: 60px;
            line-height: 60px;
        ">{content}</div>
    """

def card_style_desc(image_url, content):
    return f"""
        <div style="
            background-color: #f0f0f0;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            font-size: 20px;
            border-left: 5px solid #3498db;
            height: 40px;
            text-align: center;
            line-height: 40px;
        ">
        <div style="flex: 1; text-align: center; line-height: 40px;">
        <img src="data:image/png;base64,{image_url}" alt="Image" style="max-height: 30px;">
        {content}
        </div>
        </div>
    """

def card_style_value(content):
    return f"""
        <div style="
            background-color: #f0f0f0;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            font-size: 20px;
            #border-left: 5px solid #3498db;
            height: 40px;
            text-align: center;
            line-height: 40px;
        ">{content}</div>
    """

with st.container():
    col1, col2 = st.columns([1.8, 1.5])
    style_metric_cards(border_left_color="#DBF227")

    with col1:
        st.plotly_chart(impact_made_indicator, use_container_width=True)

    if impact_beh_option == "Impact":

        with col2:
            
            st.markdown("##")
            col2.markdown(card_style_header("Indicators of Success"), unsafe_allow_html=True)
            col3, col4 = st.columns([3,1])

            with col3:
                st.markdown("#####")
            with col4:
                st.markdown("#####")

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/leadership_logo-removebg-preview.png", 'rb').read()).decode()
                content = sum_impact_made.index[0].split('-')[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(impact_col1)) + "%"), unsafe_allow_html=True)

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/business_logo-removebg-preview.png", 'rb').read()).decode()
                content = sum_impact_made.index[1].split('-')[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(impact_col2)) + "%"), unsafe_allow_html=True)

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/new_job_logo-removebg-preview.png", 'rb').read()).decode()
                content = "Promotion"
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(impact_col3)) + "%"), unsafe_allow_html=True)

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/academic_logo-removebg-preview.png", 'rb').read()).decode()
                content = sum_impact_made.index[4].split('-')[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(impact_col4)) + "%"), unsafe_allow_html=True)

    if impact_beh_option == "Behavioural":

            with col2:
                st.markdown("##")
                col2.markdown(card_style_header("Behavioural Impact"), unsafe_allow_html=True)
                col3, col4 = st.columns([3,1])

            with col3:
                st.markdown("#####")
            with col4:
                st.markdown("#####")

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/confidence_logo.png", 'rb').read()).decode()
                content = sum_behaviour_made.index[0].split('-', 1)[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(sum_behaviour_made.values[0]))), unsafe_allow_html=True)

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/decision_making_power.png", 'rb').read()).decode()
                content = sum_behaviour_made.index[1].split('-', 1)[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(sum_behaviour_made.values[1]))), unsafe_allow_html=True)

            with col3:
                image_path = base64.b64encode(open(r"/mount/src/resonate/Images/resilience_power.png", 'rb').read()).decode()
                content = sum_behaviour_made.index[2].split('-', 1)[1]
                col3.markdown(card_style_desc(image_path, content), unsafe_allow_html=True)
            with col4:
                col4.markdown(card_style_value(str(int(sum_behaviour_made.values[2]))), unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_impact, use_container_width=True)
    with col2:
        st.plotly_chart(fig_program, use_container_width=True)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_sunburst, use_container_width=True)
    with col2:
        st.plotly_chart(fig_beh, use_container_width=True)