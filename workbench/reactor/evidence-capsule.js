(function (root) {
  'use strict';
  function stableStringify(obj) {
    if (obj === null || typeof obj !== 'object') return JSON.stringify(obj);
    if (Array.isArray(obj)) return '[' + obj.map(stableStringify).join(',') + ']';
    return '{' + Object.keys(obj).sort().map(function (k) { return JSON.stringify(k) + ':' + stableStringify(obj[k]); }).join(',') + '}';
  }
  async function buildCapsule(state) {
    var Core = root.ReactorExperimentCore;
    var manifest = { capsuleId: state.experiment.experimentId, schemaVersion: 'gnome.reactor.capsule.v1', isSyntheticDemo: Boolean(state.isSyntheticDemo) };
    var files = {
      'manifest.json': stableStringify(manifest),
      'source/references.json': stableStringify(state.sourceRef),
      'experiments/experiment.json': stableStringify(state.experiment),
      'prompts/control.txt': state.controlPrompt,
      'prompts/variant.txt': state.variantPrompt,
      'datasets/inputs.json': stableStringify(state.dataset),
      'runs/observations.json': stableStringify(state.observations),
      'evaluations/scores.json': stableStringify(state.scores),
      'claims/findings.json': stableStringify(state.claims),
      'challenges/challenges.json': stableStringify(state.challenges)
    };
    var checksums = {};
    var keys = Object.keys(files);
    for (var i = 0; i < keys.length; i++) checksums[keys[i]] = await Core.sha256Hex(files[keys[i]]);
    return {
      schemaVersion: 'gnome.reactor.capsule.v1',
      manifest: manifest,
      source: state.sourceRef,
      experiments: state.experiment,
      prompts: { control: state.controlPrompt, variant: state.variantPrompt },
      datasets: state.dataset,
      runs: { observations: state.observations },
      evaluations: state.scores,
      claims: { findings: state.claims },
      challenges: { items: state.challenges },
      integrity: { checksums: checksums }
    };
  }
  root.ReactorEvidenceCapsule = { stableStringify: stableStringify, buildCapsule: buildCapsule };
})(typeof window !== 'undefined' ? window : globalThis);
