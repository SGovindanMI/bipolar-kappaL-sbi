"""Build a separate revision comparison; never inserted into the manuscript/SI."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--previous',type=Path,required=True,help='Previous repository root');a=ap.parse_args()
    old=json.loads((a.previous/'combined/combined_numbers.json').read_text(encoding='utf-8'))
    new=json.loads((ROOT/'combined/combined_numbers.json').read_text(encoding='utf-8'))
    rows=[]
    for key,label in [('n','Corpus records'),('papers','Source papers'),('scored','Reference scored'),('admitted','Reference admitted'),('paired','Reference paired slopes'),('window_papers','Reference paired papers')]:
        rows.append(f'| {label} | {old["v5"][key]:,} | {new["v5"][key]:,} |')
    for key,label in [('n','Six-model common records'),('papers','Six-model common papers')]:
        rows.append(f'| {label} | {old["all_model_common"][key]:,} | {new["all_model_common"][key]:,} |')
    modelrows=[];details={}
    for model in new['models']:
        o=old['corpus'][model];n=new['corpus'][model]
        modelrows.append(f'| {new["short"][model]} | {o["native"]["n"]:,} → {n["native"]["n"]:,} | {o["native"]["CB"][0]:.6f} → {n["native"]["CB"][0]:.6f} | {o["all_model_common"]["CB"][0]:.6f} → {n["all_model_common"]["CB"][0]:.6f} |')
        details[model]={'previous':o,'corrected':n}
    fam=[]
    for f,g in new['family_common']['families'].items():
        og=old['family_common']['families'][f]
        fam.append(f'| {f} | {og["n"]} | {g["n"]} | {g["papers"]} |')
    text=f'''# Corrected dataset compared with the previous project dataset

This report is separate from the final manuscript and Supplementary Information. Those documents use only the corrected cohort. Neither project version is a separately published study.

The correction removes 225 records from the empirical analysis: 101 inconsistent paper/sample associations (including 24 mixed-paper transport triplets) and 124 records whose required transport curves need review because of conflicting temperature values. The 13,031 retained records reproduce the pinned official source export within the declared tolerances. Their transport inputs and saved posterior draws are unchanged; no network retraining or fresh posterior sampling was performed. Every empirical population, bootstrap interval, stratification, figure and table was regenerated after selection. Synthetic validation datasets are unchanged.

| Population | Previous | Corrected |
|---|---:|---:|
{chr(10).join(rows)}

## Six-model results

Values below are median per-curve C minus B log-slope differences over 400–750 K. Arrows show previous → corrected. Native populations differ between models; the common population uses identical curves across all models within each dataset. The dataset populations themselves differ, so these changes are not individual-curve refitting effects.

| Model | Native records | Native C minus B | Common C minus B |
|---|---:|---:|---:|
{chr(10).join(modelrows)}

The maximum absolute change in the six common-set medians is below 0.0012. The principal direction and substantial model dependence persist. This stability does not excuse incorrect source assembly and does not establish a unique physical heat decomposition. The final paper reports the corrected values only.

## Family representation on the common population

| Inherited family label | Previous records | Corrected records | Corrected papers |
|---|---:|---:|---:|
{chr(10).join(fam)}

The pre-specified threshold of 80 common curves is retained. Four named groups and the heterogeneous residual other group qualify for reported effects. The corrected family effects and paired model contrasts are in Supplementary Tables 26 and 27; component slope medians and paired differences are in Tables 28–30.

## Added data checks

Power-factor consistency is evaluated on 8,303 corrected-cohort specimens and zT consistency on 11,972. Median symmetric discrepancies are 1.46% and 2.36%; 646 and 1,185 specimens respectively exceed a 20% best-candidate median discrepancy. These are review flags, not independently validated experimental-error rates. Auxiliary transport availability and source-verification conventions are in Supplementary Tables 31–33.

The exact historical selection rule remains incomplete. An identical-feature pair with two source sample IDs is retained and shares one paper cluster. Family labels and auxiliary-field semantics still require physical interpretation. These limitations are distinct from the repaired paper/sample join and are described without presenting the previous dataset as an alternative primary analysis.

## Traceability

`data/corpus_selection.csv` maps every final row to its previous row identity. `data/corpus_provenance.json` records original and corrected file hashes. `data/source_verification.json` confirms that all final records pass the source checks. `combined/dataset_comparison.json` preserves the underlying model summaries for this comparison. The previous project deliverables remain separate; the new release requires the corrected data archive, not the old one.
'''
    (ROOT/'docs/CORRECTED_VS_PREVIOUS.md').write_text(text,encoding='utf-8')
    (ROOT/'combined/dataset_comparison.json').write_text(json.dumps({'models':details,'previous_population':old['v5']['n'],'corrected_population':new['v5']['n']},indent=2),encoding='utf-8')
    print('Built separate dataset comparison.')
if __name__=='__main__':main()
