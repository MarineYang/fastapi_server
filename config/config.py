import os
import sys
from config.config_loader import Configs
from config.config_models import DataBaseConfig, WebServerConfig, JwtToken


config_file = f"config.local.toml"
configs = Configs(config_file)

web_server_config = configs.get(WebServerConfig)
db_config = configs.get(DataBaseConfig)
jwt_config = configs.get(JwtToken)