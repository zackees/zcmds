"""askai - ask openai for help"""

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Optional

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config
from zcmds.util.prompt_input import prompt_input
from zcmds.util.streaming_console import StreamingConsole

try:
    from zcmds.util.chatgpt import (
        ADVANCED_MODEL,
        FAST_MODEL,
        ChatBot,
        ChatGPTAuthenticationError,
        ChatGPTConnectionError,
        ChatGPTRateLimitError,
        ChatStream,
    )
except KeyboardInterrupt:
    # Importing openai stuff can take a while and so if a keyboard interrupt
    # happens during that time then we want to exit immediately rather
    # than throw a cryptic error and stack trace.
    sys.exit(1)

AI_ASSISTANT = (
    "You are a helpful assistant to a senior programmer. "
    "If I am asking how to do something in general then go ahead "
    "and recommend popular third-party apps that can get the job done, "
    "but don't recommend additional tools when I'm currently asking how to do use "
    "a specific tool."
)

AI_ASSISTANT_CHECKER_PROMPT = (
    "Now check this answer and verify if it's correct. If it's correct, say so. \n"
    "If it's not correct or if there are any issues, explain what's wrong and provide the correct information. \n"
    "Otherwise, say that this correct and repeat the answer VERBATIM."
)

FORCE_COLOR = False


@dataclass
class FileOutputStream:
    outfile: Optional[str] = None

    def write(self, text: str) -> None:
        if self.outfile:
            with open(self.outfile, "a") as f:
                f.write(text)


class OutStream:
    def __init__(self, outfile: Optional[str]) -> None:
        self.outfile = FileOutputStream(outfile)
        self.color_term = StreamingConsole()
        if FORCE_COLOR:
            self.color_term.force_color()

    def write(self, text: str) -> None:
        self.outfile.write(text)
        self.color_term.update(text)

    def close(self) -> None:
        pass


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument("prompt", help="Prompt to ask OpenAI", nargs="?")
    argparser.add_argument(
        "--input-file", help="Input file containing prompts", type=str
    )
    argparser.add_argument("--json", help="Print response as json", action="store_true")
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--output", help="Output file")
    argparser.add_argument("--color", help="Output color", action="store_true")

    model_group = argparser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--fast",
        action="store_true",
        default=False,
        help=f"chat gpt 4o mini: {FAST_MODEL}",
    )
    model_group.add_argument(
        "--advanced",
        action="store_true",
        default=False,
        help=f"bleeding edge model: {ADVANCED_MODEL}",
    )
    model_group.add_argument("--model", default=None)
    argparser.add_argument("--verbose", action="store_true", default=False)
    argparser.add_argument("--no-stream", action="store_true", default=False)
    argparser.add_argument("--assistant-prompt", type=str, default=AI_ASSISTANT)
    argparser.add_argument(
        "--assistant-prompt-file", type=str, help="File containing assistant prompt"
    )
    # max tokens
    argparser.add_argument(
        "--max-tokens", help="Max tokens to return", type=int, default=None
    )
    argparser.add_argument(
        "--code",
        action="store_true",
        default=False,
        help="Code mode: enables aider mode",
    )
    argparser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Sends the response back to the chatbot for a second opinion",
    )
    return argparser.parse_args()


def run_chat_query(
    chatbot: ChatBot,
    prompts: list[str],
    output_stream: OutStream,
    args: argparse.Namespace,
) -> Optional[int]:
    # allow exit() and exit to exit the app
    as_json = args.json
    if not as_json:
        print("############ OPEN-AI QUERY")
    try:
        chat_stream: ChatStream = chatbot.query(prompts, no_stream=args.no_stream)
    except ChatGPTConnectionError as err:
        print(err)
        return 1
    except ChatGPTAuthenticationError as e:
        print(
            "Error authenticating with OpenAI, deleting password from config and exiting."
        )
        print(e)
        save_config({})
        return 1
    except ChatGPTRateLimitError:
        print("Rate limit exceeded, set a new key with --set-key")
        return 1
    if as_json:
        print(chat_stream)
        return 0
    if chat_stream is None or not chat_stream.success():
        print("No error response received from OpenAI, response was:")
        output_stream.write(str(chat_stream.response()))
        return 1
    if not args.output:
        print("############ OPEN-AI RESPONSE\n")
    response_text = ""
    for text in chat_stream:
        if text is None:
            break
        response_text += text
        output_stream.write(response_text)
    output_stream.write(response_text + "\n")
    prompts.append(response_text)
    return None


def cli() -> int:
    args = parse_args()

    global FORCE_COLOR
    FORCE_COLOR = args.color
    config = create_or_load_config()
    max_tokens = args.max_tokens
    if args.fast:
        args.model = FAST_MODEL
        max_tokens = 16384
    if args.input_file:
        with open(args.input_file, "r") as file:
            args.prompt = file.read().strip()
    if args.model is None:
        if args.advanced:
            model = ADVANCED_MODEL
            max_tokens = 4096
        else:
            model = FAST_MODEL
            max_tokens = 16384
    else:
        model = args.model

    if args.code:
        return os.system("aicode")

    if args.set_key:
        config["openai_key"] = args.set_key
        save_config(config)
        config = create_or_load_config()
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

    def log(*pargs, **kwargs):
        if not args.verbose:
            return
        print(*pargs, **kwargs)

    if args.assistant_prompt_file:
        with open(args.assistant_prompt_file, "r") as f:
            ai_assistant_prompt = f.read().strip()
    else:
        ai_assistant_prompt = args.assistant_prompt

    log(prompt)
    prompts = [prompt]

    chatbot = ChatBot(
        openai_key=key,
        max_tokens=max_tokens,
        model=model,
        ai_assistant_prompt=ai_assistant_prompt,
    )

    while True:
        try:
            rtn: Optional[int] = None
            output_stream = OutStream(args.output)  # needs to be created every time.
            new_cmd = prompts[-1].strip().replace("()", "")
            if new_cmd.startswith("!"):
                prompts = prompts[0:-1]
                new_cmd = new_cmd[1:]
                rtn = os.system(new_cmd)
                print(f"Command exited and returned {rtn}")
                prompts.append(prompt_input())
                continue
            elif new_cmd == "exit":
                print("Exited due to 'exit' command")
                return 0
            rtn = run_chat_query(chatbot, prompts, output_stream, args)
            if rtn is not None:
                return rtn

            if args.check:
                output_stream = OutStream(
                    args.output
                )  # needs to be created every time.
                check_prompt = AI_ASSISTANT_CHECKER_PROMPT + "\n\n" + prompts[-1]
                prompts.append(check_prompt)
                print("\n############ CHECKING RESPONSE")
                rtn = run_chat_query(chatbot, prompts, output_stream, args)
                if rtn is not None:
                    return rtn

            if not interactive:
                return 0

            # next loop.
            prompts.append(prompt_input())
        finally:
            output_stream.close()


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1
    except SystemExit as e:
        if isinstance(e.code, int):
            return e.code
        return 1


if __name__ == "__main__":
    sys.exit(main())
