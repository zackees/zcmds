"""askai - ask openai for help"""


# pylint: disable=all
# mypy: ignore-errors

import argparse
import atexit
import os
import subprocess
import sys
from tempfile import NamedTemporaryFile
from typing import Optional

import colorama

try:
    import openai
    from openai.error import AuthenticationError, ServiceUnavailableError
except KeyboardInterrupt:
    sys.exit(1)

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config
from zcmds.util.prompt_input import prompt_input

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_AI_ASSISTANT = (
    "You are a helpful assistant to a senior programmer. "
    "If I am asking how to do something in general then go ahead "
    "and recommend popular third-party apps that can get the job done, "
    "but don't recommend additional tools when I'm currently asking how to do use "
    "a specific tool."
)

colorama.init()


def output(text: str, outfile: Optional[str]):
    if outfile:
        with open(outfile, "a") as f:
            f.write(text)
    else:
        with NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as f:
            f.write(text)
            f.flush()
        atexit.register(lambda: os.remove(f.name))
        subprocess.call(["consolemd", f.name], universal_newlines=True)


def ai_query(prompts: list[str], max_tokens: int, model: str) -> openai.ChatCompletion:
    # assert prompts is odd
    assert (
        len(prompts) % 2 == 1
    )  # Prompts alternate between user message and last response
    messages = [
        {
            "role": "system",
            "content": DEFAULT_AI_ASSISTANT,
        },
    ]
    for i, prompt in enumerate(prompts):
        if i % 2 == 0:
            messages.append({"role": "assistant", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0,
    )
    return response


def cli() -> int:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument("prompt", help="Prompt to ask OpenAI", nargs="?")
    argparser.add_argument("--json", help="Print response as json", action="store_true")
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--output", help="Output file")
    argparser.add_argument("--model", default=DEFAULT_MODEL)
    argparser.add_argument("--verbose", action="store_true", default=False)
    # max tokens
    argparser.add_argument(
        "--max-tokens", help="Max tokens to return", type=int, default=600
    )
    args = argparser.parse_args()
    config = create_or_load_config()
    if args.set_key:
        config["openai_key"] = args.set_key
        save_config(config)
    elif "openai_key" not in config:
        key = input("No OpenAi key found, please enter one now: ")
        config["openai_key"] = key
        save_config(config)
    key = config["openai_key"]
    interactive = not args.prompt
    if interactive:
        print(
            "\nInteractive mode - press return three times to submit your code to OpenAI"
        )
    prompt = args.prompt or prompt_input()

    as_json = args.json

    openai.api_key = key

    def log(*pargs, **kwargs):
        if not args.verbose:
            return
        print(*pargs, **kwargs)

    log(prompt)
    prompts = [prompt]

    while True:
        # allow exit() and exit to exit the app
        if prompts[-1].strip().replace("()", "") == "exit":
            print("Exited due to 'exit' command")
            break
        if not as_json:
            print("############ OPEN-AI QUERY")
        try:
            response = ai_query(
                prompts=prompts, max_tokens=args.max_tokens, model=args.model
            )
        except ServiceUnavailableError as sua:
            print(sua)
            return 1
        except AuthenticationError as e:
            print(
                "Error authenticating with OpenAI, deleting password from config and exiting."
            )
            print(e)
            save_config({})
            return 1
        if as_json:
            print(response)
            return 0
        # print(response)
        if response is None or not response.choices:
            print("No error response recieved from from OpenAI, response was:")
            output(response, args.output)
            return 1
        # print(response)
        for choice in response.choices:
            if not args.output:
                print("############ OPEN-AI RESPONSE\n")
            last_response = choice["message"]["content"]
            output(last_response, args.output)
            prompts.append(last_response)
            break
        else:
            print("No response from OpenAI, response was:")
            output(response, args.output)
            return 1
        if not interactive:
            break
        prompts.append(prompt_input())
    return 0


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1
    except openai.error.RateLimitError:
        print("Rate limit exceeded, set a new key with --set-key")
        return 1


if __name__ == "__main__":
    sys.exit(main())
