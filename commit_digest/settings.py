from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    model_used: str = "gpt-4-turbo"
    base_output_dir: str = "commit_reports"
    system_prompt: str = (
        "You are an expert software engineer and technical communicator. "
        "Your task is to analyse a series of git commit logs "
        "and generate a clear, concise, and insightful summary. "
        "Focus on extracting the major changes, key improvements, "
        "and any recurring themes. "
        "If multiple repositories or dates are included, group the insights "
        "accordingly. Avoid unnecessary low-level details, "
        "and ensure the summary is actionable for both technical and business "
        "audiences."
    )
    user_prompt: str = (
        "Please summarise the following commit logs:\n\n{commit_text}\n\n"
        "The summary should include an overall overview and a bullet-point "
        "list of key changes, highlighting new features, bug fixes, "
        "refactorings, and any breaking changes."
    )

    class Config:
        env_file = ".env"


settings = Settings()
