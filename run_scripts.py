import sys, os, glob, subprocess

def run_subagent_scripts(cids):
    for cid in cids:
        scratch_dir = f"/Users/neil/.gemini/antigravity-cli/brain/{cid}/scratch"
        scripts = glob.glob(os.path.join(scratch_dir, "*.py"))
        for script in scripts:
            if "read_json" in script:
                continue
            print(f"Running script: {script}")
            res = subprocess.run(["python3", script], capture_output=True, text=True)
            print("STDOUT:", res.stdout)
            if res.stderr:
                print("STDERR:", res.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_scripts.py <cid1> <cid2> ...")
        sys.exit(1)
    run_subagent_scripts(sys.argv[1:])
