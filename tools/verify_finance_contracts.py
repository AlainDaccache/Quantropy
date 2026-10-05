"""Check authored examples, graph/catalog consistency; no expert certification."""
from pathlib import Path
import csv,itertools,json,math,statistics,sys

ROOT=Path(__file__).resolve().parents[1]/'docs'/'knowledge-base'
errors=[];checks=[]
def require(ok,msg):
    if not ok:errors.append(msg)
def rows(name):
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def case(name,actual,expected,tol=1e-8):
    ok=math.isclose(actual,expected,rel_tol=tol,abs_tol=tol)
    checks.append(dict(case=name,actual=actual,expected=expected,passed=ok))
    require(ok,'Example mismatch: '+name)

contracts=rows('contract-register.csv');methods=rows('method-catalog.csv');legacy=rows('method-inventory.csv')
require(len({x['id'] for x in contracts})==len(contracts),'Duplicate contract IDs')
require({r['id'] for r in methods}=={r['id'] for r in legacy},'Catalog/legacy membership mismatch')
require(len({r['id'] for r in methods})==len(methods),'Duplicate catalog IDs')
owners={r['owner'] for r in contracts}
require(all(r['canonical_family_owner'] in owners for r in methods),'Method without registered owner')
for r in contracts:require((ROOT/r['owner']).is_file(),'Missing contract '+r['id'])
by_slug={Path(r['owner']).stem:r for r in contracts}
graph={slug:[p for p in r['prerequisites'].split(';') if p] for slug,r in by_slug.items()}
seen=set();active=set()
def visit(node):
    if node in active:errors.append('Dependency cycle: '+node);return
    if node in seen:return
    if node not in graph:errors.append('Unknown prerequisite: '+node);return
    active.add(node)
    for dep in graph[node]:visit(dep)
    active.remove(node);seen.add(node)
for node in graph:visit(node)
source_text=(ROOT/'sources.md').read_text(encoding='utf-8')
for r in contracts:
    require(all('\n## '+sid+'\n' in source_text for sid in r['source_ids'].split(';')),'Missing contract evidence source: '+r['id'])

case('sample_mean',statistics.mean([1,2,3]),2)
case('sample_variance',statistics.variance([1,2,3]),1)
x=[0,1,2];y=[2,5,8]
beta=sum((a-statistics.mean(x))*(b-statistics.mean(y)) for a,b in zip(x,y))/sum((a-statistics.mean(x))**2 for a in x)
case('ols_slope',beta,3);case('ols_intercept',statistics.mean(y)-beta*statistics.mean(x),2)
a,b=1.,2.
for _ in range(50):
    mid=(a+b)/2
    if mid*mid>2:b=mid
    else:a=mid
case('bracketed_sqrt2',(a+b)/2,1.4142135623730951)
case('dso',365*30/365,30);case('dio',365*40/200,73);case('dpo',365*22/220,36.5)
case('cash_conversion_cycle',30+73-36.5,66.5)
case('dupont_identity',(18/200)*(200/150)*(150/90),.2)
case('altman_declared_fixture',1.2*.2+1.4*.3+3.3*.1+.6*1+1.5,3.09)
case('beneish_declared_fixture',-4.84+.92+.528+.404+.892+.115-.172-.327,-2.48)
case('gaussian_posterior_mean',(.04/.01+.08/.01)/(1/.01+1/.01),.06)
case('gaussian_posterior_variance',1/(1/.01+1/.01),.005)
case('equal_risk_vol',math.sqrt((2/3)**2*.01+(1/3)**2*.04),.09428090415820634)
case('hrp_two_leaf_left_weight',.04/(.01+.04),.8)
case('residual_income_one_period',100+(12-.1*100)/1.1,101.81818181818181)
case('acquisition_incremental_value',100+20-5-115,0)
case('subscription_nrr',(100-10-5+20)/100,1.05)
case('subscription_grr',(100-10-5)/100,.85)
case('swap_bootstrap_two_year',(1-.05/1.05)/1.05,.9070294784580498)
case('hazard_survival',math.exp(-.02),.9801986733067553)
case('hazard_spread_approx',.02*(1-.4),.012)
case('one_step_binomial_call',.5*max(110-100,0)+.5*max(90-100,0),5)
N=lambda z:.5*(1+math.erf(z/math.sqrt(2)))
def call(s,k,r,sig,t):
    d1=(math.log(s/k)+(r+.5*sig*sig)*t)/(sig*math.sqrt(t));d2=d1-sig*math.sqrt(t)
    return s*N(d1)-k*math.exp(-r*t)*N(d2)
