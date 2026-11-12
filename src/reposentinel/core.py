"""Defensive, local-only repository scanner. Values matched as secrets are never displayed."""
from pathlib import Path
import re

IGNORE = {'.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build'}
SECRET = re.compile(r'(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?([A-Za-z0-9_./+=-]{8,})')
WORKFLOW = re.compile(r'(?i)(permissions:\s*write-all|pull_request_target:)')
MAX_FILES = 5000
MAX_BYTES = 256_000

def scan(path):
    root = Path(path).resolve()
    if not root.is_dir():
        raise ValueError('Expected an existing local directory')
    findings = []
    inspected = 0
    for file in root.rglob('*'):
        if not file.is_file() or file.is_symlink() or any(part in IGNORE for part in file.relative_to(root).parts):
            continue
        if inspected >= MAX_FILES:
            break
        if file.stat().st_size > MAX_BYTES:
            continue
        inspected += 1
        rel = str(file.relative_to(root))
        if file.name in ('.env', '.env.production', '.env.local'):
            findings.append({'file': rel, 'line': None, 'rule': 'environment-file-present', 'severity': 'review'})
        try:
            contents = file.read_text('utf-8')
        except (UnicodeError, OSError):
            continue
        for n, line in enumerate(contents.splitlines(), 1):
            if SECRET.search(line) and not line.strip().startswith('#'):
                findings.append({'file': rel, 'line': n, 'rule': 'possible-secret-value-redacted', 'severity': 'review'})
            if '.github/workflows/' in rel and WORKFLOW.search(line):
                findings.append({'file': rel, 'line': n, 'rule': 'workflow-permissions-or-trigger', 'severity': 'review'})
    return {'files_inspected': inspected, 'findings': findings, 'note': 'Heuristic scan; false positives possible. No secret values are included.'}

def configure(sub):
    p = sub.add_parser('scan', help='Audit a local directory you own')
    p.add_argument('path')
    p.add_argument('--format', choices=['json', 'sarif'], default='json', help='Output format (SARIF for GitHub code scanning)')
    p.add_argument('--max-findings', type=int, default=None, help='Allowed findings for CI gate')

def run(args):
    result = scan(args.path)
    if args.max_findings is not None:
        result['gate'] = evaluate_gate(result, args.max_findings)
    return to_sarif(result) if args.format == 'sarif' else result

def demo():
    return scan(Path(__file__).resolve().parents[2] / 'samples' / 'demo_repo')

def to_sarif(report):
    """Export sanitized findings to SARIF 2.1.0 for GitHub code scanning.

    Never include matched source lines, secret values or snippets.
    """
    labels = {
        'environment-file-present': 'Environment configuration file requires review',
        'possible-secret-value-redacted': 'Possible secret value (redacted)',
        'workflow-permissions-or-trigger': 'Review GitHub Actions permissions or trigger',
    }
    results = []
    for finding in report['findings']:
        rule = finding['rule']
        region = {'startLine': finding['line']} if isinstance(finding.get('line'), int) and finding['line'] > 0 else None
        location = {'physicalLocation': {'artifactLocation': {'uri': finding['file'].replace('\\', '/')}}}
        if region:
            location['physicalLocation']['region'] = region
        results.append({
            'ruleId': rule, 'level': 'warning',
            'message': {'text': labels.get(rule, 'Review finding')},
            'locations': [location],
        })
    return {
        'version': '2.1.0',
        '$schema': 'https://json.schemastore.org/sarif-2.1.0.json',
        'runs': [{
            'tool': {'driver': {
                'name': 'H4 RepoSentinel', 'informationUri': 'https://github.com/H4ckD4d/h4-reposentinel',
                'rules': [{'id': key, 'shortDescription': {'text': value}} for key, value in labels.items()],
            }},
            'results': results,
        }],
    }


def evaluate_gate(report, maximum):
    """Check CI finding budget without exposing secret values."""
    if not isinstance(maximum, int) or maximum < 0:
        raise ValueError('maximum findings must be nonnegative')
    count = len(report.get('findings', []))
    return {'passed': count <= maximum, 'observed': count, 'maximum': maximum}
