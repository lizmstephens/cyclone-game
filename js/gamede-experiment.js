/* Experimental Gamede daily forecast reconstruction.
 * Source: data/scenarios.json, event 2007_tr0013.
 * This scenario has ONE original WATTCH initialization (2007-02-21).
 * These daily updates are SYNTHETIC, not independent WATTCH forecasts.
 * The reference track is used after issuance: NOT suitable for forecast verification.
 * Original ensemble trajectories remain untouched.
 */
export function buildGamedeDailyForecasts(scenario, options={}) {
  if (scenario.event_id !== "2007_tr0013") throw Error("Expected Gamede 2007");
  const day=86400000, half=day/2;
  const time=s=>Date.parse(String(s).replace(" ","T")+"Z");
  const stamp=t=>new Date(t).toISOString().slice(0,16).replace("T"," ");
  const tracks=scenario.forecast_tracks;
  const ref=scenario.reference_track;
  const point=(arr,t)=>{
    if (!arr?.length || t<time(arr[0][0]) || t>time(arr[arr.length-1][0])) return null;
    for(let i=0;i<arr.length-1;i++){
      const a=arr[i],b=arr[i+1],ta=time(a[0]),tb=time(b[0]);
      if(ta<=t&&t<=tb){
        const f=tb===ta?0:(t-ta)/(tb-ta);
        return [1,2,3].map(k=>+a[k]+f*(+b[k]-+a[k]));
      }
    }
    return arr.length&&time(arr.at(-1)[0])===t?arr.at(-1).slice(1,4):null;
  };
  const init=time(scenario.initialization+" 00:00");
  const last=Math.min(time(ref.at(-1)[0]),init+11*day);
  const end=Math.min(last,init+(options.days??9)*day);
  const result=[];
  for(let issue=init;issue<=end;issue+=day){
    const origin=point(ref,issue);
    if(!origin)continue;
    const forecast_tracks=tracks.map((m,memberIndex)=>{
      const points=[];
      for(let lead=0;lead<=7*day;lead+=half){
        const valid=issue+lead,original=point(m.points,valid),truth=point(ref,valid);
        if(!original||!truth)break;
        const positions=tracks.map(x=>point(x.points,valid)).filter(Boolean);
        if(positions.length<3)break;
        const mean=[0,1,2].map(k=>positions.reduce((a,p)=>a+p[k],0)/positions.length);
        // Retain the original ensemble's member-specific deviations from its centre.
        // All members start at the observed reference location, then fan out.
        const ramp=1-Math.exp(-lead/(1.2*day));
        // Scale declines with each successive issue to emulate improved knowledge
        // of a fixed future event; this is an explicit training assumption.
        const age=(issue-init)/day;
        const scale=Math.max(0.48,1-0.055*age);
        const lat=truth[0]+(original[0]-mean[0])*ramp*scale;
        const lon=truth[1]+(original[1]-mean[1])*ramp*scale;
        const wind=lead===0?origin[2]:Math.max(0,truth[2]+(original[2]-mean[2])*ramp*scale);
        points.push([stamp(valid),+lat.toFixed(3),+lon.toFixed(3),+wind.toFixed(2)]);
      }
      return {member:m.member,points};
    }).filter(m=>m.points.length>=2);
    result.push({issue_time:stamp(issue),source:issue===init?"synthetic reanchoring of original WATTCH issue":"synthetic reference-anchored reconstruction",reference_position:origin,forecast_tracks});
  }
  return {event_id:scenario.event_id,storm_name:scenario.storm_name,
    original_initialization:scenario.initialization,method:"synthetic reference-anchored ensemble perturbations",
    warning:"Uses future reference track; not an archived forecast or a scientifically valid hindcast. Only one original WATTCH initialization available.",
    forecasts:result};
}
