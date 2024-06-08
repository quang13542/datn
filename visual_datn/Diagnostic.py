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



def visual_com_size_salary():
    app = Dash(__name__)

    # Query to calculate the average salary by company size
    average_salary_by_size = session.query(
        DimCompany.size,
        func.avg(FactJobPost.salary_max).label('avg_salary_max'),
        func.avg(FactJobPost.salary_min).label('avg_salary_min')
    ).join(FactJobPost, DimCompany.company_id == FactJobPost.company_id) \
    .group_by(DimCompany.size) \
    .all()

    # Convert the query results into a DataFrame
    df_avg_salary = pd.DataFrame(average_salary_by_size, columns=['company_size', 'avg_salary_max', 'avg_salary_min'])
    df_avg_salary = df_avg_salary.sort_values(by='company_size')

    print(df_avg_salary)

    app.layout = html.Div([
        html.H4("Average Salary by Company Size"),
        dcc.Graph(id="salary-graph"),
    ])

    @app.callback(
        Output("salary-graph", "figure"), 
        [Input("salary-graph", "id")]
    )
    def update_graph(_):
        fig = px.bar(df_avg_salary, x='company_size', y=['avg_salary_max', 'avg_salary_min'], barmode='group')

        fig.update_layout(
            title='Average Salary by Company Size',
            xaxis_title='Company Size',
            yaxis_title='Average Salary',
            showlegend=True
        )

        return fig

    return app