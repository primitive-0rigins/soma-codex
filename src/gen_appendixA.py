#!/usr/bin/env python3
"""Convert the source theorem corpus into the Appendix A HTML fragment,
faithfully, marking the load-bearing entries used in Book III."""
import html, os, re

SRC_MD = "/home/evolution/Desktop/predictive-chaos-bio-ecosystem-theorems.md"
OUT = "/home/evolution/Desktop/SOMA-Codex/src/_appendixA.html"

# entries wired into an organ in Book III (load-bearing)
LOAD_BEARING = {
    "bayes' theorem", "markov chains", "hidden markov models", "kalman filter",
    "exponential moving average", "logistic function", "entropy", "queueing theory",
    "multi-armed bandit", "thompson sampling", "pid control", "hysteresis",
    "information gain", "survival analysis", "active inference / free energy principle",
    "conformal prediction", "merkle trees", "hash chains", "vector clocks",
    "lamport clocks", "crdts", "little's law", "viability theory", "circuit breaker",
    "backpressure", "drift detection", "cusum", "pagerank",
    "optimal transport / wasserstein distance", "causal emergence", "negative selection",
    "danger model", "topological sort", "critical path method", "constraint satisfaction",
    "cellular sheaf theory", "percolation theory",
}

def esc(s): return html.escape(s.strip())

def main():
    lines = open(SRC_MD, encoding="utf-8").read().splitlines()
    out = []
    i = 0
    n = len(lines)
    n_total = 0
    n_lb = 0
    while i < n:
        ln = lines[i].rstrip()
        if ln.startswith("# ") and not ln.startswith("## "):
            i += 1; continue  # skip the document H1
        if ln.startswith("## "):
            title = ln[3:].strip()
            # the final "Best Fit" section contains a fenced code block: render verbatim
            if title.lower().startswith("best fit"):
                out.append('<h3>%s</h3>' % esc(title))
                # gather until end / fence
                block = []
                i += 1
                while i < n and not lines[i].startswith("```"):
                    i += 1
                if i < n and lines[i].startswith("```"):
                    i += 1
                    while i < n and not lines[i].startswith("```"):
                        block.append(lines[i]); i += 1
                    if i < n: i += 1
                out.append('<pre class="diagram">%s</pre>' % esc("\n".join(block)))
                continue
            out.append('<h3>%s</h3>' % esc(title))
            i += 1; continue
        if ln.startswith("### "):
            name = ln[4:].strip()
            n_total += 1
            star = ""
            if name.lower() in LOAD_BEARING:
                star = ' <span style="color:#1f7a44;font-weight:bold">&#9733; load-bearing</span>'
                n_lb += 1
            # collect description + use lines until next heading
            i += 1
            desc, use = [], []
            mode = "desc"
            while i < n and not lines[i].startswith("#"):
                t = lines[i].strip()
                if t.lower().startswith("use:"):
                    mode = "use"; use.append(t[4:].strip())
                elif t:
                    (desc if mode == "desc" else use).append(t)
                i += 1
            out.append('<h4>%s%s</h4>' % (esc(name), star))
            if desc:
                out.append('<p>%s</p>' % esc(" ".join(desc)))
            if use:
                out.append('<p class="small"><b>Use in SOMA:</b> %s</p>' % esc(" ".join(use)))
            continue
        i += 1
    header = ('<p class="small">%d ideas, reproduced faithfully from the source corpus. '
              'The %d marked <span style="color:#1f7a44;font-weight:bold">&#9733; load-bearing</span> '
              'are wired into an organ in Book III; the rest are generative analogies and open '
              'conjectures, kept for the design imagination and labeled honestly as such.</p>'
              % (n_total, n_lb))
    open(OUT, "w", encoding="utf-8").write(header + "\n" + "\n".join(out) + "\n")
    print("wrote %s — %d entries, %d load-bearing" % (OUT, n_total, n_lb))

if __name__ == "__main__":
    main()
