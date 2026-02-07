import { useState } from "react"
import axios from "axios"

export default function App(){

  const [url,setUrl] = useState("")
  const [result,setResult] = useState(null)
  const [loading,setLoading] = useState(false)

  async function runAudit(){

    setLoading(true)

    const res = await axios.post("http://127.0.0.1:8000/audit",{url})
    const jobId = res.data.job_id

    const interval = setInterval(async ()=>{

      const r = await axios.get(`http://127.0.0.1:8000/result/${jobId}`)

      if(!r.data.status){
        setResult(r.data)
        setLoading(false)
        clearInterval(interval)
      }

    },2000)
  }

  return(

    <div className="flex min-h-screen bg-gradient-to-br from-gray-950 to-black text-white">

      {/* SIDEBAR */}
      <div className="w-64 bg-black/40 backdrop-blur-xl border-r border-gray-800 p-6">

        <h1 className="text-xl font-bold mb-10">
          ⚡ PerfAI
        </h1>

        <div className="space-y-4 text-gray-400">
          <p>Dashboard</p>
          <p>History</p>
          <p>Settings</p>
        </div>

      </div>


      {/* MAIN */}
      <div className="flex-1 p-10">

        {/* URL INPUT */}
        <div className="flex gap-4 mb-10">
          <input
            value={url}
            onChange={(e)=>setUrl(e.target.value)}
            placeholder="Enter website URL"
            className="bg-gray-900 p-4 rounded-xl w-96 border border-gray-700"
          />

          <button
            onClick={runAudit}
            className="bg-purple-600 hover:bg-purple-700 px-6 rounded-xl"
          >
            Analyze
          </button>
        </div>

        {loading && <p>Analyzing performance... 😈</p>}

        {result && (

          <>
            {/* HERO SCORE */}
            <div className="bg-black/30 backdrop-blur-xl border border-gray-800 p-10 rounded-2xl mb-10 flex items-center gap-12">

              <ScoreRing score={result.performance_score}/>

              <div>
                <p className="text-gray-400">Predicted Score</p>
                <h2 className="text-5xl font-bold">
                  {result.predicted_score}
                </h2>
              </div>

            </div>

            {/* METRICS GRID */}
            <div className="grid grid-cols-4 gap-6 mb-10">

              <Metric title="LCP" value={Math.round(result.lcp)+" ms"} />
              <Metric title="CLS" value={result.cls} />
              <Metric title="TBT" value={result.tbt} />
              <Metric title="Performance" value={result.performance_score} />

            </div>

            {/* INSIGHTS */}
            <Panel title="🧠 AI Insights">
              {result.insights?.map((i,index)=>(
                <p key={index}>{i}</p>
              ))}
            </Panel>

            {/* SUGGESTIONS */}
            <Panel title="🛠 Suggested Fixes">

              {result.suggestions?.map((s,index)=>(

                <div key={index} className="mb-6">

                  <p className="font-bold">{s.issue}</p>
                  <p className="text-gray-400">{s.fix}</p>

                </div>

              ))}

            </Panel>

            {/* CODE FIXES */}
            <Panel title="💻 Code Fix Examples">

              {result.code_fixes?.map((c,index)=>(

                <div key={index} className="mb-6">

                  <p className="font-bold">{c.issue}</p>

                  {c.code_fix_html &&
                    <pre className="bg-black p-3 rounded mt-2">{c.code_fix_html}</pre>
                  }

                  {c.code_fix_react &&
                    <pre className="bg-black p-3 rounded mt-2">{c.code_fix_react}</pre>
                  }

                </div>

              ))}

            </Panel>

          </>
        )}

      </div>

    </div>
  )
}


/* ---------------- COMPONENTS ---------------- */

function Metric({title,value}){

  return(

    <div className="bg-black/30 backdrop-blur-xl border border-gray-800 p-6 rounded-xl">
      <p className="text-gray-400">{title}</p>
      <h2 className="text-2xl font-bold">{value}</h2>
    </div>

  )
}


function Panel({title,children}){

  return(

    <div className="bg-black/30 backdrop-blur-xl border border-gray-800 p-6 rounded-xl mb-10">
      <h3 className="text-xl mb-4">{title}</h3>
      {children}
    </div>

  )
}


function ScoreRing({score}){

  const color =
    score > 80 ? "text-green-400"
    : score > 50 ? "text-yellow-400"
    : "text-red-400"

  return(

    <div className={`text-7xl font-bold ${color}`}>
      {score}
    </div>

  )
}
