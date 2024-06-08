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

def test():
    correction = {'Cần Thơn': 'Cần Thơ', 'An Giang': 'An Giang', 'Bắc Ninh': 'Bắc Ninh', 'Lạng Sơn': 'Lạng Sơn', 'Khánh Hòa': 'Khánh Hòa', 'Phú Yên': 'Phú Yên', 'Hà Tĩnh': 'Hà Tĩnh', 'Bình Dương': 'Bình Dương', 'Phú Thọ': 'Phú Thọ', 'Vĩnh Long': 'Vĩnh Long', 'Đồng Nai': 'Đồng Nai', 'Hải Dương': 'Hải Dương', 'Tuyên Quang': 'Tuyên Quang', 'Tây Ninh': 'Tây Ninh', 'Gia Lai': 'Gia Lai', 'Yên Bái': 'Yên Bái', 'Đà Nẵng': 'Đà Nẵng', 'Thái Bình': 'Thái Bình', 'Thừa Thiên Huế': 'Thừa Thiên Huế', 'Hưng Yên': 'Hưng Yên', 'Đồng Tháp': 'Đồng Tháp', 'TP. Hồ Chí Minh': 'Hồ Chí Minh', 'Bình Định': 'Bình Định', 'Lào Cai': 'Lào Cai', 'Quảng Ngãi': 'Quảng Ngãi', 'Sóc Trăng': 'Sóc Trăng', 'Nghệ An': 'Nghệ An', 'Bình Thuận': 'Bình Thuận', 'Thái Nguyên': 'Thái Nguyên', 'Bắc Kạn': 'Bắc Kạn', 'Kien Giang': 'Kiên Giang', 'Kon Tum': 'Kon Tum', 'Bình Phước': 'Bình Phước', 'Đăk Nông': 'Đắk Nông', 'Bạc Liêu': 'Bạc Liêu', 'Quản Bình': 'Quảng Bình', 'Hà Nam': 'Hà Nam', 'Trà Vinh': 'Trà Vinh', 'Quảng Ninh': 'Quảng Ninh', 'Cà Mau': 'Cà Mau', 'Tiền Giang': 'Tiền Giang', 'Đăk Lăk': 'Đắk Lắk', 'Cao Bằng': 'Cao Bằng', 'Hải Phòng': 'Hải Phòng', 'Bắc Giang': 'Bắc Giang', 'Quảng Trị': 'Quảng Trị', 'Hòa Bình': 'Hòa Bình', 'Lâm Đồng': 'Lâm Đồng', 'Lai Châu': 'Lai Châu', 'Thanh Hóa': 'Thanh Hóa', 'Bà Rịa -Vũng Tàu': 'Bà Rịa - Vũng Tàu', 'Ninh Bình': 'Ninh Bình', 'Ninh Thuận': 'Ninh Thuận', 'Vĩnh Phúc': 'Vĩnh Phúc', 'Hà Giang': 'Hà Giang', 'Bến Tre': 'Bến Tre', 'Long An': 'Long An', 'Nam Định': 'Nam Định', 'Sơn La': 'Sơn La', 'Quảng Nam': 'Quảng Nam', 'Hậu Giang': 'Hậu Giang', 'Điện Biên': 'Điện Biên', 'Hà Nội': 'Hà Nội'}
    job_post_region_counts = session.query(
        DimPosition.region,
        func.count(DimPosition.region).label('count')
    ).join(FactJobPost, FactJobPost.position_id == DimPosition.position_id) \
    .group_by(DimPosition.region) \
    .order_by(func.count(DimPosition.region).desc()) \
    .all()
    job_post_region = {}
    for region in job_post_region_counts:
        job_post_region[region[0]] = region[1]
    # print(job_post_region_counts)
    job_post_city_counts = session.query(
        DimPosition.city,
        func.count(DimPosition.city).label('count')
    ).join(FactJobPost, FactJobPost.position_id == DimPosition.position_id) \
    .group_by(DimPosition.city) \
    .order_by(func.count(DimPosition.city).desc()) \
    .all()
    job_post_city_df = pd.DataFrame(list(job_post_city_counts), columns=['city', 'count'])
    print(job_post_city_counts)
    # job_post_city = {}
    # for city in job_post_city_counts:
    #     job_post_city[city[0]] = city[1]

    # with open('./visual_datn/vn-projected.json') as f:
    #     geo = json.load(f)
    
    # for feature in geo['features']:
    #     name = feature['properties']['ten_tinh']
    #     if name in correction:
    #         # correct province's name if needed
    #         feature['properties']['ten_tinh'] = correction[name]
    #         name = correction[name]
        
    #     # add density property and remove unused others
    #     feature['properties']['job_post_city'] = job_post_city.get(name, 0)
    #     del feature['properties']['gid']
    #     del feature['properties']['code']

    # fig = px.choropleth_mapbox(
    #     job_post_city_df,
    #     geojson=geo,
    #     locations='province',
    #     featureidkey="properties.ten_tinh",
    #     color='job_post_city',
    #     color_continuous_scale="Viridis",
    #     mapbox_style="carto-positron",
    #     zoom=4,
    #     center={"lat": 14.0583, "lon": 108.2772},
    #     opacity=0.5,
    #     labels={'job_post_city': 'job_post_city'}
    # )

    # fig.update_geos(fitbounds="locations", visible=False)

    # # Create a Dash app
    # app = Dash(__name__)

    # app.layout = html.Div([
    #     html.H1("Vietnam Provincial Map Chart"),
    #     dcc.Graph(id='map-chart', figure=fig)
    # ])

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

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


    df['z_score'] = stats.zscore(df['yoe'])
    # Define threshold (commonly set to 3)
    threshold = 3
    # Filter out outliers
    df = df[(df['z_score'].abs() <= threshold)]
    # Drop the 'z_score' column as it's no longer needed
    df = df.drop(columns=['z_score'])


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




    df['z_score'] = stats.zscore(df['salary_max'])
    # Define threshold (commonly set to 3)
    threshold = 3
    # Filter out outliers
    df = df[(df['z_score'].abs() <= threshold)]
    # Drop the 'z_score' column as it's no longer needed
    df = df.drop(columns=['z_score'])




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

    skill_df = pd.DataFrame(skill_counts, columns=['skill', 'count'])

    job_role_counts = session.query(
        DimJobRole.name,
        func.count(DimJobRole.job_role_id).label('count')
    ).group_by(DimJobRole.name) \
    .order_by(func.count(DimJobRole.job_role_id).desc()) \
    .all()

    job_role_df = pd.DataFrame(job_role_counts, columns=['job_role', 'count'])

    skill_wordcloud_image = generate_wordcloud(skill_df, 'skill')
    job_role_wordcloud_image = generate_wordcloud(job_role_df, 'job_role')

    app = Dash(__name__)

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

