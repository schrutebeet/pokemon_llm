from pathlib import Path
import yaml

class Config:

    def __init__(self):
        self.__config_file_path = Path(__file__).parent.parent.parent / 'config.yml'
        self.__config_data = self._load_config(self.__config_file_path)
    
    @staticmethod
    def _load_config(config_data_path: Path):
        with open(config_data_path, 'r') as file:
            return yaml.safe_load(file)
        
    def get(self, key: str):
        return self.__config_data.get(key)