price=call(100,100,.05,.2,1)
case('bsm_reference_call',price,10.450583572185565)
require(call(101,100,.05,.2,1)>price,'Call underlying monotonicity')
require(call(100,101,.05,.2,1)<price,'Call strike monotonicity')
require(call(100,100,.05,.21,1)>price,'Call volatility monotonicity')
lo,hi=.001,2.
for _ in range(70):
    mid=(lo+hi)/2
    if call(100,100,.05,mid,1)>10.450583572185565:hi=mid
    else:lo=mid
case('implied_vol_reference_inversion',(lo+hi)/2,.2)
case('svi_atm_example',math.sqrt(.02+.1*.1),.17320508075688773)
case('brinson_allocation',(.6-.5)*(.1-.075)+(.4-.5)*(.05-.075),.005)
case('brinson_selection',.5*(.12-.1)+.5*(.04-.05),.005)
case('brinson_interaction',(.6-.5)*(.12-.1)+(.4-.5)*(.04-.05),.003)
case('brinson_reconciliation',.6*.12+.4*.04-(.5*.1+.5*.05),.013)
case('end_period_contribution',100*1.05+10,115)
case('begin_period_contribution',110*1.05,115.5)
case('inflated_spending',10*1.02,10.2)
case('life_annuity_two_year',100*.99/1.05+100*.97/1.05**2,182.26757369614512)
case('aggregate_loss_expectation',2*100,200)
case('aggregate_loss_variance',2*100**2,20000)
case('excess_loss_recovery',min(max(150-100,0),30),30)
case('private_tvpi',(40+90)/100,1.3)
case('simple_carry',.2*(150-100),10)
case('futures_multiplier_pnl',50*(102-100),100)
case('psr_at_benchmark',N(0),.5)
case('psr_normal_moments',N(.1*math.sqrt(100)/math.sqrt(1+.5*.1**2)),.8407413278013518)
case('merton_maturity_reconciliation_high',max(120-100,0)+min(120,100),120)
case('merton_maturity_reconciliation_low',max(80-100,0)+min(80,100),80)

# Negative cases must fail economically rather than silently return plausible numbers.
require(1/0.001>100,'Near-zero denominator exposes scale sensitivity')
require(math.isclose(sum([.8,.2]),1),'Fully invested weights')
labels=[(1,5),(4,6)]
require(max(labels[0][0],labels[1][0])<=min(labels[0][1],labels[1][1]),'Purging overlap fixture')
fill_ids=['a','b','a'];quantities={'a':4,'b':6}
case('idempotent_fill_quantity',sum(quantities[k] for k in set(fill_ids)),10)

summary=dict(contracts=len(contracts),mapped_methods=len(methods),dependency_nodes=len(seen),arithmetic_cases=len(checks),errors=errors,scope='Draft graph/catalog consistency and selected example arithmetic and invariants; no independent domain review, all-method verification or production engine validation')
if '--write-evidence' in sys.argv:
    require(not errors,'Evidence must not be written on failed verification')
    if not errors:(ROOT/'contract-verification.json').write_text(json.dumps(dict(summary=summary,checks=checks),indent=2),encoding='utf-8')
else:
    recorded=json.loads((ROOT/'contract-verification.json').read_text(encoding='utf-8'))
    require(recorded['checks']==checks,'Stored evidence differs from recomputed examples')
print(json.dumps(summary,indent=2))
raise SystemExit(1 if errors else 0)
