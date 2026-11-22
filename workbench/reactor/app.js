(function (root) {
  'use strict';
  var Src = root.ReactorSourceAdapter;
  var Core = root.ReactorExperimentCore;
  var Comp = root.ReactorComparisonEngine;
  var Cap = root.ReactorEvidenceCapsule;
  var Replay = root.ReactorReplayEngine;

  root.bootEvidenceReactor = async function () {
    var rootEl = document.getElementById('reactor-root');
    var baseline;
    try { baseline = await Src.loadIndex(); } catch (e) { rootEl.textContent = 'Reactor source index unavailable: ' + e.message; return; }
    var state = {
      mode: 'm1',
      isSyntheticDemo: false,
      selectedEntry: baseline.entries[0],
      controlPrompt: 'OBJECTIVE: Summarize the attached log.',
      variantPrompt: 'OBJECTIVE: Summarize only verified claims in [LOG].\nEVIDENCE BOUNDARY: Cite [Line]; output NOT_IN_SOURCE if absent.',
      variantHash: 'pending',
      experiment: {
        schemaVersion: 'gnome.reactor.experiment.v1',
        experimentId: 'EXP-001',
        hypothesis: 'Adding explicit NOT_IN_SOURCE evidence boundary reduces unsupported metric interpolation.',
        dataset: { datasetId: 'DS-001', inputs: [{ inputId: 'IN-1', text: 'Q2 latency: 18ms. (Q3 absent)' }] },
        rubric: { criteria: ['no_unsupported_claims'] },
        modelConfig: { provider: 'offline-import', model: 'UNSPECIFIED', temperature: null, seed: null },
        controlPromptHash: null, variantPromptHash: null
      },
      observations: [],
      challenges: [],
      replayResult: null,
      statusMsg: '',
      errMsg: ''
    };

    var navBtns = document.querySelectorAll('.mode-btn');

    function esc(s) { return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

    function loadSyntheticDemo() {
      state.isSyntheticDemo = true;
      state.observations = [
        { schemaVersion: 'gnome.reactor.observation.v1', runId: 'DEMO-1C', experimentId: 'EXP-001', condition: 'CONTROL', inputId: 'IN-1', inputHash: 'demo', promptHash: 'demo', provider: 'SYNTHETIC_DEMO', model: 'SYNTHETIC_MODEL', outputText: 'Q3 latency was 21ms.', passed: false, evaluator: 'rubric-v1' },
        { schemaVersion: 'gnome.reactor.observation.v1', runId: 'DEMO-1V', experimentId: 'EXP-001', condition: 'VARIANT', inputId: 'IN-1', inputHash: 'demo', promptHash: 'demo', provider: 'SYNTHETIC_DEMO', model: 'SYNTHETIC_MODEL', outputText: 'NOT_IN_SOURCE: Q3 absent.', passed: true, evaluator: 'rubric-v1' }
      ];
      state.statusMsg = 'Loaded SYNTHETIC DEMONSTRATION (clearly isolated from empirical evidence).';
      state.mode = 'm5';
      render();
    }

    function render() {
      navBtns.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-mode') === state.mode ? 'true' : 'false'); });
      var demoBanner = state.isSyntheticDemo
        ? '<div class="callout-err"><strong>SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE:</strong> Illustrative onboarding data only. Cannot be promoted to verified research claims.</div>'
        : '';

      var body = '';
      if (state.mode === 'm1') {
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 01 — Method Selector (Domain A: Source Truth)</h2>' +
          '<p style="color:var(--text-dim);font-size:0.88rem;">Select a source-linked method from the 91-entry baseline (<code>0/91</code> canonical bodies independently verified; raw candidates only), or explore with a clearly marked synthetic onboarding experiment.</p>' +
          '<div style="margin-bottom:12px;"><button type="button" class="btn btn-primary" id="load-demo-btn">Load Synthetic Onboarding Demo</button></div>' +
          baseline.entries.map(function (e) {
            return '<button type="button" class="btn" data-sel-entry="' + e.id + '" style="display:block;width:100%;text-align:left;margin-bottom:8px;' + (state.selectedEntry.id === e.id ? 'border-color:var(--amber);' : '') + '">' +
              '<strong>' + esc(e.id) + '</strong> — ' + esc(e.title) + ' <span class="pill pill-amber">' + esc(e.bodyStatus) + '</span>' +
            '</button>';
          }).join('');
      } else if (state.mode === 'm2') {
        var diff = Core.computeLineDiff(state.controlPrompt, state.variantPrompt);
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 02 — Prompt Microscope (Domain B: Experimental)</h2>' +
          '<div class="callout">Modified variants never inherit canonical editorial verification status.</div>' +
          '<div class="microscope-grid" style="grid-template-columns:1fr 1fr;">' +
            '<div class="pane"><div class="mono" style="font-size:0.72rem;color:var(--amber);">CONTROL SNAPSHOT</div><textarea id="ctrl-ta" class="textarea">' + esc(state.controlPrompt) + '</textarea></div>' +
            '<div class="pane"><div class="mono" style="font-size:0.72rem;color:var(--green);">EXPERIMENTAL VARIANT</div><textarea id="var-ta" class="textarea">' + esc(state.variantPrompt) + '</textarea></div>' +
          '</div>' +
          '<div class="source-pre" style="background:#070709;color:var(--text);margin-top:12px;">' + diff.map(function (d) { return (d.type === 'del' ? '- ' : d.type === 'add' ? '+ ' : '  ') + esc(d.line); }).join('\n') + '</div>';
      } else if (state.mode === 'm3') {
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 03 — Experiment Designer</h2>' +
          '<div class="pane"><label class="mono" style="font-size:0.72rem;">Hypothesis</label><input id="exp-hyp" class="input" value="' + esc(state.experiment.hypothesis) + '" style="margin:4px 0 10px;">' +
          '<label class="mono" style="font-size:0.72rem;">Model Identifier (Leave UNSPECIFIED if offline)</label><input id="exp-model" class="input" value="' + esc(state.experiment.modelConfig.model) + '"><button type="button" class="btn btn-primary" id="freeze-exp-btn">Freeze Prompt Hashes</button><p class="mono">Frozen hashes must match imported observation promptHash. No automatic experimental result is produced.</p></div>';
      } else if (state.mode === 'm4') {
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 04 — Execution Chamber (Offline Import &amp; Opt-In Local Endpoint)</h2>' +
          '<div class="pane"><div class="mono" style="font-size:0.72rem;color:var(--amber);">PATH A — OFFLINE EVIDENCE IMPORT (JSON ARRAY)</div><p class="mono">Requires experiment ID, true SHA-256 prompt/input hashes, matched model configuration, unique trials and known dataset IDs.</p>' +
          '<textarea id="obs-import-ta" class="textarea" placeholder=\'[{"inputId":"IN-1","condition":"CONTROL","outputText":"...","passed":false,"model":"m1","provider":"p1","evaluator":"r1"}]\' style="margin:6px 0;"></textarea>' +
          '<button type="button" class="btn btn-primary" id="import-obs-btn">Import Observation Records</button></div>';
      } else if (state.mode === 'm5') {
        var hasObs = state.observations.length > 0;
        var summary = hasObs ? Comp.summarizeTrials(state.observations) : null;
        var compStatus = summary && summary.pairs.length ? summary.pairs[0].comparability : null;
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 05 — Comparative Analysis, Counterfactuals &amp; Challenges</h2>' +
          (!hasObs
            ? '<div class="callout"><strong>NOT MEASURED:</strong> No execution observations imported yet. Import real observations in Mode 04 or load the labeled Synthetic Onboarding Demo in Mode 01.</div>'
            : '<div class="callout-ok"><strong>Comparability:</strong> ' + esc(compStatus ? compStatus.status : 'INSUFFICIENT_PAIRS') + ' | <strong>Paired Outcome (IN-1):</strong> ' + esc(JSON.stringify(summary.classifications)) + '</div>') +
          '<div class="pane" style="margin-top:12px;"><div class="mono" style="font-size:0.72rem;color:var(--crimson);">ADVERSARIAL CHALLENGE LAYER</div>' +
          '<input id="chal-rat" class="input" placeholder="Challenge rationale (e.g., Baseline miss or evaluator contamination)..." style="margin:6px 0;">' +
          '<button type="button" class="btn btn-primary" id="add-chal-btn">File Challenge</button>' +
          state.challenges.map(function (c) { return '<div class="callout-err"><strong>' + esc(c.challengeId) + ':</strong> ' + esc(c.rationale) + '</div>'; }).join('') +
          '</div>';
      } else {
        body = '<h2 style="font-family:var(--serif);font-weight:400;margin:0 0 8px;">Mode 06 — Evidence Capsule &amp; Offline Computational Replay</h2>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">' +
            '<button type="button" class="btn btn-primary" id="export-cap-btn">Export Evidence Capsule (.json)</button>' +
            '<button type="button" class="btn btn-green" id="run-replay-btn">Run Offline Computational Replay</button><label class="btn">Import capsule for replay <input type="file" accept=".json,application/json" id="import-cap-file"></label>' +
          '</div>' +
          (state.replayResult ? '<pre class="source-pre" style="background:#070709;color:var(--text);">' + esc(JSON.stringify(state.replayResult, null, 2)) + '</pre>' : '');
      }

      rootEl.innerHTML = demoBanner + (state.statusMsg ? '<div class="callout-ok">' + esc(state.statusMsg) + '</div>' : '') + (state.errMsg ? '<div class="callout-err">' + esc(state.errMsg) + '</div>' : '') + body;
      wire();
    }

    function wire() {
      var ldb = document.getElementById('load-demo-btn'); if (ldb) ldb.addEventListener('click', loadSyntheticDemo);
      rootEl.querySelectorAll('[data-sel-entry]').forEach(function (b) {
        b.addEventListener('click', function () {
          state.selectedEntry = baseline.entries.find(function (e) { return e.id === b.getAttribute('data-sel-entry'); });
          render();
        });
      });
      var cta = document.getElementById('ctrl-ta'); if (cta) cta.addEventListener('input', function () { state.controlPrompt = cta.value; state.experiment.controlPromptHash = null; state.observations = []; state.replayResult = null; });
      var vta = document.getElementById('var-ta'); if (vta) vta.addEventListener('input', function () { state.variantPrompt = vta.value; state.experiment.variantPromptHash = null; state.observations = []; state.replayResult = null; });
      var freezeBtn = document.getElementById('freeze-exp-btn');
      if (freezeBtn) freezeBtn.addEventListener('click', async function () {
        try {
          state.experiment.controlPromptHash = await Core.sha256Hex(state.controlPrompt);
          state.experiment.variantPromptHash = await Core.sha256Hex(state.variantPrompt);
          state.experiment.hypothesis = document.getElementById('exp-hyp').value.trim();
          state.experiment.modelConfig.model = document.getElementById('exp-model').value.trim();
          var errors = root.ReactorObservationValidator.validateExperiment(state.experiment);
          if (errors.length) throw new Error(errors.join('; '));
          state.observations = []; state.isSyntheticDemo = false;
          state.statusMsg = 'Control/variant hashes frozen for offline-import matching. No observations imported.';
          state.errMsg = '';
        } catch (e) { state.errMsg = e.message; }
        render();
      });
      var impBtn = document.getElementById('import-obs-btn');
      if (impBtn) impBtn.addEventListener('click', async function () {
        try {
          var arr = JSON.parse(document.getElementById('obs-import-ta').value);
          if (!Array.isArray(arr)) throw new Error('Expected JSON array');
          if (state.experiment.controlPromptHash == null || state.experiment.variantPromptHash == null) throw new Error('EXPERIMENT_PROMPT_HASHES_NOT_SET');
          var errs = await root.ReactorObservationValidator.validateObservations(arr, state.experiment);
          if (errs.length) throw new Error(errs.slice(0,6).join('; '));
          state.isSyntheticDemo = false;
          state.observations = arr;
          state.errMsg = '';
          state.statusMsg = 'Imported ' + arr.length + ' observation records (missing metadata preserved as unknown).';
        } catch (e) { state.errMsg = 'Import failed: ' + e.message; }
        render();
      });
      var chBtn = document.getElementById('add-chal-btn');
      if (chBtn) chBtn.addEventListener('click', function () {
        var rat = (document.getElementById('chal-rat') || {}).value || '';
        if (!rat.trim()) return;
        state.challenges.push({ challengeId: 'CHAL-' + (state.challenges.length + 1), rationale: rat.trim(), status: 'OPEN' });
        render();
      });
      var expCap = document.getElementById('export-cap-btn');
      if (expCap) expCap.addEventListener('click', async function () {
        try { if (state.isSyntheticDemo) throw new Error('SYNTHETIC_DEMO_NOT_EXPORTABLE');
        if (root.ReactorObservationValidator.validateExperiment(state.experiment).length) throw new Error('EXPERIMENT_SCHEMA_INVALID');
        if ((await root.ReactorObservationValidator.validateObservations(state.observations,state.experiment)).length) throw new Error('OBSERVATION_SCHEMA_INVALID');
        var cap = await Cap.buildCapsule({
          sourceRef: Src.buildSourceReference(state.selectedEntry, true),
          experiment: state.experiment,
          controlPrompt: state.controlPrompt,
          variantPrompt: state.variantPrompt,
          dataset: state.experiment.dataset,
          observations: state.observations,
          scores: {},
          claims: [],
          challenges: state.challenges,
          isSyntheticDemo: state.isSyntheticDemo
        });
        var blob = new Blob([JSON.stringify(cap, null, 2)], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a'); a.href = url; a.download = 'evidence-capsule.json';
        document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
        state.statusMsg = 'Exported evidence-capsule.json with SHA-256 checksums.'; state.errMsg = '';
        } catch(e) { state.errMsg = 'Export blocked: ' + e.message; }
        render();
      });
      var capInput = document.getElementById('import-cap-file');
      if (capInput) capInput.addEventListener('change', async function () {
        try {
          var candidate = JSON.parse(await capInput.files[0].text());
          state.replayResult = await Replay.replayCapsule(candidate);
          if (!state.replayResult.valid) state.errMsg = 'Capsule rejected: ' + state.replayResult.errors.join('; ');
          else { state.errMsg = ''; state.statusMsg = 'Offline capsule computational replay completed.'; }
        } catch (e) { state.errMsg = 'Capsule import failed: ' + e.message; }
        render();
      });
      var repBtn = document.getElementById('run-replay-btn');
      if (repBtn) repBtn.addEventListener('click', async function () {
        try { if (state.isSyntheticDemo) throw new Error('SYNTHETIC_DEMO_NOT_EXPORTABLE');
        if (root.ReactorObservationValidator.validateExperiment(state.experiment).length) throw new Error('EXPERIMENT_SCHEMA_INVALID');
        var cap = await Cap.buildCapsule({
          sourceRef: Src.buildSourceReference(state.selectedEntry, true),
          experiment: state.experiment,
          controlPrompt: state.controlPrompt,
          variantPrompt: state.variantPrompt,
          dataset: state.experiment.dataset,
          observations: state.observations,
          scores: {},
          claims: [],
          challenges: state.challenges,
          isSyntheticDemo: state.isSyntheticDemo
        });
        state.replayResult = await Replay.replayCapsule(cap);
        } catch(e) { state.errMsg = 'Replay blocked: ' + e.message; }
        render();
      });
    }

    navBtns.forEach(function (b) { b.addEventListener('click', function () { state.mode = b.getAttribute('data-mode'); state.errMsg = ''; state.statusMsg = ''; render(); }); });
    render();
  };
})(typeof window !== 'undefined' ? window : globalThis);
