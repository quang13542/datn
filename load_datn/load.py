import pandas as pd
from datetime import datetime

from load_datn.models import (
    DimCompany,
    DimDate,
    DimJobRole,
    DimPosition,
    DimSkill,
    DimSkillList,
    DimSource,
    FactJobPost
)

def test_company():
    df = pd.read_csv('./load_datn/transformed_ITjobs.csv', header=0)

    company_list = df[['company_name', 'company_size']].value_counts().index.values

    print(len(company_list))
    for x in company_list:
        for y in company_list:
            if x!=y:
                if x[0]==y[0]:
                    print(x, y)

def combine_data():
    df1 = pd.read_csv('./load_datn/transformed_ITjobs.csv')
    df2 = pd.read_csv('./load_datn/transformed_ITViec.csv')
    df3 = pd.read_csv('./load_datn/transformed_TopCV.csv')
    df4 = pd.read_csv('./load_datn/transformed_TopDev.csv')

    combined_df = pd.concat([df1, df2, df3, df4], axis=0, ignore_index=True)

    combined_df.to_csv(f"./load_datn/combined_source/{datetime.today().strftime('%Y_%m_%d')}_combined_data.csv")