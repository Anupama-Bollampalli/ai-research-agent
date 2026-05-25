import { useState, useRef } from 'react'
import { Brain, Search, ChevronRight, Loader2 } from 'lucide-react'
import ThoughtStream from './components/ThoughtStream'

export interface AgentStep {
  type: 'thought' | 'tool_call' | 'final_answer' | 'done'
  content?: string
  tool?: string
  input?: unknown
  output?: unknown
}

const EXAMPLE_QUERIES = [
  'What are the latest advances in retrieval-augmented generation (RAG) systems?',
  'How do modern data pipelines handle real-time streaming with Apache Kafka and Flink?',
  'Compare vector databases: Pinecone vs Weaviate vs Chroma for production ML systems',
  'What is the best approach for fine-tuning large language models on domain-specific data?',
  'Explain the differences between GitOps with ArgoCD and traditional CI/CD pipelines',
]

export default function App() {
  const [question, setQuestion] = useState('')
  const [steps, setSteps] = useState<AgentStep[]>([])
  const [isResearching, setIsResearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const handleResearch = async () => {
    if (!question.trim() || isResearching) return

    setSteps([])
    setError(null)
    setIsResearching(true)

    abortRef.current = new AbortController()

    try {
      const apiBase = import.meta.env.VITE_API_URL ?? ''
      const response = await fetch(`${apiBase}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
        signal: abortRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const raw = line.slice(6).trim()
            if (!raw || raw === '[DONE]') continue
            try {
              const step: AgentStep = JSON.parse(raw)
              if (step.type === 'done') {
                setIsResearching(false)
              } else {
                setSteps((prev) => [...prev, step])
              }
            } catch {
              // Skip malformed lines
            }
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err.message ?? 'An unexpected error occurred.')
      }
    } finally {
      setIsResearching(false)
    }
  }

  const handleStop = () => {
    abortRef.current?.abort()
    setIsResearching(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleResearch()
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800/60 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-indigo-600">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white leading-none">AI Research Agent</h1>
            <p className="text-xs text-slate-400 mt-0.5">ReAct · Reason · Act · Observe</p>
          </div>
        </div>
      </header>

      <div className="flex flex-1 max-w-7xl mx-auto w-full px-4 py-6 gap-6">
        {/* Sidebar */}
        <aside className="hidden lg:flex flex-col w-72 shrink-0 gap-4">
          <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Example Queries
            </h2>
            <ul className="space-y-2">
              {EXAMPLE_QUERIES.map((q, i) => (
                <li key={i}>
                  <button
                    onClick={() => setQuestion(q)}
                    className="w-full text-left text-sm text-slate-300 hover:text-white bg-slate-700/50 hover:bg-slate-700 rounded-lg px-3 py-2.5 transition-colors flex items-start gap-2 group"
                  >
                    <ChevronRight className="w-3.5 h-3.5 mt-0.5 text-indigo-400 shrink-0 group-hover:translate-x-0.5 transition-transform" />
                    <span className="leading-snug">{q}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Available Tools
            </h2>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-center gap-2"><span>🔍</span> web_search</li>
              <li className="flex items-center gap-2"><span>📝</span> text_summarizer</li>
              <li className="flex items-center gap-2"><span>✅</span> fact_checker</li>
              <li className="flex items-center gap-2"><span>🧮</span> calculator</li>
            </ul>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 flex flex-col gap-6 min-w-0">
          {/* Input area */}
          <div className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Research Question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a research question… e.g. What are the best practices for building RAG pipelines?"
              rows={3}
              className="w-full bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-sm"
            />
            <div className="flex items-center justify-between mt-3">
              <p className="text-xs text-slate-500">Press ⌘+Enter to run</p>
              <div className="flex gap-2">
                {isResearching && (
                  <button
                    onClick={handleStop}
                    className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors"
                  >
                    Stop
                  </button>
                )}
                <button
                  onClick={handleResearch}
                  disabled={!question.trim() || isResearching}
                  className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-colors"
                >
                  {isResearching ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Researching…
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Research
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded-xl px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {/* Steps stream */}
          {steps.length > 0 && (
            <ThoughtStream steps={steps} isLoading={isResearching} />
          )}

          {/* Empty state */}
          {steps.length === 0 && !isResearching && !error && (
            <div className="flex-1 flex flex-col items-center justify-center py-16 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center">
                <Brain className="w-8 h-8 text-slate-500" />
              </div>
              <div>
                <p className="text-slate-400 font-medium">No research yet</p>
                <p className="text-slate-600 text-sm mt-1">
                  Enter a question above or pick an example from the sidebar
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
