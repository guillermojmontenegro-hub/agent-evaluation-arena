const candidates = [
  { rank: "01", name: "Atlas", model: "gpt-5 · prompt v12", score: 91, range: "87–94%", cost: "$0.041", latency: "4.2s", color: "#c7ff5e" },
  { rank: "02", name: "Nova", model: "claude-sonnet · prompt v8", score: 86, range: "81–90%", cost: "$0.035", latency: "3.8s", color: "#f6c85f" },
  { rank: "03", name: "Forge", model: "gemini-pro · prompt v6", score: 79, range: "73–84%", cost: "$0.028", latency: "5.1s", color: "#c9b8ff" },
];

const trace = [
  { time: "00:00.000", title: "task.started", detail: "repo_patch_017 · seed 42", tone: "lime" },
  { time: "00:00.184", title: "tool.call", detail: "read_file(src/parser.py)", tone: "violet" },
  { time: "00:01.421", title: "candidate.output", detail: "+ 38 lines · − 11 lines", tone: "gold" },
  { time: "00:04.182", title: "grader.completed", detail: "6 / 6 assertions passed", tone: "lime" },
];

export default function Page() {
  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#"><span>Æ</span> AGENT ARENA <small>/ LAB</small></a>
        <nav><a className="active" href="#leaderboard">Leaderboard</a><a href="#runs">Runs</a><a href="#traces">Traces</a><a href="/docs">API</a></nav>
        <div className="system"><i /> SYSTEM ONLINE <kbd>⌘ K</kbd></div>
      </header>

      <section className="hero">
        <div className="eyebrow">EVALUATION / SUITE-042</div>
        <h1>Measure agents.<br/><em>Trust the results.</em></h1>
        <p>Same tasks. Same budget. Reproducible evidence.<br/>Compare capability without the guesswork.</p>
        <div className="heroActions"><button>▶ &nbsp; NEW EVALUATION</button><a href="#traces">EXPLORE LAST RUN ↘</a></div>
        <div className="runStamp"><span>LAST SNAPSHOT</span><b>2026.07.10 / 14:32 UTC</b><small>128 TASKS · 3 CANDIDATES · SEED 42</small></div>
      </section>

      <section className="metrics" id="runs">
        <article><span>RUNS COMPLETED</span><strong>384</strong><small>+24 THIS WEEK</small></article>
        <article><span>TASK EXECUTIONS</span><strong>49,152</strong><small>100% REPLAYABLE</small></article>
        <article><span>MEDIAN SUCCESS</span><strong>86.3<sup>%</sup></strong><small>± 4.1% CI</small></article>
        <article><span>TOTAL SPEND</span><strong>$13.28</strong><small>$0.034 / RUN</small></article>
      </section>

      <section className="board" id="leaderboard">
        <div className="sectionHead">
          <div><span className="eyebrow">CURRENT SNAPSHOT</span><h2>Leaderboard</h2></div>
          <div className="filters"><button>Suite: coding-core ▾</button><button>Budget: standard ▾</button><button>↗ EXPORT</button></div>
        </div>
        <div className="tableHead"><span>RANK / CANDIDATE</span><span>SUCCESS RATE · 95% CI</span><span>COST / TASK</span><span>LATENCY P50</span><span>RUN</span></div>
        {candidates.map((candidate) => (
          <article className="candidate" key={candidate.name}>
            <div className="candidateName"><b>{candidate.rank}</b><i style={{background: candidate.color}}/><span><strong>{candidate.name}</strong><small>{candidate.model}</small></span></div>
            <div className="score"><span><strong>{candidate.score}%</strong><small>{candidate.range}</small></span><div><i style={{width: `${candidate.score}%`, background: candidate.color}} /></div></div>
            <strong className="mono">{candidate.cost}</strong><strong className="mono">{candidate.latency}</strong><button className="round">↗</button>
          </article>
        ))}
        <p className="budgetNote"><span>◉</span> Rankings only compare runs with identical budgets <b>steps=20 · tokens=8k · timeout=120s</b></p>
      </section>

      <section className="replay" id="traces">
        <div className="replayIntro"><span className="eyebrow">TRACE / RUN-A8F2</span><h2>Every decision,<br/>accounted for.</h2><p>Replay the complete execution timeline. Inputs, tool calls, outputs and grades—without secrets.</p><button>OPEN FULL REPLAY ↗</button></div>
        <div className="terminal">
          <header><span><i/><i/><i/></span><b>run-a8f2.trace</b><small>COMPLETED</small></header>
          <div className="terminalMeta"><span>CANDIDATE <b>Atlas</b></span><span>TASK <b>repo_patch_017</b></span><span>RESULT <b className="pass">PASS</b></span></div>
          <div className="events">
            {trace.map((event, index) => <div className="event" key={event.time}><time>{event.time}</time><i className={event.tone}/><span><strong>{event.title}</strong><small>{event.detail}</small></span>{index === 3 && <b className="grade">1.0</b>}</div>)}
          </div>
          <footer><span>runner@1.0.0</span><span>grader@1.0.0</span><span>dataset@3.2.1</span><span>SHA 8e41c2</span></footer>
        </div>
      </section>

      <footer className="footer"><a className="brand" href="#"><span>Æ</span> AGENT ARENA</a><p>OPEN EVALUATION INFRASTRUCTURE<br/>BUILT FOR REPRODUCIBILITY.</p><div><a href="/docs">DOCS</a><a href="https://github.com/guillermojmontenegro-hub/agent-evaluation-arena">GITHUB</a><a href="/health">STATUS</a></div></footer>
    </main>
  );
}
