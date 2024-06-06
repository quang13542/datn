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
import requests

from load_datn.models import (
    DimSource,
    FactJobPost,
    DimSkillList,
    DimSkill,
    DimJobRole
)

url = "https://raw.githubusercontent.com/datasets/geo-boundaries-world-110m/master/countries/VNM.geojson"
vietnam_geojson = requests.get(url).json()
colors = pcolors.qualitative.Plotly

def test():
    visual_data = session.query(
        FactJobPost.job_level, FactJobPost.years_of_experience
    )

    print(visual_data[0])

def visual_yoe():
    app = Dash(__name__)

    visual_data = session.query(
        FactJobPost.job_level,
        DimSource.name,
        FactJobPost.years_of_experience
    ).join(DimSource).filter(FactJobPost.years_of_experience != -1)

    query = session.query(DimSource)
    results = query.all()

    source_list = [source.name for source in results]
    df = pd.DataFrame(visual_data, columns=['level', 'source', 'yoe'])
    level_list = df['level'].unique()

    app.layout = html.Div([
        html.H4("Analysis of the year of experience"),
        html.P("job-level:"),
        dcc.Checklist(
            id='job-level', 
            options=level_list,
            value=[level_list[0]], 
            inline=True
        ),
        html.P("source:"),
        dcc.Checklist(
            id='source', 
            options=source_list,
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
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Box Plot", "Stacked Bar Chart"))

        filtered_data = df[
            (df['level'].isin(selected_job_level)) & 
            (df['source'].isin(selected_source))
        ]

        for i, level in enumerate(filtered_data['level'].unique()):
            level_data = filtered_data[filtered_data['level'] == level]

            fig.add_trace(go.Box(
                y=level_data['yoe'],
                x=[level]*len(level_data),
                name=level,
                marker_color=colors[i % len(colors)],
            ), row=1, col=1)

        grouped_data = filtered_data.groupby(['level', 'yoe']).size().unstack(fill_value=0)
        for i, level in enumerate(filtered_data['level'].unique()):
            fig.add_trace(go.Bar(
                x=grouped_data.columns,
                y=grouped_data.loc[level],
                name=level,
                marker_color=colors[i % len(colors)],
                showlegend=False,
            ), row=1, col=2)

        fig.update_layout(
            barmode='stack',
            title='Stacked Bar Charts',
            showlegend=True
        )

        fig.update_xaxes(title_text="Level", row=1, col=1)
        fig.update_yaxes(title_text="Years of Experience", row=1, col=1)
        fig.update_xaxes(title_text="Years of Experience", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=1, col=2)
    
        return fig

    return app

def visual_salary_analysis():
    app = Dash(__name__)

    visual_data = session.query(
        FactJobPost.job_level,
        DimSource.name,
        FactJobPost.salary_min,
        FactJobPost.salary_max
    ).join(DimSource).filter(FactJobPost.salary_max != 0)

    query = session.query(DimSource)
    results = query.all()

    source_list = [source.name for source in results]
    df = pd.DataFrame(visual_data, columns=['level', 'source', 'salary_min', 'salary_max'])
    level_list = df['level'].unique()

    app.layout = html.Div([
        html.H4("Salary Analysis"),
        html.P("job-level:"),
        dcc.Checklist(
            id='job-level', 
            options=[{'label': l, 'value': l} for l in level_list],
            value=[level_list[0]], 
            inline=True
        ),
        html.P("source:"),
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
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Box Plot", "Histogram"))

        filtered_data = df[
            (df['level'].isin(selected_job_level)) & 
            (df['source'].isin(selected_source))
        ]
        for i, level in enumerate(filtered_data['level'].unique()):
            level_data = filtered_data[filtered_data['level'] == level]

            fig.add_trace(go.Box(
                y=level_data['salary_max'],
                x=[level]*len(level_data),
                name=level,
                marker_color=colors[i % len(colors)]
            ), row=1, col=1)

        fig.add_trace(go.Histogram(
            x=filtered_data['salary_max'],
            name='Overall Distribution',
            opacity=0.5,
            marker_color='gray'
        ), row=1, col=2) 

        fig.update_layout(
            yaxis_title='Salary',
            boxmode='group',
            bargap=0.1,
            bargroupgap=0.1,
            showlegend=False
        )
    
        return fig

    return app

def generate_wordcloud(data, column_name):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(data.values))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    return f'data:image/png;base64,{image_base64}'

def visual_word_cloud():
    app = Dash(__name__)

    # Query to count skills
    skill_counts = session.query(
        DimSkill.name,
        func.count(DimSkillList.skill_id).label('count')
    ).join(DimSkillList, DimSkill.skill_id == DimSkillList.skill_id) \
    .group_by(DimSkill.name) \
    .order_by(func.count(DimSkillList.skill_id).desc()) \
    .all()

    # Convert to DataFrame
    skill_df = pd.DataFrame(skill_counts, columns=['skill', 'count'])

    # Query to count job roles
    job_role_counts = session.query(
        DimJobRole.name,
        func.count(DimJobRole.job_role_id).label('count')
    ).group_by(DimJobRole.name) \
    .order_by(func.count(DimJobRole.job_role_id).desc()) \
    .all()

    # Convert to DataFrame
    job_role_df = pd.DataFrame(job_role_counts, columns=['job_role', 'count'])

    # Generate word clouds
    skill_wordcloud_image = generate_wordcloud(skill_df, 'skill')
    job_role_wordcloud_image = generate_wordcloud(job_role_df, 'job_role')

    # Create Dash app
    app = Dash(__name__)

    # Layout of the Dash app
    app.layout = html.Div([
        html.H1("Word Clouds for Skills and Job Roles"),
        html.Div([
            html.H2("Skill Word Cloud"),
            html.Img(src=skill_wordcloud_image)
        ]),
        html.Div([
            html.H2("Job Role Word Cloud"),
            html.Img(src=job_role_wordcloud_image)
        ])
    ])

    return app