import asyncio
import logging
import os
from asyncio import sleep
from datetime import datetime
from functools import wraps
from open_ai_pressentation_explainer.pptx_processor import PptxProcessor

import openai
from flask.cli import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='info.log')
ROLE = "user"
GENERATION_TIMEOUT = 10  # seconds to wait for a response from OpenAI
PATH = 'sources/asyncio-intro.pptx'
ERROR_OCCURRED_MESSAGE = "An error occurred while processing the presentation:"
LOG_FILE_PATH = 'info.log'
RATE_LIMIT_SECONDS = 1
WAIT_TIME = 60
RATE_LIMIT_MSG = f"Rate limit exceeded. Please wait a {WAIT_TIME} seconds and try again."

load_dotenv()
OPEN_AI_MODEL = os.environ.get('OPEN_AI_MODEL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE_PATH)


def handle_errors(func: callable) -> callable:
    """Decorator that handles exceptions in a function and logs them.
    :param func: the function to decorate.
    :return: a decorator that handles exceptions in a function and logs them.
    """

    @wraps(func)
    async def wrapper(*args: list, **kwargs: dict) -> str:
        try:
            return await func(*args, **kwargs)
        except openai.error.RateLimitError:
            logging.error(RATE_LIMIT_MSG)
            print(RATE_LIMIT_MSG)
            await asyncio.sleep(WAIT_TIME)
            return RATE_LIMIT_MSG
        except Exception as e:
            slide_number = args[0]
            logging.error(f"{ERROR_OCCURRED_MESSAGE} {slide_number}: {e}")
            return f"{ERROR_OCCURRED_MESSAGE} {slide_number}: {e}"

    return wrapper


def timer(sec: int) -> callable:
    """Decorator that limits the execution time of a function to sec seconds.
    :param sec: the number of seconds to limit the execution time to.
    :return: a decorator that limits the execution time of a function to sec seconds.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=sec)

        return wrapper

    return decorator


@handle_errors
@timer(GENERATION_TIMEOUT)
async def generate_slide_explanation_from_openai(slide_number: int, prompt: str) -> str:
    """Generates an explanation for a slide using OpenAI's API.
    :param slide_number: the number of the slide to generate an explanation for.
    :param prompt: the text to use as context for the explanation.
    :return: a dictionary containing the slide number and its explanation.
    output example: {"slide_number": 1, "explanation": "This is a slide about asyncio."}
    """
    logging.info(f"send prompt to openai: {prompt}")

    response = openai.ChatCompletion.create(
        model=OPEN_AI_MODEL,
        messages=[{"role": ROLE, "content": prompt}],
    )
    explanation = response.choices[0].message.content
    logging.info(f"Got response from OpenAI: {explanation}")
    return explanation


def extract_explanations(slides_explanation: list, res: tuple) -> None:
    for slide_number, api_slide_explanation in enumerate(res, start=1):
        if api_slide_explanation == "":
            logging.info(f"Skipping slide {slide_number} because it's empty")
            continue
        else:
            slides_explanation.append({"slide_number": slide_number, "explanation": api_slide_explanation})
            logging.info(f"Slide {slide_number} explanation: {api_slide_explanation}")


async def get_pptx_slides_explanations(pptx_path: str, slides: list) -> list:
    """Generates explanations for all slides in a presentation.
    :param slides: a list of dictionaries containing the slide number and its text.
    :param pptx_path: path to the presentation. must be a .pptx file.
    :return: a list of dictionaries containing the slide number and its explanation.
    output example: [{"slide_number": 1, "explanation": "This is a slide about asyncio."}, ...]
    """
    slides_explanation = []
    tasks = []
    for slide_number, slide_text in enumerate(slides, start=1):
        logging.info(f"Generating explanation for slide {slide_number}")
        if slide_text == "":
            logging.info(f"Skipping slide {slide_number} because it's empty")
            continue
        task = asyncio.create_task(generate_slide_explanation_from_openai(slide_number, slide_text))
        tasks.append(task)
        await asyncio.sleep(RATE_LIMIT_SECONDS)

    res = await asyncio.gather(*tasks)  # wait for all tasks to finish
    extract_explanations(slides_explanation, res)

    return slides_explanation


async def slides_explanations_generator(pptx_path: str, api_key: str) -> None:
    """Generates explanations for all slides in a presentation and saves them to a json file.
    :param pptx_path: path to the presentation. must be a .pptx file.
    :param api_key: OpenAI API key.
    """
    set_api_key(api_key)
    pptx_parser = PptxProcessor(pptx_path)
    slides_text = pptx_parser.get_slides()
    logging.info(f"Starting to generate explanations for {len(slides_text)} slides...")
    slides_explanation = await get_pptx_slides_explanations(pptx_path, slides=slides_text)
    logging.info(f"saving explanations to explanations_{PATH.split('/')[-1]}")
    pptx_parser.save_explanations_as_json(slides_explanation)
    logging.info(f"Explanations saved successfully to explanations...")
    print_explanations(slides_explanation)


def set_api_key(api_key: str) -> None:
    openai.api_key = api_key


def print_explanations(slides_explanations: list) -> None:
    for slide_explanation in slides_explanations:
        print(slide_explanation)


def main():
    asyncio.run(slides_explanations_generator(pptx_path=PATH, api_key=OPEN_AI_API_KEY))


if __name__ == "__main__":
    main()
