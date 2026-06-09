"""Minimal Vercel serverless entry point for NSACA."""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="NSACA API")

@app.get("/")
def root():
    """Serve the landing page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NSACA - NeuroSymbolic AI Architect</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Inter',-apple-system,sans-serif; background:#0c0a1e; color:#e4e4e7; line-height:1.6; overflow-x:hidden; }
    .bg-glow { position:fixed; top:-50%; left:-50%; width:200%; height:200%; background:radial-gradient(ellipse at 25% 15%, rgba(139,92,246,0.08) 0%, transparent 50%), radial-gradient(ellipse at 75% 85%, rgba(59,130,246,0.05) 0%, transparent 50%); pointer-events:none; z-index:0; }
    .grid-bg { position:fixed; inset:0; background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px); background-size:60px 60px; pointer-events:none; z-index:0; }
    .container { max-width:1100px; margin:0 auto; padding:0 24px; position:relative; z-index:1; }
    nav { display:flex; justify-content:space-between; align-items:center; padding:20px 0; border-bottom:1px solid rgba(255,255,255,0.06); }
    .logo { display:flex; align-items:center; gap:10px; font-size:20px; font-weight:700; }
    .logo-icon { width:32px; height:32px; background:linear-gradient(135deg,#8b5cf6,#6366f1); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:16px; }
    .logo-text { background:linear-gradient(135deg,#a78bfa,#818cf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .nav-links { display:flex; gap:24px; }
    .nav-links a { color:#a1a1aa; text-decoration:none; font-size:14px; transition:color .2s; }
    .nav-links a:hover { color:#fff; }
    .hero { text-align:center; padding:100px 0 60px; }
    .hero-badge { display:inline-block; padding:6px 16px; background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.2); border-radius:20px; font-size:12px; color:#a78bfa; margin-bottom:24px; letter-spacing:0.5px; }
    .hero h1 { font-size:52px; font-weight:800; line-height:1.1; margin-bottom:16px; }
    .hero h1 span { background:linear-gradient(135deg,#a78bfa,#818cf8,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero p { font-size:18px; color:#a1a1aa; max-width:680px; margin:0 auto 32px; }
    .hero-buttons { display:flex; gap:12px; justify-content:center; }
    .btn { padding:12px 28px; border-radius:8px; font-size:14px; font-weight:600; text-decoration:none; transition:all .2s; cursor:pointer; border:none; }
    .btn-primary { background:linear-gradient(135deg,#8b5cf6,#6366f1); color:#fff; }
    .btn-primary:hover { transform:translateY(-1px); box-shadow:0 8px 24px rgba(99,102,241,0.3); }
    .btn-secondary { background:rgba(255,255,255,0.05); color:#e4e4e7; border:1px solid rgba(255,255,255,0.1); }
    .btn-secondary:hover { background:rgba(255,255,255,0.1); }
    section { margin-bottom:80px; }
    section h2 { font-size:28px; font-weight:700; text-align:center; margin-bottom:40px; }
    .capabilities-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:20px; }
    .cap-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:16px; padding:28px; transition:all .3s; }
    .cap-card:hover { border-color:rgba(139,92,246,0.3); transform:translateY(-2px); }
    .cap-icon { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px; margin-bottom:16px; }
    .cap-card h3 { font-size:16px; font-weight:600; margin-bottom:8px; }
    .cap-card p { font-size:13px; color:#a1a1aa; }
    .arch-flow { display:flex; justify-content:center; align-items:center; gap:12px; flex-wrap:wrap; padding:32px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:16px; }
    .arch-node { padding:12px 20px; background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.2); border-radius:10px; font-size:13px; font-weight:500; color:#a78bfa; }
    .arch-arrow { color:#52525b; font-size:18px; }
    .endpoints { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:16px; overflow:hidden; }
    .endpoint { display:flex; align-items:center; gap:16px; padding:16px 24px; border-bottom:1px solid rgba(255,255,255,0.04); transition:background .2s; }
    .endpoint:last-child { border-bottom:none; }
    .endpoint:hover { background:rgba(255,255,255,0.02); }
    .method { padding:3px 10px; border-radius:4px; font-size:11px; font-weight:700; text-transform:uppercase; min-width:48px; text-align:center; }
    .method.get { background:rgba(34,197,94,0.15); color:#22c55e; }
    .endpoint-path { font-family:'JetBrains Mono','SF Mono',monospace; font-size:13px; color:#e4e4e7; }
    .endpoint-desc { font-size:13px; color:#71717a; margin-left:auto; }
    .code-block { background:#1a1a2e; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:20px; font-family:'JetBrains Mono','SF Mono',monospace; font-size:13px; line-height:1.7; overflow-x:auto; color:#a5b4fc; }
    .code-block .comment { color:#71717a; }
    .stack-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; }
    .stack-item { padding:16px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; text-align:center; font-size:13px; transition:all .2s; }
    .stack-item:hover { border-color:rgba(139,92,246,0.2); }
    .stack-item strong { display:block; font-size:14px; margin-bottom:4px; color:#e4e4e7; }
    .stack-item span { color:#71717a; font-size:12px; }
    .footer { text-align:center; padding:40px 0; color:#52525b; font-size:13px; border-top:1px solid rgba(255,255,255,0.06); }
    .footer a { color:#a78bfa; text-decoration:none; }
    @media (max-width:768px) {
      .hero h1 { font-size:32px; }
      .nav-links { display:none; }
      .arch-flow { flex-direction:column; }
      .arch-arrow { transform:rotate(90deg); }
    }
  </style>
</head>
<body>
  <div class="bg-glow"></div>
  <div class="grid-bg"></div>
  <div class="container">
    <nav>
      <div class="logo">
        <div class="logo-icon">&#9670;</div>
        <span class="logo-text">NSACA</span>
      </div>
      <div class="nav-links">
        <a href="#capabilities">Capabilities</a>
        <a href="#architecture">Architecture</a>
        <a href="#api">API</a>
        <a href="#stack">Stack</a>
        <a href="https://github.com/Dhruv19duv/nsaca" target="_blank">GitHub</a>
      </div>
    </nav>

    <div class="hero">
      <div class="hero-badge">&#9670; NEUROSYMBOLIC &bull; SELF-IMPROVING &bull; CODE ARCHITECT</div>
      <h1>AI Software Architect that <span>designs &amp; improves itself</span></h1>
      <p>Automatically designs, optimizes, debugs, and self-improves large-scale software systems using LLM reasoning, graph intelligence, reinforcement learning, and compiler-level optimization.</p>
      <div class="hero-buttons">
        <a href="#api" class="btn btn-primary">API Status</a>
        <a href="#architecture" class="btn btn-secondary">Architecture</a>
      </div>
    </div>

    <section id="capabilities">
      <h2>Core Capabilities</h2>
      <div class="capabilities-grid">
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(139,92,246,0.15);">&#9000;</div>
          <h3>Problem Parsing</h3>
          <p>Converts natural language to dependency graphs via knowledge graphs, ASTs, and semantic parsing.</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(59,130,246,0.15);">&#9889;</div>
          <h3>Algorithm Selection</h3>
          <p>Dynamically chooses optimal data structures (segment trees, tries, bloom filters) based on complexity analysis.</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(34,211,238,0.15);">&#127775;</div>
          <h3>Architecture Simulation</h3>
          <p>Monte Carlo Tree Search over software architecture candidates to find the optimal design.</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(52,211,153,0.15);">&#128200;</div>
          <h3>Performance Prediction</h3>
          <p>Bottleneck prediction before execution using learned performance models.</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(248,113,113,0.15);">&#128170;</div>
          <h3>Self-Healing Debugging</h3>
          <p>Adversarial testing + automatic rewriting for robust self-improving systems.</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:rgba(251,191,36,0.15);">&#129504;</div>
          <h3>Memory Engine</h3>
          <p>Vector databases and graph memory for transfer learning across projects.</p>
        </div>
      </div>
    </section>

    <section id="architecture">
      <h2>Architecture Flow</h2>
      <div class="arch-flow">
        <div class="arch-node">Natural Language</div>
        <div class="arch-arrow">&#8594;</div>
        <div class="arch-node">Knowledge Graph</div>
        <div class="arch-arrow">&#8594;</div>
        <div class="arch-node">AST Parser</div>
        <div class="arch-arrow">&#8594;</div>
        <div class="arch-node">Dependency Graph</div>
        <div class="arch-arrow">&#8594;</div>
        <div class="arch-node">MCTS Simulator</div>
        <div class="arch-arrow">&#8594;</div>
        <div class="arch-node">Code Generation</div>
      </div>
    </section>

    <section id="api">
      <h2>API Endpoints</h2>
      <div class="endpoints">
        <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/</span><span class="endpoint-desc">System status &amp; landing page</span></div>
        <div class="endpoint"><span class="method get">GET</span><span class="endpoint-path">/status</span><span class="endpoint-desc">Version &amp; model info</span></div>
      </div>
      <div style="margin-top:24px">
        <div class="code-block">
          <span class="comment"># Check system status</span>
          curl https://nsaca-production.up.railway.app/status
          <span class="comment"># {"version":"0.1.0","model":"gpt-4"}</span>
        </div>
      </div>
    </section>

    <section id="stack">
      <h2>Technology Stack</h2>
      <div class="stack-grid">
        <div class="stack-item"><strong>Python</strong><span>AI Orchestration &bull; LLM &bull; GNN &bull; RL</span></div>
        <div class="stack-item"><strong>Rust</strong><span>High-performance DSA engine</span></div>
        <div class="stack-item"><strong>FastAPI</strong><span>Serving layer</span></div>
        <div class="stack-item"><strong>PyTorch</strong><span>Deep learning models</span></div>
        <div class="stack-item"><strong>Neo4j</strong><span>Knowledge graph</span></div>
        <div class="stack-item"><strong>Docker</strong><span>Deployment</span></div>
      </div>
    </section>

    <div class="footer">
      <a href="https://github.com/Dhruv19duv/nsaca" target="_blank">NSACA</a> &mdash; NeuroSymbolic Autonomous Code Architect
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)


@app.get("/status")
def status():
    return {"version": "0.1.0", "model": "gpt-4"}
