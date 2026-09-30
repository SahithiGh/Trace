from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'TRACE Product Intelligence API'
    environment: str = 'development'
    database_url: str = 'postgresql+asyncpg://trace:trace@localhost:5432/trace'
    hindsight_base_url: str = 'https://api.hindsight.vectorize.io'
    hindsight_api_key: str = ''
    hindsight_bank_id: str = 'trace-demo'
    llm_api_key: str = ''
    llm_base_url: str = ''
    llm_model: str = ''
    cors_origins: str = 'http://localhost:5173'
    log_level: str = 'INFO'
    request_max_bytes: int = 2_000_000
    api_key: str = Field(default='', validation_alias='TRACE_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

settings = Settings()
