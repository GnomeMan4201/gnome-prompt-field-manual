#!/usr/bin/env python3
"""Offline verification and deterministic replay of a GNOME Reactor capsule JSON."""
import argparse,json,sys
from pathlib import Path
from reactor_engine import verify_and_replay_capsule

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('capsule',type=Path)
    a=p.parse_args(argv)
    try:
        cap=json.loads(a.capsule.read_text(encoding='utf-8'))
        result=verify_and_replay_capsule(cap)
    except (ValueError,OSError,TypeError) as exc:
        result={'valid':False,'errors':['CAPSULE_READ_OR_PARSE_FAILURE:'+str(exc)],'replay':None}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['valid'] else 2

if __name__=='__main__':sys.exit(main())
