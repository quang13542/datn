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
    visual_word_cloud
)

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