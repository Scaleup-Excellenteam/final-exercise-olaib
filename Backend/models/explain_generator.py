import json
import os

import openai
import asyncio
from typing import IO
from functools import wraps
from .pptx_parser import save_content_to_json_file
from config import explainer_log as log, OPEN_AI_MODEL, ROLE, JSON_FILE_EXTENSION, \
    GENERATION_TIMEOUT, RATE_LIMIT_SECONDS, WAIT_TIME, RATE_LIMIT_MSG, ERROR_OCCURRED_MESSAGE, app


def handle_errors(func: callable) -> callable:
    """Decorator that handles exceptions in a function and logs them.
    :param func: the function to decorate.
    :return: a decorator that handles exceptions in a function and logs them.
    """

    @wraps(func)
    async def wrapper(*args: list, **kwargs: dict) -> None:
        try:
            return await func(*args, **kwargs)
        # RateLimitError handle
        except openai.error.RateLimitError:
            log.error(RATE_LIMIT_MSG)
            print(RATE_LIMIT_MSG)
            await asyncio.sleep(WAIT_TIME)
            return RATE_LIMIT_MSG
        except Exception as e:
            slide_number = args[0]
            log.error(f"{ERROR_OCCURRED_MESSAGE} slide #{slide_number}:- {str(e)}")

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
    log.info(f"send prompt to openai: {prompt}")

    response = openai.ChatCompletion.create(
        model=OPEN_AI_MODEL,
        # make it more good at explaining
        messages=[{"role": ROLE,
                   "content": f"I need an explanation based on a slide presentation. Here are the key points of the presentation - \
                   slide number: {str(slide_number)}, slide text: " + prompt}],
    )
    explanation = response.choices[0].message.content
    log.info(f"Got response from OpenAI: {explanation}")
    return explanation


def extract_explanations(slides_explanation: list, res: tuple|list) -> None:
    for slide_number, api_slide_explanation in enumerate(res, start=1):
        if api_slide_explanation == "":
            log.info(f"Skipping slide {slide_number} because it's empty")
            continue
        else:
            slides_explanation.append({"slide_number": slide_number, "explanation": api_slide_explanation})
            log.info(f"Slide {slide_number} explanation: {api_slide_explanation}")


async def get_pptx_slides_explanations(file: IO, slides: list | tuple) -> list:
    """Generates explanations for all slides in a presentation.
    :param slides: a list of dictionaries containing the slide number and its text.
    :param file: json file
    :return: a list of dictionaries containing the slide number and its explanation.
    output example: [{"slide_number": 1, "explanation": "This is a slide about asyncio."}, ...]
    """
    slides_explanation = []
    tasks = []
    for slide_number, slide_text in enumerate(slides, start=1):
        log.info(f"Generating explanation for slide {slide_number}")
        if slide_text == "":
            log.info(f"Skipping slide {slide_number} because it's empty")
            continue
        task = asyncio.create_task(
            generate_slide_explanation_from_openai(slide_number=slide_number, prompt=slide_text))
        tasks.append(task)
        await asyncio.sleep(RATE_LIMIT_SECONDS)

    res = await asyncio.gather(*tasks)  # wait for all tasks to finish
    log.info(f"Got {len(res)} explanations from OpenAI")
    extract_explanations(slides_explanation, res)

    return slides_explanation


def read_pptx_slides_form_json_file_as_json(file, filename: str) -> list:
    """Reads a json file containing a list of slides and returns it as a list.
    :param file: json file to read from
    :param filename: name of the file to save the explanations to
    :return: a list of slides
    """
    log.info(f"Reading slides from {filename}")
    slides = []
    with open(file, 'r') as f:
        json_data = json.load(f)
        slides = list(json_data.values())
    log.info(f"Read {len(slides)} slides from {filename}\
    slides: {slides}")
    return slides


async def slides_explanations_generator(file, filename: str) -> None:
    """Generates explanations for all slides in a presentation and saves them to a json file.
    :param filename - name of the file to save the explanations to
    :param file - json file to read from
    """
    slides_text = read_pptx_slides_form_json_file_as_json(file, filename)
    log.info(f"Starting to generate explanations for {len(slides_text)} slides...")
    slides_explanation = await get_pptx_slides_explanations(file, slides=slides_text)
    log.info(f"saving explanations to {filename}")
    output_filepath = os.path.join(app.config['OUTPUT_FOLDER'])
    save_content_to_json_file(slides_explanation, output_filepath, filename)
    log.info(f"Explanations saved successfully to explanations...")
