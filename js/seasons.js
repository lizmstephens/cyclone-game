/**
 * Build a fictional cyclone season by sampling independent WATTCH cases.
 * Cases come from different historical years; this is a training season,
 * not a reconstruction of any actual cyclone season.
 * The number of storms is variable, sampled from a configurable distribution.
 */
export const DEFAULT_SEASON_OPTIONS = Object.freeze({
  stormCountWeights: {2: 10, 3: 20, 4: 25, 5: 20, 6: 15, 7: 10},
  startingBudgetCHF: 150000,
  prepositionCostCHF: 20000,
  distributionCostCHF: 8000
});
function weightedCount(weights, random) {
  const entries=Object.entries(weights).map(([n,w])=>[Number(n),Number(w)]).filter(([n,w])=>Number.isInteger(n)&&n>0&&Number.isFinite(w)&&w>0);
  if(!entries.length)throw Error("At least one positive storm count weight is required.");
  const total=entries.reduce((sum,[,w])=>sum+w,0);
  let pick=random()*total;
  for(const [n,w] of entries){pick-=w;if(pick<0)return n;}
  return entries.at(-1)[0];
}
function shuffled(items, random) {
  const out=items.slice();
  for(let i=out.length-1;i>0;i--){
    const j=Math.min(i,Math.floor(random()*(i+1)));
    [out[i],out[j]]=[out[j],out[i]];
  }
  return out;
}
export function makeSeason(catalogue, options={}, random=Math.random) {
  const cfg={...DEFAULT_SEASON_OPTIONS,...options};
  const scenarios=Array.isArray(catalogue)?catalogue:catalogue?.scenarios;
  if(!Array.isArray(scenarios)||!scenarios.length)throw Error("No WATTCH scenarios supplied.");
  const count=Math.min(scenarios.length, weightedCount(cfg.stormCountWeights,random));
  const chosen=shuffled(scenarios,random).slice(0,count);
  return {
    kind:"fictional-training-season",
    numberOfStorms:chosen.length,
    startingBudgetCHF:cfg.startingBudgetCHF,
    remainingBudgetCHF:cfg.startingBudgetCHF,
    costsCHF:{preposition:cfg.prepositionCostCHF,distribution:cfg.distributionCostCHF},
    completedStorms:0,
    storms:chosen.map((s,i)=>({
      slot:i+1,
      scenarioId:s.id,
      historicalInitialization:s.initialization,
      title:"Storm "+(i+1),
      summary:s.summary,
      scenario:s
    }))
  };
}
export async function loadCatalogue(url="./data/scenarios-100.json"){
  const response=await fetch(url);
  if(!response.ok)throw Error("Could not load WATTCH scenario library ("+response.status+").");
  const catalogue=await response.json();
  if(!Array.isArray(catalogue.scenarios)||!catalogue.scenarios.length)throw Error("Scenario library is empty.");
  return catalogue;
}
