#!/usr/bin/env python3
"""Source-bound references and declared blind review, without identity spoofing claims.

This offline utility cannot authenticate people or external source origin. It will
never assert INDEPENDENTLY_CHECKED based on two user-supplied text fields.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
from datetime import datetime, timezone
from typing import Any

AUTHORITY_LEVELS = frozenset({
    'SYNTHETIC_FIXTURE', 'REVIEWER_ASSERTED', 'SOURCE_CHECKED',
    'INDEPENDENTLY_CHECKED', 'DISPUTED', 'NOT_VERIFIABLE'
})


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _nonempty(s: Any) -> bool:
    return isinstance(s, str) and bool(s.strip()) and len(s) <= 512


def verify_reference_bytes(ref: dict) -> list[str]:
    errors = []
    if not isinstance(ref, dict):
        return ['REFERENCE_NOT_OBJECT']
    content, span = ref.get('originalContent'), ref.get('evidenceSpan')
    if not isinstance(content, str) or len(content.encode('utf-8')) > 256 * 1024:
        errors.append('INVALID_SOURCE_CONTENT')
    elif ref.get('sourceHash') != sha256_text(content):
        errors.append('SOURCE_HASH_MISMATCH')
    if not _nonempty(span) or not isinstance(content, str) or span not in content:
        errors.append('EVIDENCE_SPAN_NOT_IN_SOURCE')
    if not _nonempty(ref.get('referenceId')) or not _nonempty(ref.get('sourceId')):
        errors.append('REFERENCE_ID_MISSING')
    if ref.get('authorityLevel') not in AUTHORITY_LEVELS:
        errors.append('UNKNOWN_AUTHORITY')
    if ref.get('authorityLevel') == 'INDEPENDENTLY_CHECKED':
        # Offline review identities cannot be authenticated by this app.
        errors.append('INDEPENDENCE_NOT_AUTHENTICATED')
    return errors


def create_reference(ref_id: str, source_id: str, source_type: str,
                     original_content: str, evidence_span: str, expected_answer: str,
                     authority: str = 'REVIEWER_ASSERTED', reviewer_id: str | None = None,
                     reviewed_at: str | None = None, *, expected_json: dict | None = None) -> dict[str, Any]:
    if authority not in ('REVIEWER_ASSERTED','SYNTHETIC_FIXTURE'):
        raise ValueError('AUTHORITY_REQUIRES_SEPARATE_REVIEW')
    if not all(_nonempty(v) for v in (ref_id,source_id,source_type,evidence_span,expected_answer,reviewer_id)):
        raise ValueError('INVALID_REFERENCE_FIELDS')
    if not isinstance(original_content,str) or evidence_span not in original_content:
        raise ValueError('EVIDENCE_SPAN_NOT_IN_SOURCE')
    obj = {'schemaVersion':'gnome.reactor.reference.v3', 'referenceId':ref_id,
           'sourceId':source_id,'sourceType':source_type,'originalContent':original_content,
           'sourceHash':sha256_text(original_content),'evidenceSpan':evidence_span,
           'expectedAnswer':expected_answer,'verificationMethod':'NONE',
           'reviewerId':reviewer_id,'reviewTimestamp':reviewed_at,
           'authorityLevel':authority,'reviewHistory':[],
           'contradictoryEvidence':[],
           'independenceAuthentication':'NOT_AVAILABLE_OFFLINE',
           'knownLimitations':['Local SHA-256 does not authenticate external source origin.']}
    if expected_json is not None:
        if not isinstance(expected_json,dict) or not expected_json:
            raise ValueError('INVALID_EXPECTED_JSON')
        obj['expectedJson']=deepcopy(expected_json)
    return obj


def blind_verify_reference(ref: dict[str, Any], second_reviewer_id: str,
                           confirmed_answer: str, model_output_hidden: bool = True,
                           *, observed_source: str | None = None) -> dict[str, Any]:
    """Declared blind second-review. Identity independence is NOT established.

    A second reviewer must supply actual source bytes; never trust a check box
    alone. This is a content check, not cryptographic reviewer authentication.
    """
    if not model_output_hidden:
        raise ValueError('BLIND_REVIEW_VIOLATION')
    if not _nonempty(second_reviewer_id) or second_reviewer_id == ref.get('reviewerId') or not ref.get('reviewerId'):
        rejected=deepcopy(ref)
        rejected['reviewRejection']='REVIEWER_NOT_SEPARATE'
        rejected['authorityLevel']='REVIEWER_ASSERTED'
        return rejected
    if not _nonempty(confirmed_answer):
        raise ValueError('EMPTY_CONFIRMATION')
    result = deepcopy(ref)
    result['reviewHistory'] = list(result.get('reviewHistory',[]))
    source_matches = (observed_source is not None and isinstance(observed_source,str)
                      and sha256_text(observed_source) == result.get('sourceHash')
                      and result.get('evidenceSpan','') in observed_source)
    agrees = confirmed_answer == result.get('expectedAnswer')
    record = {'reviewerId':second_reviewer_id,
              'blindReviewDeclared':True, 'sourceBytesProvided':observed_source is not None,
              'sourceHashMatched':source_matches,'answerAgreed':agrees,
              'identityAuthentication':'UNVERIFIED_OFFLINE'}
    result['reviewHistory'].append(record)
    if not agrees:
        result['authorityLevel']='DISPUTED'
        result['contradictoryEvidence'].append({'reviewerId':second_reviewer_id,
                                                 'observedExpectedAnswer':confirmed_answer})
    elif source_matches:
        result['authorityLevel']='SOURCE_CHECKED'
        result['verificationMethod']='SECOND_REVIEWER_DECLARED_SOURCE_BYTE_CHECK'
    else:
        # Still reviewer-asserted; supplying a name and matching string is not checking a source.
        result['authorityLevel']='REVIEWER_ASSERTED'
    return result


def checked_reference_eligible(ref: dict) -> bool:
    """Requires recorded content check; does not imply independent identity."""
    if verify_reference_bytes(ref):
        return False
    if ref.get('authorityLevel') != 'SOURCE_CHECKED':
        return False
    return any(r.get('sourceHashMatched') is True and r.get('answerAgreed') is True
               and r.get('reviewerId') != ref.get('reviewerId')
               and r.get('sourceBytesProvided') is True for r in ref.get('reviewHistory',[]))
