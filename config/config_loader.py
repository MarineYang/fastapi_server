import tomli as tomllib
from typing import Optional, Type, Dict, TypeVar
from pydantic import BaseModel

class ConfigModel(BaseModel):
    pass

#APP_ENV 
#local : 로컬 환경(개인 pc)
#dev : 개발환경 (사내 pc)
#staging : 스테이징 환경(출시(프로덕션)전 환경, 클라우드 서버)
#prod : 서비스 환경 ( 클라우드 서버 ) 

#실행시 환경변수 설정
#linux : export APP_ENV=dev
#window : set APP_ENV=dev

class Configs:
    ConfigType = TypeVar('ConfigType', bound=ConfigModel)
    
    def __init__(self, file_path: str):
        self._settings: Dict[Type[Configs.ConfigType], Configs.ConfigType] = self._load_settings_from_toml(file_path)

    def _load_settings_from_toml(self, file_path: str) -> Dict[Type[ConfigType], ConfigType]:   
        with open(file_path, "rb") as f:
            try:
                toml_content = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                print(f"TOML 파일 디코딩 오류: {e}")
                toml_content = {}

        config_subclasses = ConfigModel.__subclasses__()
        configs = {
            config_class: config_class.parse_obj(toml_content[config_class.__name__])
            for config_class in config_subclasses
            if config_class.__name__ in toml_content
        }
        return configs

    def get(self, config_class: Type[ConfigType]) -> Optional[ConfigType]:
        return self._settings.get(config_class)
