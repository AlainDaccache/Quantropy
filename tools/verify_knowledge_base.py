"""Verify KB structure and selected illustrative calculations, not all finance."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1] / 'docs' / 'knowledge-base'
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

def read_csv(name):
    with (ROOT/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
listed = {r['path'] for r in manifest['files']}
actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name != 'manifest.json'}
require(listed == actual, 'Manifest file membership differs')
for entry in manifest['files']:
    p = ROOT/entry['path']
    require(p.is_file(), 'Missing file: '+entry['path'])
    if p.is_file():
        require(hashlib.sha256(p.read_bytes()).hexdigest() == entry['sha256'], 'Hash mismatch: '+entry['path'])
        require(p.stat().st_size == entry['bytes'], 'Size mismatch: '+entry['path'])

links = 0
for p in ROOT.rglob('*.md'):
    for href in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
        if href.startswith(('https://', 'http://')):
            continue
        rel, _, anchor = href.partition('#')
        dest = (p.parent/rel).resolve() if rel else p
        links += 1
        require(dest.is_file(), f'Broken link: {p.name} -> {href}')
        if dest.is_file() and anchor:
            headings = re.findall(r'^#+\s+(.+)$', dest.read_text(encoding='utf-8'), re.M)
            anchors = {re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings}
            require(anchor in anchors, f'Broken anchor: {p.name} -> {href}')

source_ids = set(re.findall(r'^## ([A-Z0-9-]+)$', (ROOT/'sources.md').read_text(encoding='utf-8'), re.M))
require(len(source_ids) == manifest['sources'], 'Source count mismatch')
for name, count, owner, refs in [
    ('capability-register.csv', 'capabilities', 'specification', None),
    ('method-inventory.csv', 'methods', 'specification_owner', 'reference_map'),
    ('finance-coverage.csv', 'finance_coverage_units', 'canonical_owner', None),
    ('coverage-audit.csv', None, 'owner_specification', 'framework_or_source_ids'),
    ('strategy-families.csv', 'strategy_families', None, None),
]:
    rows = read_csv(name)
    require(len({r['id'] for r in rows}) == len(rows), 'Duplicate IDs: '+name)
    if count:
        require(len(rows) == manifest[count], 'Count mismatch: '+name)
    if owner:
        require(all((ROOT/r[owner]).is_file() for r in rows), 'Owner missing: '+name)
    if refs:
        require(all(set(r[refs].split(';')) <= source_ids for r in rows), 'Source missing: '+name)
coverage = read_csv('finance-coverage.csv')
require(len({(r['domain'], r['unit']) for r in coverage}) == len(coverage), 'Duplicate coverage unit')
require(len(list((ROOT/'reference').glob('[0-9][0-9]-*.md'))) == manifest['reference_articles'], 'Reference article count mismatch')

# Recalculate examples independently of the committed report.
results = {}
def calc(name, value):
    results[name] = value
calc('compound_two_years', 100*1.05**2)
calc('annuity_three_years', sum(100/1.05**t for t in range(1, 4)))
payment = 1000*.05/(1-1.05**-3)
calc('loan_payment', payment)
balance = 1000
for _ in range(3):
    balance = balance*1.05-payment
calc('loan_final_balance', balance)
calc('real_return', 1.05/1.02-1)
calc('fcff', 100*.75+10-20-5)
calc('perpetuity', 60/(.08-.02))
calc('sovereign_debt_ratio', 1.04/1.03*.6-.01)
price = 5/1.05+105/1.05**2
calc('bond_par', price)
duration = (5/1.05+2*105/1.05**2)/price
calc('bond_macaulay', duration)
calc('bond_modified', duration/1.05)
calc('credit_loss', .02*.4*1000)
calc('option_parity_call', 6+100-100*math.exp(-.05))
calc('equal_weight_vol', math.sqrt(.5**2*.1**2+.5**2*.2**2))
calc('minimum_variance_vol', math.sqrt(.8**2*.1**2+.2**2*.2**2))
calc('linked_return', 1.1**2-1)
calc('account_with_flow', (100*1.1+100)*1.1)
calc('withdrawal_sequence_up_down', (100*1.2-10)*.8-10)
calc('withdrawal_sequence_down_up', (100*.8-10)*1.2-10)
calc('insurance_expected_pv', 1000*.01/1.05)
calc('ten_year_gross_fee_example', 100*1.08**10)
calc('ten_year_net_fee_example', 100*1.06**10)
report = json.loads((ROOT/'reference-verification.json').read_text(encoding='utf-8'))
require(set(results) == {c['case'] for c in report['checks']}, 'Example evidence membership mismatch')
for c in report['checks']:
    require(c['case'] in results and math.isclose(results.get(c['case'], math.nan), c['expected'], rel_tol=1e-8, abs_tol=1e-8), 'Example mismatch: '+c['case'])

# Non-formula invariants: return order, derivative bounds, risk contribution and tail convention.
require((100*1.2-10)*.8-10 != (100*.8-10)*1.2-10, 'Withdrawal sequence must affect result')
require(math.isclose(100*1.2*.8, 100*.8*1.2), 'No-flow terminal return must be order invariant')
weights = [.8, .2]
variances = [.01, .04]
vol = math.sqrt(sum(w*w*v for w, v in zip(weights, variances)))
require(math.isclose(sum(w*w*v/vol for w, v in zip(weights, variances)), vol), 'Risk contributions must sum to volatility')
losses = [0, 1, 2, 3, 4]
alpha = .8
var = losses[math.ceil(alpha*len(losses))-1]
es = sum(losses[math.ceil(alpha*len(losses)):])/(len(losses)*(1-alpha))
require(var == 3 and math.isclose(es, 4), 'Discrete tail example mismatch')

result = dict(hashed_files=len(listed), internal_links=links, reference_articles=manifest['reference_articles'], finance_units=len(coverage), arithmetic_examples=len(results), sources=len(source_ids), errors=errors, scope='Structural consistency and selected arithmetic/invariants only; no universal completeness, claim-level expert review or runtime certification')
print(json.dumps(result, indent=2))
raise SystemExit(1 if errors else 0)
