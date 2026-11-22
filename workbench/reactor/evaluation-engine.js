(function (root) {
  'use strict';
  function evaluateDeterministic(text, rules) {
    if (text == null || !rules || typeof rules !== 'object' || !['forbiddenTokens','requiredTokens','requireJson','requireCitationRegex'].some(function(k){return !!rules[k] && (!Array.isArray(rules[k]) || rules[k].length>0);})) return 'UNKNOWN';
    var f = (rules && rules.forbiddenTokens) || [];
    for (var i = 0; i < f.length; i++) if (text.indexOf(f[i]) !== -1) return 'FAIL';
    var r = (rules && rules.requiredTokens) || [];
    for (var j = 0; j < r.length; j++) if (text.indexOf(r[j]) === -1) return 'FAIL';
    return 'PASS';
  }
  function evaluateGrounded(text, ref) {
    if (text == null || !ref) return 'NOT_ASSESSABLE';
    if ((ref.contradictedClaims || []).some(function (c) { return text.indexOf(c) !== -1; })) return 'CONTRADICTED';
    if ((ref.supportedClaims || []).some(function (s) { return text.indexOf(s) !== -1; })) return 'SUPPORTED';
    return 'UNSUPPORTED';
  }
  function combineDisposition(det, grounded, judge) {
    var ev = grounded === 'SUPPORTED' ? 'PASS' : (grounded === 'UNSUPPORTED' || grounded === 'CONTRADICTED' ? 'FAIL' : 'UNKNOWN');
    var known = [det, ev, judge].filter(function (x) { return x === 'PASS' || x === 'FAIL'; });
    if (!known.length || !['PASS','FAIL'].includes(det) || ev === 'UNKNOWN') return 'Insufficient evidence';
    if (known.some(function (x) { return x !== known[0]; })) return 'Disputed';
    return known[0] === 'PASS' ? 'Supported pass' : 'Supported failure';
  }
  root.ReactorEvaluationEngine = { evaluateDeterministic: evaluateDeterministic, evaluateGrounded: evaluateGrounded, combineDisposition: combineDisposition };
})(typeof window !== 'undefined' ? window : globalThis);