def scale_coordinates(coordinates, scale_factor=1):
    return [(x * scale_factor, y * scale_factor) for x, y in coordinates]

def read_svg(svg_file):
    with open(svg_file, 'rb') as f:
        svg_data = f.read()
    svg_base64 = base64.b64encode(svg_data).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

def sqrt_scale(value, min_value, max_value):
    norm_value = (value - min_value) / (max_value - min_value)
    sqrt_value = np.sqrt(norm_value)
    return sqrt_value

def get_color(density, thresholds, colors):
    for i, threshold in enumerate(thresholds):
        if density <= threshold:
            return colors[i]
    return colors[-1]

def visual_map():
    correction = {
        'Cần Thơn': 'Cần Thơ', 'An Giang': 'An Giang', 'Bắc Ninh': 'Bắc Ninh', 'Lạng Sơn': 'Lạng Sơn', 
        'Khánh Hòa': 'Khánh Hòa', 'Phú Yên': 'Phú Yên', 'Hà Tĩnh': 'Hà Tĩnh', 'Bình Dương': 'Bình Dương', 
        'Phú Thọ': 'Phú Thọ', 'Vĩnh Long': 'Vĩnh Long', 'Đồng Nai': 'Đồng Nai', 'Hải Dương': 'Hải Dương', 
        'Tuyên Quang': 'Tuyên Quang', 'Tây Ninh': 'Tây Ninh', 'Gia Lai': 'Gia Lai', 'Yên Bái': 'Yên Bái', 
        'Đà Nẵng': 'Đà Nẵng', 'Thái Bình': 'Thái Bình', 'Thừa Thiên Huế': 'Thừa Thiên Huế', 'Hưng Yên': 'Hưng Yên', 
        'Đồng Tháp': 'Đồng Tháp', 'TP. Hồ Chí Minh': 'Hồ Chí Minh', 'Bình Định': 'Bình Định', 'Lào Cai': 'Lào Cai', 
        'Quảng Ngãi': 'Quảng Ngãi', 'Sóc Trăng': 'Sóc Trăng', 'Nghệ An': 'Nghệ An', 'Bình Thuận': 'Bình Thuận', 
        'Thái Nguyên': 'Thái Nguyên', 'Bắc Kạn': 'Bắc Kạn', 'Kien Giang': 'Kiên Giang', 'Kon Tum': 'Kon Tum', 
        'Bình Phước': 'Bình Phước', 'Đăk Nông': 'Đắk Nông', 'Bạc Liêu': 'Bạc Liêu', 'Quản Bình': 'Quảng Bình', 
        'Hà Nam': 'Hà Nam', 'Trà Vinh': 'Trà Vinh', 'Quảng Ninh': 'Quảng Ninh', 'Cà Mau': 'Cà Mau', 'Tiền Giang': 'Tiền Giang', 
        'Đăk Lăk': 'Đắk Lắk', 'Cao Bằng': 'Cao Bằng', 'Hải Phòng': 'Hải Phòng', 'Bắc Giang': 'Bắc Giang', 
        'Quảng Trị': 'Quảng Trị', 'Hòa Bình': 'Hòa Bình', 'Lâm Đồng': 'Lâm Đồng', 'Lai Châu': 'Lai Châu', 
        'Thanh Hóa': 'Thanh Hóa', 'Bà Rịa -Vũng Tàu': 'Bà Rịa - Vũng Tàu', 'Ninh Bình': 'Ninh Bình', 
        'Ninh Thuận': 'Ninh Thuận', 'Vĩnh Phúc': 'Vĩnh Phúc', 'Hà Giang': 'Hà Giang', 'Bến Tre': 'Bến Tre', 
        'Long An': 'Long An', 'Nam Định': 'Nam Định', 'Sơn La': 'Sơn La', 'Quảng Nam': 'Quảng Nam', 
        'Hậu Giang': 'Hậu Giang', 'Điện Biên': 'Điện Biên', 'Hà Nội': 'Hà Nội'
    }

    # Fetch data from the database
    job_post_city_counts = session.query(
        DimPosition.city,
        func.count(DimPosition.city).label('count')
    ).join(FactJobPost, FactJobPost.position_id == DimPosition.position_id) \
    .group_by(DimPosition.city) \
    .order_by(func.count(DimPosition.city).desc()) \
    .all()

    # Create a DataFrame from the query results
    job_post_city_df = pd.DataFrame(list(job_post_city_counts), columns=['city', 'count'])

    # Create a dictionary for quick lookups
    job_post_city = {city[0]: city[1] for city in job_post_city_counts}

    # Load the GeoJSON data
    with open('./visual_datn/vn-projected.json', 'r', encoding='utf-8') as f:
        geo = json.load(f)

    # Process the GeoJSON data
    for feature in geo['features']:
        name = feature['properties']['ten_tinh']
        if name in correction:
            feature['properties']['ten_tinh'] = correction[name]
            name = correction[name]
        
        feature['properties']['job_post_city'] = job_post_city.get(name, 0)
        del feature['properties']['gid']
        del feature['properties']['code']

    features = geo.get('features', [])

    # Define the thresholds and corresponding colors
    thresholds = [100, 500, 1000, 2000, 4000]
    colors = ['#d4eeff', '#89c2d9', '#4682b4', '#2b6cb0', '#0f4c81', '#08306b']  # Example colors

    for feature in features:
        density = feature['properties'].get('job_post_city', 0)
        color = get_color(density, thresholds, colors)
        feature['properties']['fill'] = color

    svg_file = 'vn-color.svg'
    dwg = svgwrite.Drawing(svg_file, profile='tiny', size=(800, 800))

    # Function to draw polygons and multipolygons
    def draw_polygon(polygon, fill_color):
        points = scale_coordinates(polygon[0])  # Assuming exterior ring only
        dwg.add(dwg.polygon(points, fill=fill_color))

    def draw_multipolygon(multipolygon, fill_color):
        for polygon in multipolygon:
            points = scale_coordinates(polygon[0])  # Assuming exterior ring only
            dwg.add(dwg.polygon(points, fill=fill_color))

    # Draw the features with their assigned colors
    for feature in features:
        properties = feature['properties']
        coordinates = feature['geometry']['coordinates']
        fill_color = properties.get('fill', '#000000')

        if feature['geometry']['type'] == 'Polygon':
            draw_polygon(coordinates, fill_color)
        elif feature['geometry']['type'] == 'MultiPolygon':
            draw_multipolygon(coordinates, fill_color)

    # Save the SVG file
    dwg.save()

    app = Dash(__name__)

    # Read and encode the SVG file
    svg_base64 = read_svg(svg_file)

    # Define the app layout
    app.layout = html.Div([
        html.H1("Vietnam Provincial Map (SVG)"),
        html.Img(src=svg_base64, style={'width': '100%', 'height': 'auto'})
    ])

    return app

def visual_salary_distribution():
    app = Dash(__name__)

    # Query the data
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

        # Create swarm plot using scatter plot with jitter
        fig = go.Figure()

        for level in filtered_data['level'].unique():
            level_data = filtered_data[filtered_data['level'] == level]
            
            # Adding jitter to the x-values
            jittered_x = level_data['source'] + np.random.uniform(-0.1, 0.1, size=len(level_data))

            fig.add_trace(go.Scatter(
                x=jittered_x,
                y=level_data['salary_max'],
                mode='markers',
                name=level,
                marker=dict(size=10, line=dict(width=1), opacity=0.8)
            ))

        fig.update_layout(
            title='Salary Distribution by Job Level and Source',
            xaxis_title='Source',
            yaxis_title='Salary Max',
            showlegend=True
        )

        return fig

    return app