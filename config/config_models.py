from config.config_loader import ConfigModel

class WebServerConfig(ConfigModel):
    server_name: str = ""
    host: str = ""
    port: int = 0
    is_web_server: bool = False
    is_ssl: bool = False

class JwtToken(ConfigModel):
    access_key: str = ""
    refresh_key: str = ""
    access_expire_min: int = 0
    refresh_expire_day: int = 0
    check_duplicate: bool = True

class DataBaseConfig(ConfigModel):
    db_host: str = ""
    db_port: str = ""
    db_name: str = ""
    db_username: str = ""
    db_password: str = ""
    