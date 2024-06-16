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

from load_datn.models import (
    DimSource,
    FactJobPost,
    DimSkillList,
    DimSkill,
    DimJobRole,
    DimCompany,
    DimPosition
)

colors = pcolors.qualitative.Plotly

def visual_exp_salary():
    app = Dash(__name__)

    # Query the data
    visual_data = session.query(
        FactJobPost.job_level,
        DimSource.name,
        FactJobPost.salary_min,
        FactJobPost.salary_max,
        FactJobPost.years_of_experience
    ).join(DimSource).filter(FactJobPost.salary_max != 0).filter(FactJobPost.years_of_experience != -1)

    query = session.query(DimSource)
    results = query.all()

    source_list = [source.name for source in results]
    df = pd.DataFrame(visual_data, columns=['level', 'source', 'salary_min', 'salary_max', 'years_of_experience'])

    # Remove outliers using Z-score method
    df['z_score'] = stats.zscore(df['salary_max'])
    threshold = 3
    df = df[(df['z_score'].abs() <= threshold)]
    df = df.drop(columns=['z_score'])

    level_list = df['level'].unique()

    app.layout = html.Div([
        html.H4("Salary Analysis"),
        html.P("Job Level:"),
        dcc.Checklist(
            id='job-level', 
            options=[{'label': l, 'value': l} for l in level_list],
            value=[level_list[0]], 
            inline=True
        ),
        html.P("Source:"),
        dcc.Checklist(
            id='source', 
            options=[{'label': s, 'value': s} for s in source_list],
            value=[source_list[0]], 
            inline=True
        ),
        dcc.Graph(id="graph"),
    ])

    @app.callback(
        Output("graph", "figure"), 
        [Input("job-level", "value"), 
        Input("source", "value")]
    )
    def generate_chart(selected_job_level, selected_source):
        filtered_data = df[
            (df['level'].isin(selected_job_level)) & 
            (df['source'].isin(selected_source))
        ]

        fig = px.strip(filtered_data, x='years_of_experience', y='salary_max', color='level')

        fig.update_layout(
            title='Experience vs Salary Distribution by Job Level',
            xaxis_title='Experience (years)',
            yaxis_title='Salary Max',
            showlegend=True
        )

        return fig

    return app


def parse_company_size(size):
    if '+' in size:
        lower_bound = int(size.replace('+', ''))
        upper_bound = float('inf')  # Represents no upper limit
    else:
        bounds = size.split('-')
        lower_bound = int(bounds[0])
        upper_bound = int(bounds[1])
    return lower_bound, upper_bound

def visual_com_size_salary():
    app = Dash(__name__)

    # Query to calculate the average salary by company size
    average_salary_by_size = session.query(
        DimCompany.size,
        func.avg(FactJobPost.salary_max).label('avg_salary_max'),
        func.avg(FactJobPost.salary_min).label('avg_salary_min'),
        func.avg(FactJobPost.years_of_experience).label('avg_yoe'),
    ).filter(FactJobPost.salary_max != 0) \
    .filter(FactJobPost.years_of_experience != -1) \
    .join(FactJobPost, DimCompany.company_id == FactJobPost.company_id) \
    .group_by(DimCompany.size) \
    .all()

    # Convert the query results into a DataFrame
    df_avg_salary = pd.DataFrame(average_salary_by_size, columns=['company_size', 'avg_salary_max', 'avg_salary_min', 'avg_yoe'])
    df_avg_salary = df_avg_salary.astype({'company_size': str, 'avg_salary_max': float, 'avg_salary_min': float, 'avg_yoe': float})
    df_avg_salary['parsed_size'] = df_avg_salary['company_size'].apply(parse_company_size)

    # Sort DataFrame based on the parsed size lower bound
    df_avg_salary = df_avg_salary.sort_values(by='parsed_size', key=lambda x: [b[0] for b in x]).reset_index(drop=True)

    print(df_avg_salary.dtypes)

    app.layout = html.Div([
        html.H4("Average Salary by Company Size"),
        dcc.Graph(id="salary-bar-graph"),
        dcc.Graph(id="salary-line-graph"),
    ])

    @app.callback(
        Output("salary-bar-graph", "figure"), 
        [Input("salary-bar-graph", "id")]
    )
    def update_yoe_graph(_):
        fig = px.line(df_avg_salary, x='company_size', y='avg_yoe')

        fig.update_layout(
            title='Average years of experience by Company Size',
            xaxis_title='Company Size',
            yaxis_title='Average years of experience',
            showlegend=True
        )
        return fig

    @app.callback(
        Output("salary-line-graph", "figure"),
        [Input("salary-line-graph", "id")]
    )
    def update_salary_graph(_):
        fig = px.line(df_avg_salary, x='company_size', y=['avg_salary_max', 'avg_salary_min'])

        fig.update_layout(
            title='Average Salary Trend by Company Size',
            xaxis_title='Company Size',
            yaxis_title='Average Salary',
            showlegend=True
        )
        return fig

    return app