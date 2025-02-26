import logging

from openai import OpenAI

from .settings import settings


def summarise_commits(
    commit_text: str, client=OpenAI(api_key=settings.openai_api_key)
) -> str:
    """
    Query an OpenAI model to summarise the essential points from commit logs.
    """
    client.api_key = settings.openai_api_key
    try:
        response = client.chat.completions.create(
            model=settings.model_used,
            messages=[
                {"role": "system", "content": settings.system_prompt},
                {
                    "role": "user",
                    "content": settings.user_prompt.format(commit_text=commit_text),
                },
            ],
            temperature=0.5,
            max_tokens=500,
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        logging.error(f"Failed to summarise commit logs: {e}")
        return "Summary unavailable."
