import { useState } from "react"
import axios from "axios"

export default function App(){

  const [url,setUrl]=useState("")
  const [result,setResult]=useState(null)
  const [loading,setLoading]=useState(false)
  const [jobId,setJobId]=useState(null)

  const [question,setQuestion]=useState("")
  const [answer,setAnswer]=useState("")

  async function runAudit(){

    setLoading(true)

    const res = await axios.post("http://127.0.0.1:8000/audit",{url})
    const id = res.data.job_id
    setJobId(id)

    const interval=setInterval(async()=>{

      const r=await axios.get(`http://127.0.0.1:8000/result/${id}`)

      if(!r.data.status){
        setResult(r.data)
        setLoading(false)
        clearInterval(interval)
      }

    },2000)
  }

  async function askAI(){

    const res = await axios.post(
      "http://127.0.0.1:8000/explain",
      {job_id:jobId,question}
    )

    setAnswer(res.data.answer)
  }

  return(

    <div className="flex min-h-screen bg-black text-white">

      <div className="flex-1 p-10">

        <div className="flex gap-4 mb-10">

          <input
            value={url}
            onChange={(e)=>setUrl(e.target.value)}
            className="bg-gray-900 p-4 rounded-xl"
            placeholder="Enter URL"
          />

          <button onClick={runAudit}>
            Analyze
          </button>

        </div>

        {loading && <p>Analyzing... 😈</p>}

        {result && (

          <>
            <h2>Score: {result.performance_score}</h2>

            <h3>Suggestions</h3>
            {result.suggestions?.map((s,i)=>
              <p key={i}>{s.issue}</p>
            )}

            <hr/>

            <h3>🤖 Ask PerfAI</h3>

            <input
              value={question}
              onChange={(e)=>setQuestion(e.target.value)}
              className="bg-gray-900 p-3"
              placeholder="Ask AI..."
            />

            <button onClick={askAI}>
              Ask
            </button>

            {answer && <p>{answer}</p>}

          </>
        )}

      </div>

    </div>
  )
}
