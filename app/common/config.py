import os
from pyaml_env import parse_config

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(current_dir))
config_path = os.path.join(app_dir, 'config.yaml')

config = parse_config(os.environ.get('API_CONFIG', config_path))