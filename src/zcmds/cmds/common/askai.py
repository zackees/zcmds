"""askai - ask openai for help"""


# pylint: disable=all
# mypy: ignore-errors

import argparse
import atexit
import os
import subprocess
import sys
import warnings
from tempfile import NamedTemporaryFile
from typing import Optional

import colorama
import json5 as json
import tiktoken

try:
    import openai
    from openai import APIConnectionError, AuthenticationError, OpenAI

except KeyboardInterrupt:
    sys.exit(1)

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config
from zcmds.util.prompt_input import prompt_input

MAX_TOKENS = 4096
HIDDEN_PROMPT_TOKEN_COUNT = 100  # this hack corrects for the unnaccounted for tokens in the prompt
ADVANCED_MODEL = "gpt-4-1106-preview"
DEFAULT_MODEL = "gpt-4"
SLOW_MODEL = "gpt-4"
FAST_MODEL = "gpt-3.5-turbo"
DEFAULT_AI_ASSISTANT = (
    "You are a helpful assistant to a senior programmer. "
    "If I am asking how to do something in general then go ahead "
    "and recommend popular third-party apps that can get the job done, "
    "but don't recommend additional tools when I'm currently asking how to do use "
    "a specific tool."
)

colorama.init()

client = None


def count_tokens(model: str, text: str):
    # Ensure you have the right model, for example, "gpt-3.5-turbo"
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


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
    global client
    # assert prompts is odd
    assert len(prompts) % 2 == 1  # Prompts alternate between user message and last response
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

    if client is None:
        config = create_or_load_config()
        key = config["openai_key"]
        client = OpenAI(api_key=key)

    # compute the max_tokens by counting the tokens in the prompt
    # and subtracting that from the max_tokens
    messages_json_str = json.dumps(messages)
    prompt_tokens = count_tokens(model, messages_json_str)
    max_tokens = max_tokens - prompt_tokens - HIDDEN_PROMPT_TOKEN_COUNT
    response = client.chat.completions.create(
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

    model_group = argparser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--fast", action="store_true", default=False, help=f"chat gpt 3 turbo: {FAST_MODEL}"
    )
    model_group.add_argument(
        "--slow", action="store_true", default=False, help=f"chat gpt 4: {SLOW_MODEL}"
    )
    model_group.add_argument(
        "--advanced",
        action="store_true",
        default=False,
        help=f"bleeding edge model: {ADVANCED_MODEL}",
    )
    model_group.add_argument("--model", default=None)
    argparser.add_argument("--verbose", action="store_true", default=False)
    # max tokens
    argparser.add_argument("--max-tokens", help="Max tokens to return", type=int, default=None)
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
        print("\nInteractive mode - press return three times to submit your code to OpenAI")
    prompt = args.prompt or prompt_input()
    max_tokens = args.max_tokens

    as_json = args.json

    def log(*pargs, **kwargs):
        if not args.verbose:
            return
        print(*pargs, **kwargs)

    log(prompt)
    prompts = [prompt]
    if args.fast:
        warnings.warn("--fast is deprecated, fast assumed by default unless --slow")
    if args.model is None:
        if args.slow:
            model = SLOW_MODEL
            if max_tokens is None:
                max_tokens = 4096
        elif args.advanced:
            model = ADVANCED_MODEL
            max_tokens = 128000
        else:
            model = FAST_MODEL
            max_tokens = 4096
    else:
        model = args.model

    while True:
        # allow exit() and exit to exit the app
        if prompts[-1].strip().replace("()", "") == "exit":
            print("Exited due to 'exit' command")
            break
        if not as_json:
            print("############ OPEN-AI QUERY")
        try:
            response = ai_query(prompts=prompts, max_tokens=max_tokens, model=model)
        except APIConnectionError as err:
            print(err)
            return 1
        except AuthenticationError as e:
            print("Error authenticating with OpenAI, deleting password from config and exiting.")
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
            last_response = choice.message.content
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
    except openai.RateLimitError:
        print("Rate limit exceeded, set a new key with --set-key")
        return 1


if __name__ == "__main__":
    # sys.argv.append("write binary search in python")
    sys.exit(main())
