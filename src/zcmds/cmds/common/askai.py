"""askai - ask openai for help"""


# pylint: disable=all
# mypy: ignore-errors

import argparse
import sys
import time
from typing import Optional, Tuple

import openai
from openai.error import AuthenticationError

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config

from .inputimeout import TimeoutOccurred, inputimeout


def read_console(prompt: Optional[str] = None, timeout: float = 1.0) -> Tuple[bool, str, float]:
    start_time = time.time()
    end_time = 0.0
    try:
        out = inputimeout(prompt=prompt, timeout=timeout)
        end_time = time.time()
        return (True, out, end_time - start_time)
    except TimeoutOccurred:
        return (False, "", end_time - start_time)


def prompt_input() -> str:
    lines: list[str] = []
    times: list[float] = []
    streaming_mode = False
    while True:
        if streaming_mode:
            ok, line, elapsed = read_console(timeout=0.1)
            if not ok:
                ok, line, elapsed = read_console(prompt=None, timeout=99999)  # wait for input
                lines.append(line)
                times.append(elapsed)
                break  # timed out
            lines.append(line)
            times.append(elapsed)
        else:
            if len(lines) == 0:
                print("input: ", end="")
            start = time.time()
            line = input("")
            times.append(time.time() - start)
            lines.append(line)
        # if the two lines lines were all fast, switch to streaming mode
        if not streaming_mode and len(times) > 2 and all(t < 0.1 for t in times[-2:]):
            streaming_mode = True
        # print(lines)
        if not streaming_mode:
            if lines[-2:] == ["", ""]:
                # chop of the last two lines
                lines = lines[:-2]
                break
    return "\n".join(lines)


MODELS = {"code": "text-davinci-003"}


def cli() -> int:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument("prompt", help="Prompt to ask OpenAI", nargs="?")
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--mode", default="code", choices=MODELS.keys())
    argparser.add_argument("--verbose", action="store_true", default=False)
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
    prompt = args.prompt or prompt_input()

    # wow this makes all the difference with this ai
    stop = '"""'
    prompt += f"\n{stop}\nHere's my response:\n"
    openai.api_key = key

    def log(*pargs, **kwargs):
        if not args.verbose:
            return
        print(*pargs, **kwargs)

    log("\n############ BEGIN PROMPT OpenAI")
    log(prompt)
    log("############ END PROMPT")

    print("############ OPEN-AI QUERY")
    try:
        import warnings  # type: ignore  # pylint: disable=import-outside-toplevel

        warnings.simplefilter("ignore")
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
    except AuthenticationError as e:
        print("Error authenticating with OpenAI, deleting password from config and exiting.")
        print(e)
        save_config({})
        return 1
    # print(response)
    if response is None or not response.choices:
        print("No error response recieved from from OpenAI, response was:")
        print(response)
        return 1
    # print(response)
    for choice in response.choices:
        print("############ OPEN-AI RESPONSE")
        print(choice.text)
        if choice.finish_reason != "stop":
            print(
                "Warning: Weird response from OpenAI - choice.finish_reason: "
                + choice.finish_reason
            )
            break
    return 0


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
