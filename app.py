#!/usr/bin/env python3
import sys
import argparse

from src.transcriber import transcribe, load_rules

def main():
    parser = argparse.ArgumentParser(description="Transcribe Thai text to Czech phonetics.")
    parser.add_argument("text", nargs="*", help="Thai text to transcribe. If not provided, reads from stdin.")

    args = parser.parse_args()

    rules = load_rules()

    if args.text:
        # Text provided as command line arguments
        input_text = " ".join(args.text)
        result = transcribe(input_text, rules)
        print(result)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
            if input_text:
                result = transcribe(input_text, rules)
                print(result)
        else:
            # Interactive mode or nothing provided
            try:
                for line in sys.stdin:
                    line = line.strip()
                    if line:
                        result = transcribe(line, rules)
                        print(result)
            except KeyboardInterrupt:
                pass

if __name__ == "__main__":
    main()
