import requests
import logging

from config import SERPER_API_KEY

logging.basicConfig(level=logging.INFO)


def search(query: str) -> str:
    logging.info(f"Ищу в гугле {query}")

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-type": "application/json"},
            json={"q": query},
        )

        if response.status_code in [200, 201]:
            data_json = response.json()
            data = "\n".join(
                f"{item['title']}: {item['snippet']}"
                for item in data_json.get("organic", [])[:3]
            )
            return data

    except Exception as e:
        logging.error(f"Ошибка при поиске: {str(e)}")
        return f"Ошибка при поиске: {str(e)[:5000]}"


response = search("масса земли")
logging.info(response)
