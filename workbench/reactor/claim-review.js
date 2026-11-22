(function (root) {
  'use strict';
  root.ReactorClaimReview = {
    reviewClaim: function (claim, action, separateExpId) {
      var errs = [];
      if (action === 'CONFIRM_WITHIN_SCOPE' && (!claim.supportingEvidence || !claim.supportingEvidence.length)) errs.push('CANNOT_CONFIRM_WITHOUT_EVIDENCE');
      if (action === 'RECORD_INDEPENDENT_REPRODUCTION' && (!separateExpId || separateExpId === claim.experimentId)) errs.push('REPRODUCTION_REQUIRES_SEPARATE_EXPERIMENT_ID');
      return { ok: errs.length === 0, errors: errs };
    }
  };
})(typeof window !== 'undefined' ? window : globalThis);
