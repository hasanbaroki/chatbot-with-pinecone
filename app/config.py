from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    index_name: str = "chatbot-longterm"
    model: str = "gpt-4o-mini"
    port: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()
