(function (root) {
  'use strict';
  var CATEGORIES = [
    'PROMPT_INJECTION', 'INSTRUCTION_HIERARCHY_CONFUSION', 'TOOL_OUTPUT_CONTAMINATION',
    'RETRIEVED_DOCUMENT_MANIPULATION', 'EVALUATOR_INJECTION', 'CONTEXT_BOUNDARY_CONFUSION',
    'AUTHORITY_SPOOFING', 'UNSUPPORTED_CLAIM_GENERATION', 'MULTI_TURN_INSTRUCTION_DRIFT', 'EVIDENCE_LAUNDERING'
  ];
  function validateThreatModel(tm) {
    var errs = [];
    if (!tm || typeof tm !== 'object') return ['INVALID_THREAT_MODEL'];
    if (tm.schemaVersion !== 'gnome.reactor.threat-model.v1') errs.push('INVALID_SCHEMA_VERSION');
    if (CATEGORIES.indexOf(tm.category) === -1) errs.push('INVALID_THREAT_CATEGORY');
    ['threatModelId', 'targetBehavior', 'expectedAuthorizedBehavior', 'attackerObjective', 'attackerControlledSurface', 'defenderControlledSurface', 'trustBoundary', 'evaluationRubric'].forEach(function (f) {
      if (!tm[f] || !String(tm[f]).trim()) errs.push('MISSING_FIELD:' + f);
    });
    ["attackAssumptions","successConditions","failureConditions","scopeLimitations","safetyConstraints"].forEach(function(k){if(!Array.isArray(tm[k])||!tm[k].length||tm[k].some(function(x){return typeof x!=='string'||!x.trim()}))errs.push('INVALID_FIELD:'+k);});
    return errs;
  }
  root.ReactorThreatModel = { CATEGORIES: CATEGORIES, validateThreatModel: validateThreatModel };
})(typeof window !== 'undefined' ? window : globalThis);
