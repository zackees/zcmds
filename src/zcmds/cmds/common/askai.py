import argparse
import json
import os
import sys

import openai
from appdirs import user_config_dir  # type: ignore


def get_config_path() -> str:
    env_path = user_config_dir("zcmds", "zcmds", roaming=True)
    config_file = os.path.join(env_path, "askai.json")
    return config_file


def save_config(config: dict) -> None:
    config_file = get_config_path()
    # make all subdirs of config_file
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(config, f)


def create_or_load_config() -> dict:
    config_file = get_config_path()
    try:
        with open(config_file) as f:
            config = json.loads(f.read())
        return config
    except OSError:
        save_config({})
        return {}


MODELS = {"code": "text-davinci-003"}


def main() -> int:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument("prompt", help="Prompt to ask OpenAI", nargs="?")
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--mode", default="code", choices=MODELS.keys())
    # max tokens
    argparser.add_argument("--max-tokens", help="Max tokens to return", type=int, default=600)
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
    prompt = args.prompt or input("Prompt: ")
    # wow this makes all the difference with this ai
    stop = '"""'
    prompt += f"\n{stop}\nHere's my response:\n"
    openai.api_key = key
    print("\n############ BEGIN PROMPT OpenAI")
    print(prompt)
    print("############ END PROMPT")
    response = openai.Completion.create(
        model=MODELS[args.mode],
        prompt=prompt,
        temperature=0.7,
        max_tokens=args.max_tokens,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0,
        stop=[stop],
    )
    # print(response)
    if response is None or not response.choices:
        print("No error response recieved from from OpenAI, response was:")
        print(response)
        return 1
    # print(response)
    for choice in response.choices:
        print("\n############ BEGIN RESPONSE OpenAI")
        print(choice.text)
        if choice.finish_reason != "stop":
            print(
                "Warning: Weird response from OpenAI - choice.finish_reason: "
                + choice.finish_reason
            )
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
