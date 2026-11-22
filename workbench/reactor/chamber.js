(function(){'use strict';
const input=document.getElementById('pairs'),output=document.getElementById('result');
document.getElementById('evaluate').addEventListener('click',()=>{
 try{const value=JSON.parse(input.value);const result=globalThis.ReactorAttributionEngine.attributeTrials(value);output.textContent=JSON.stringify(result,null,2)}
 catch(err){output.textContent='INVALID INPUT: '+String(err.message||err)}
});
document.getElementById('load-demo').addEventListener('click',()=>{
 input.value=JSON.stringify([{trialId:'QA-1',inputId:'I-1',comparable:true,control:{outputText:'baseline okay'},variant:{outputText:'variant fails'},controlDisposition:'Supported pass',variantDisposition:'Supported failure'}],null,2);
 output.textContent='SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE. Select Inspect attribution.';
});
})();
