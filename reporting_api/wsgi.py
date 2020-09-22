import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from reporting_api.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host='0.0.0.0')
