import { Loader2 } from 'lucide-react'
import type { AgentStep } from '../App'
import ToolCallCard from './ToolCallCard'
import FinalAnswer from './FinalAnswer'

interface Props {
  steps: AgentStep[]
  isLoading: boolean
}

const TOOL_EMOJIS: Record<string, string> = {
  web_search: '🔍',
  text_summarizer: '📝',
  fact_checker: '✅',
  calculator: '🧮',
}

export default function ThoughtStream({ steps, isLoading }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
        Agent Reasoning Steps
      </h2>

      {steps.map((step, idx) => {
        if (step.type === 'thought') {
          return (
            <div
              key={idx}
              className="fade-in flex gap-3 bg-slate-800/60 border border-slate-700 rounded-xl px-4 py-3"
            >
              <span className="text-lg leading-none mt-0.5">💭</span>
              <p className="text-sm text-slate-300 italic leading-relaxed">{step.content}</p>
            </div>
          )
        }

        if (step.type === 'tool_call') {
          const emoji = TOOL_EMOJIS[step.tool ?? ''] ?? '🔧'
          return (
            <ToolCallCard
              key={idx}
              toolName={step.tool ?? 'unknown'}
              emoji={emoji}
              input={step.input}
              output={step.output}
            />
          )
        }

        if (step.type === 'final_answer') {
          return <FinalAnswer key={idx} content={step.content ?? ''} />
        }

        return null
      })}

      {isLoading && (
        <div className="fade-in flex items-center gap-2 px-4 py-3 bg-slate-800/40 border border-slate-700/50 rounded-xl">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-sm text-slate-400">Agent is reasoning…</span>
        </div>
      )}
    </div>
  )
}
