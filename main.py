import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from dotenv import load_dotenv
import anthropic
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors
RDLogger.DisableLog("rdApp.*")

load_dotenv()
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))


def compute_admet(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}"}
    return {
        "mw": round(Descriptors.MolWt(mol), 2),
        "logp": round(Descriptors.MolLogP(mol), 2),
        "tpsa": round(rdMolDescriptors.CalcTPSA(mol), 2),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "rotbonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "rings": rdMolDescriptors.CalcNumRings(mol),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
    }


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.input).head(args.n)
    # Compute ADMET locally
    props_table = []
    for _, row in df.iterrows():
        props = compute_admet(row["smiles"])
        props["compound_name"] = row["compound_name"]
        props["smiles"] = row["smiles"]
        props["pic50"] = row["pic50"]
        props_table.append(props)

    props_text = json.dumps(props_table, indent=2)

    prompt = (
        "You are a drug discovery ADMET reviewer. Review these compounds' properties and provide a risk assessment.\n\n"
        f"Computed ADMET properties:\n{props_text}\n\n"
        "For each compound, respond in JSON array format:\n"
        '[{"compound_name": "...", "risk_level": "low|medium|high", '
        '"flags": ["list of ADMET concerns"], '
        '"recommendation": "one sentence recommendation"}]'
    )

    print(f"\nPhase 64 — Claude Reviewing ADMET Flags")
    print(f"Model: {args.model} | Compounds: {args.n}\n")

    # Local validation done, one API call
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=args.model, max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text = block.text
            break

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    reviews = []
    if json_match:
        try:
            reviews = json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")

    for r in reviews:
        print(f"  {r.get('compound_name','?'):20s} | risk={r.get('risk_level','?'):6s} | flags={r.get('flags',[])} | {r.get('recommendation','')[:60]}")

    usage = response.usage
    cost = (usage.input_tokens / 1e6 * 0.80) + (usage.output_tokens / 1e6 * 4.0)

    report = f"Phase 64 — ADMET Review\n{'='*40}\nModel: {args.model}\nCompounds: {args.n}\nReviews: {len(reviews)}\nInput: {usage.input_tokens} | Output: {usage.output_tokens}\nCost: ${cost:.4f}\n"
    print(f"\n{report}")

    with open(os.path.join(args.output_dir, "admet_review.json"), "w") as f:
        json.dump({"properties": props_table, "reviews": reviews}, f, indent=2)
    with open(os.path.join(args.output_dir, "admet_report.txt"), "w") as f:
        f.write(report)
    print("Done.")


if __name__ == "__main__":
    main()
