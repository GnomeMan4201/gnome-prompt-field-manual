"""Valid strict Phase VIII-A synthetic inputs for invariant regression tests only."""
import hashlib
from reactor_engine import sha256_text

C = sha256_text('Control')
V = sha256_text('Variant')
I = sha256_text('Input')
from reactor_engine import canonical_json
R = sha256_text(canonical_json({'criteria':['criterion']}))

def observation(condition,passed=True,input_id='I-1',trial_id='trial-1',**mods):
    value=dict(schemaVersion='gnome.reactor.observation.v1',runId=f'{condition}-{input_id}-{trial_id}',
        experimentId='E-1',condition=condition,inputId=input_id,inputHash=I,
        promptHash=C if condition=='CONTROL' else V,
        provider='p',model='m',evaluator='e',temperature=0,seed=None,tools=[],datasetId='D-1',rubricHash=R,
        trialId=trial_id,outputText='test output',passed=passed)
    value.update(mods)
    return value

def experiment(inputs=None):
    return dict(schemaVersion='gnome.reactor.experiment.v1',experimentId='E-1',hypothesis='Controlled hypothesis',
        controlPromptHash=C,variantPromptHash=V,dataset={'datasetId':'D-1','inputs':inputs or [{'inputId':'I-1'}]},
        rubric={'criteria':['criterion']},modelConfig={'provider':'p','model':'m','temperature':0,'seed':None})
