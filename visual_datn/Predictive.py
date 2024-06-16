import seaborn as sns
from dash import Dash, dcc, html, Input, Output, html, dcc
from plotly.subplots import make_subplots
from metadata import session
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pcolors
from wordcloud import WordCloud
import dash.dependencies as dd
from io import BytesIO
import base64
from sqlalchemy import func
import matplotlib.pyplot as plt
import json
import matplotlib.colors as mcolors
import svgwrite
from svgwrite import cm, mm
import numpy as np
from scipy import stats
import plotly.express as px
import re
from statsmodels.tsa.statespace.sarimax import SARIMAX

from load_datn.models import (
    DimSource,
    FactJobPost,
    DimSkillList,
    DimSkill,
    DimJobRole,
    DimCompany,
    DimPosition,
    DimDate
)

def visual_skill_demand():
    app = Dash(__name__)

    # Query the data
    visual_data = session.query(
        DimSkill.name.label('skill_name'),
        DimDate.year,
        DimDate.month,
        func.count(FactJobPost.job_post_id).label('demand')
    ).join(DimSkillList, DimSkill.skill_id == DimSkillList.skill_id)\
    .join(FactJobPost, DimSkillList.job_post_id == FactJobPost.job_post_id)\
    .join(DimDate, FactJobPost.start_recruit_date_id == DimDate.date_id)\
    .group_by(DimSkill.name, DimDate.year, DimDate.month).all()

    df = pd.DataFrame(visual_data, columns=['skill_name', 'year', 'month', 'demand'])
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    skill_list = df['skill_name'].unique()

    app.layout = html.Div([
        html.H4("Skill Demand Analysis Over Time"),
        dcc.Dropdown(
            id='skills', 
            options=[{'label': skill, 'value': skill} for skill in skill_list],
            value=[skill_list[0]], 
            multi=True,
            searchable=True
        ),
        dcc.Graph(id="graph"),
    ])

    @app.callback(
        Output("graph", "figure"),
        [Input("skills", "value")]
    )
    def generate_chart(selected_skills):
        filtered_data = df[df['skill_name'].isin(selected_skills)]

        fig = px.line(filtered_data, x='date', y='demand', color='skill_name')

        fig.update_layout(
            title='Skill Demand Analysis Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Job Postings',
            showlegend=True
        )

        return fig

    return app

def visual_job_role_popularity():
    app = Dash(__name__)

    visual_data = session.query(
        DimJobRole.name.label('job_role'),
        DimDate.year,
        DimDate.month,
        func.count(FactJobPost.job_post_id).label('count')
    ).join(DimJobRole, FactJobPost.job_role_id == DimJobRole.job_role_id)\
    .join(DimDate, FactJobPost.start_recruit_date_id == DimDate.date_id)\
    .group_by(DimJobRole.name, DimDate.year, DimDate.month).all()

    df = pd.DataFrame(visual_data, columns=['job_role', 'year', 'month', 'count'])
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    job_roles = df['job_role'].unique()

    app.layout = html.Div([
        html.H4("Job Role Popularity Over Time"),
        dcc.Checklist(
            id='job-roles', 
            options=[{'label': role, 'value': role} for role in job_roles],
            value=[job_roles[0]], 
            inline=True
        ),
        dcc.Graph(id="graph"),
    ])

    @app.callback(
        Output("graph", "figure"),
        [Input("job-roles", "value")]
    )
    def generate_chart(selected_roles):
        filtered_data = df[df['job_role'].isin(selected_roles)]

        fig = px.line(filtered_data, x='date', y='count', color='job_role')

        fig.update_layout(
            title='Job Role Popularity Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Job Postings',
            showlegend=True
        )

        return fig

    return app

def visual_skill_demand_forecast():
    app = Dash(__name__)

    # Query the data
    visual_data = session.query(
        DimSkill.name.label('skill_name'),
        DimDate.year,
        DimDate.month,
        func.count(FactJobPost.job_post_id).label('demand')
    ).join(DimSkillList, DimSkill.skill_id == DimSkillList.skill_id)\
    .join(FactJobPost, DimSkillList.job_post_id == FactJobPost.job_post_id)\
    .join(DimDate, FactJobPost.start_recruit_date_id == DimDate.date_id)\
    .group_by(DimSkill.name, DimDate.year, DimDate.month).all()

    df = pd.DataFrame(visual_data, columns=['skill_name', 'year', 'month', 'demand'])
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df.set_index('date', inplace=True)

    # Ensure that all expected dates are present
    df = df.groupby('skill_name').apply(lambda group: group.resample('MS').sum().fillna(0)).reset_index(level=0, drop=True)

    skill_list = df['skill_name'].unique()

    print(df.isna().sum())

    app.layout = html.Div([
        html.H4("Skill Demand Analysis with Forecast"),
        dcc.Dropdown(
            id='skills', 
            options=[{'label': skill, 'value': skill} for skill in skill_list],
            value=[skill_list[0]], 
            multi=True,
            searchable=True
        ),
        dcc.Graph(id="graph"),
    ])

    @app.callback(
        Output("graph", "figure"),
        [Input("skills", "value")]
    )
    def generate_chart(selected_skills):
        filtered_data = df[df['skill_name'].isin(selected_skills)]
        
        fig = px.line(filtered_data.reset_index(), x='date', y='demand', color='skill_name')

        for skill in selected_skills:
            skill_data = filtered_data[filtered_data['skill_name'] == skill]['demand']
            model = SARIMAX(skill_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            model_fit = model.fit(disp=False)
            forecast = model_fit.get_forecast(steps=12)
            forecast_df = forecast.conf_int()
            forecast_df['forecast'] = model_fit.predict(start=forecast_df.index[0], end=forecast_df.index[-1])
            forecast_df['skill_name'] = skill
            forecast_df.index = pd.date_range(start=filtered_data.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')

            fig.add_traces([
                go.Scatter(
                    x=forecast_df.index,
                    y=forecast_df['forecast'],
                    mode='lines',
                    name=f'Forecast {skill}',
                    line=dict(dash='dash')
                ),
                go.Scatter(
                    x=forecast_df.index,
                    y=forecast_df.iloc[:, 0],  # Lower bound of confidence interval
                    fill=None,
                    mode='lines',
                    line=dict(color='lightgrey'),
                    showlegend=False
                ),
                go.Scatter(
                    x=forecast_df.index,
                    y=forecast_df.iloc[:, 1],  # Upper bound of confidence interval
                    fill='tonexty',
                    mode='lines',
                    line=dict(color='lightgrey'),
                    showlegend=False
                )
            ])
        
        fig.update_layout(
            title='Skill Demand Analysis with Forecast',
            xaxis_title='Date',
            yaxis_title='Number of Job Postings',
            showlegend=True
        )

        return fig

    return app