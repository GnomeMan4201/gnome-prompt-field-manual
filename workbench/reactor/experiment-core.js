(function (root) {
  'use strict';
  async function sha256Hex(str) {
    if (typeof crypto !== 'undefined' && crypto.subtle && typeof TextEncoder !== 'undefined') {
      var buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(str)));
      return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
    }
    throw new Error('SHA256_UNAVAILABLE: Web Crypto is required; use HTTPS or localhost.');
  }
  function computeLineDiff(textA, textB) {
    var a = String(textA || '').split('\n'), b = String(textB || '').split('\n');
    var m = a.length, n = b.length, dp = [];
    for (var i = 0; i <= m; i++) dp[i] = new Array(n + 1).fill(0);
    for (var i2 = m - 1; i2 >= 0; i2--) {
      for (var j2 = n - 1; j2 >= 0; j2--) {
        dp[i2][j2] = a[i2] === b[j2] ? 1 + dp[i2 + 1][j2 + 1] : Math.max(dp[i2 + 1][j2], dp[i2][j2 + 1]);
      }
    }
    var out = [], x = 0, y = 0;
    while (x < m && y < n) {
      if (a[x] === b[y]) { out.push({ type: 'ctx', line: a[x] }); x++; y++; }
      else if (dp[x + 1][y] >= dp[x][y + 1]) { out.push({ type: 'del', line: a[x++] }); }
      else { out.push({ type: 'add', line: b[y++] }); }
    }
    while (x < m) out.push({ type: 'del', line: a[x++] });
    while (y < n) out.push({ type: 'add', line: b[y++] });
    return out;
  }
  root.ReactorExperimentCore = { sha256Hex: sha256Hex, computeLineDiff: computeLineDiff };
})(typeof window !== 'undefined' ? window : globalThis);
