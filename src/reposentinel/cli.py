"""Command-line entry point for H4 RepoSentinel."""
import argparse
import json
from . import core, research

PUBLIC_TOPICS = {
"pt": "Boas práticas públicas de auditoria defensiva de repositórios e configuração ci/cd",
"en": "Public best practices for defensive repository and ci/cd configuration audits",
"es": "Buenas prácticas públicas sobre auditorías defensivas de repositorios y ci/cd"}

def main():
    parser = argparse.ArgumentParser(description="H4 RepoSentinel by Chris Cruz (@h4ckd4d)")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run local, synthetic demonstration")
    demo.add_argument("--lang", choices=["pt", "en", "es"], default="pt")
    external = sub.add_parser("research", help="Opt-in public research grounded with Google Search")
    external.add_argument("--lang", choices=["pt", "en", "es"], default="pt")
    external.add_argument("--topic", default=None)
    core.configure(sub)
    args = parser.parse_args()
    if args.command == "demo":
        result = core.demo()
    elif args.command == "research":
        result = research.lookup(args.topic or PUBLIC_TOPICS[args.lang], args.lang)
    else:
        result = core.run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
