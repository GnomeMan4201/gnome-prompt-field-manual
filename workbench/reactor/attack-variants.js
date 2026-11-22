(function (root) {
  'use strict';
  root.ReactorAttackVariants = {
    createMutationRecord: function (ctrlSurfaces, varSurfaces, mutationType, expectedEffect) {
      var modified = Object.keys(Object.assign({}, ctrlSurfaces, varSurfaces)).filter(function (k) {
        return ctrlSurfaces[k] !== varSurfaces[k];
      }).sort();
      return {
        schemaVersion: 'gnome.reactor.attack-variant.v1',
        modifiedSurfaces: modified,
        mutationType: mutationType,
        isCompoundIntervention: modified.length > 1,
        expectedEffect: expectedEffect
      };
    }
  };
})(typeof window !== 'undefined' ? window : globalThis);
