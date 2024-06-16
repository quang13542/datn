from sqlalchemy import func
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

from metadata import session
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

def visual_critical_skills():
    app = Dash(__name__)

    # Query the data
    skill_data = session.query(
        DimJobRole.name.label('job_role_name'),
        DimSkill.name.label('skill_name'),
        func.count(DimSkillList.skill_id).label('skill_count')
    ).join(FactJobPost, FactJobPost.job_role_id == DimJobRole.job_role_id
    ).join(DimSkillList, FactJobPost.job_post_id == DimSkillList.job_post_id
    ).join(DimSkill, DimSkillList.skill_id == DimSkill.skill_id
    ).filter(DimSkillList.core_skill == True
    ).group_by(
        DimJobRole.name,
        DimSkill.name
    ).order_by(func.count(DimSkillList.skill_id).desc()
    ).all()

    df = pd.DataFrame(skill_data, columns=['job_role_name', 'skill_name', 'skill_count'])

    job_role_list = df['job_role_name'].unique()

    app.layout = html.Div([
        html.H4("Critical Skills Analysis"),
        html.P("Job Role:"),
        dcc.Dropdown(
            id='job-role', 
            options=[{'label': jr, 'value': jr} for jr in job_role_list],
            value=job_role_list[0], 
            multi=True,
        ),
        dcc.Graph(id="graph"),
        html.H4("Skill Word Cloud"),
        html.Img(id="wordcloud")
    ])

    @app.callback(
        [Output("graph", "figure"), Output("wordcloud", "src")], 
        [Input("job-role", "value")]
    )
    def generate_chart(selected_job_role):
        if isinstance(selected_job_role, str):
            selected_job_role = [selected_job_role]
        
        filtered_data = df[df['job_role_name'].isin(selected_job_role)]

        fig = px.bar(filtered_data, x='skill_name', y='skill_count', color='job_role_name')
        fig.update_layout(
            title='Critical Skills for Job Roles',
            xaxis_title='Skill Name',
            yaxis_title='Skill Count',
            showlegend=True
        )

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_data['skill_name']))
        
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode('utf-8')
        wordcloud_src = f'data:image/png;base64,{img_base64}'

        return fig, wordcloud_src

    return app

def get_skill_data():
    skill_data = session.query(
        DimJobRole.name.label('job_role_name'),
        DimSkill.name.label('skill_name'),
        func.count(DimSkillList.skill_id).label('skill_count')
    ).join(FactJobPost, FactJobPost.job_role_id == DimJobRole.job_role_id
    ).join(DimSkillList, FactJobPost.job_post_id == DimSkillList.job_post_id
    ).join(DimSkill, DimSkillList.skill_id == DimSkill.skill_id
    ).filter(DimSkillList.core_skill == True
    ).group_by(
        DimJobRole.name,
        DimSkill.name
    ).order_by(func.count(DimSkillList.skill_id).desc()
    ).all()

    return pd.DataFrame(skill_data, columns=['job_role_name', 'skill_name', 'skill_count'])

# Define the Dash app
def visual_job_roles_by_skill():
    app = Dash(__name__)

    df = get_skill_data()
    skill_list = df['skill_name'].unique()

    app.layout = html.Div([
        html.H4("Job Roles by Skill Analysis"),
        html.P("Skill:"),
        dcc.Dropdown(
            id='skill', 
            options=[{'label': sk, 'value': sk} for sk in skill_list],
            value=[skill_list[0]], 
            multi=True,
        ),
        dcc.Graph(id="graph"),
        html.H4("Job Role Word Cloud"),
        html.Img(id="wordcloud")
    ])

    @app.callback(
        [Output("graph", "figure"), Output("wordcloud", "src")], 
        [Input("skill", "value")]
    )
    def generate_charts(selected_skill):
        if isinstance(selected_skill, str):
            selected_skill = [selected_skill]
        
        filtered_data = df[df['skill_name'].isin(selected_skill)]

        # Bar chart for job roles by skill
        job_role_by_skill = filtered_data.groupby('skill_name')['job_role_name'].nunique().reset_index(name='job_role_count')
        fig_job_role_by_skill = px.bar(job_role_by_skill, x='skill_name', y='job_role_count')
        fig_job_role_by_skill.update_layout(
            title='Job Roles by Skill',
            xaxis_title='Skill Name',
            yaxis_title='Job Role Count',
            showlegend=False
        )

        # Generate word cloud for job roles
        job_role_counts = filtered_data['job_role_name'].value_counts()
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(job_role_counts)
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode('utf-8')
        wordcloud_src = f'data:image/png;base64,{img_base64}'

        return fig_job_role_by_skill, wordcloud_src

    return app