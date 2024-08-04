import sys,os
from load_datn.models import create_database_structure
from load_datn.load import (
    upsert_data,
    combine_data,
)
from visual_datn.Descriptive import (
    visual_yoe,
    test,
    visual_salary_analysis,
    visual_word_cloud,
    visual_map,
    visual_salary_distribution,
)
from visual_datn.Diagnostic import (
    visual_exp_salary,
    visual_com_size_salary
)

from visual_datn.Predictive import (
    visual_skill_demand,
    # visual_job_role_popularity,
    visual_skill_demand_forecast
)

from crawler_datn.ITJobs_url_crawler import (
    crawl_ITjobs
)
from crawler_datn.ITjobs_post_crawler import (
    crawl_ITjobs_post
)
from crawler_datn.TopCV_url_crawler import (
    crawl_TopCV_url
)
from crawler_datn.TopCV_post_crawler import (
    crawl_TopCV_post
)
from transform_datn.final_transform import (
    transform_ITjobs,
    transform_TopCV,
    transform_ITViec,
    transform_TopDev
)
from visual_datn.Prescriptive import (
    visual_critical_skills,
    visual_job_roles_by_skill
)
from crawler_datn.ITjobs_update_status import update_ITjobs_status
from crawler_datn.TopCV_update_status import update_TopCV_status

sys.path.append(os.getcwd())


if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('visual_'):
            app = globals()[sys.argv[1]]()
            app.run_server(debug=True)
        else:
            globals()[sys.argv[1]]()
    else:
        pass