import argparse
import os
import sys
from pathlib import Path

from antlr4 import CommonTokenStream, FileStream, ParseTreeWalker

from SiteLangLexer import SiteLangLexer
from SiteLangParser import SiteLangParser
from SiteListener import DeploymentError, SiteDeployListener
from syntax_error_listener import SyntaxErrorListener


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Compile a SiteLang file and deploy the generated site."
    )
    parser.add_argument("input_file", help="Path to the .sl source file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate HTML locally without calling GitHub or Vercel",
    )
    return parser.parse_args(argv[1:])


def parse_source(input_path):
    syntax_listener = SyntaxErrorListener()
    input_stream = FileStream(str(input_path), encoding="utf-8")

    lexer = SiteLangLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(syntax_listener)

    token_stream = CommonTokenStream(lexer)
    parser = SiteLangParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(syntax_listener)
    tree = parser.site()
    return tree, syntax_listener.errors


def main(argv):
    try:
        args = parse_arguments(argv)
    except SystemExit as exc:
        return int(exc.code)

    input_path = Path(args.input_file).resolve()
    if not input_path.is_file():
        print(f"Usage error: input file not found: {input_path}", file=sys.stderr)
        return 2

    tree, syntax_errors = parse_source(input_path)
    if syntax_errors:
        for error in syntax_errors:
            print(f"Syntax error: {error}", file=sys.stderr)
        print("Compilation stopped before any external API call.", file=sys.stderr)
        return 1

    listener = SiteDeployListener(
        github_token=os.environ.get("GITHUB_TOKEN", ""),
        vercel_token=os.environ.get("VERCEL_TOKEN", ""),
        vercel_team_id=os.environ.get("VERCEL_TEAM_ID", ""),
    )
    ParseTreeWalker().walk(listener, tree)

    semantic_errors = listener.validate()
    if semantic_errors:
        for error in semantic_errors:
            print(f"Semantic error: {error}", file=sys.stderr)
        print("Compilation stopped before any external API call.", file=sys.stderr)
        return 1

    output_path = Path(__file__).resolve().parent / "generated" / "index.html"
    html_content = listener.compile(output_path)
    print(f"[+] HTML generated: {output_path}")

    if args.dry_run:
        print("[OK] Dry run completed. No external API calls were made.")
        return 0

    if not listener.github_token or not listener.vercel_token:
        print(
            "Usage error: GITHUB_TOKEN and VERCEL_TOKEN are required for deployment.",
            file=sys.stderr,
        )
        return 2

    try:
        result = listener.deploy(html_content)
    except DeploymentError as error:
        print(f"Deployment error: {error}", file=sys.stderr)
        return 1

    print(f"[+] GitHub repository: {result['repository_url']}")
    print(f"[+] GitHub file: {result['file_url']}")
    print(f"[OK] Vercel deployment READY: {result['deployment_url']}")
    print("[OK] Done! SiteLang compiled and deployed the site.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
