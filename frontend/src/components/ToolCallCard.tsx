import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface Props {
  toolName: string
  emoji: string
  input: unknown
  output: unknown
}

function formatValue(value: unknown): string {
  if (typeof value === 'string') return value
  return JSON.stringify(value, null, 2)
}

function isObject(value: unknown): boolean {
  return typeof value === 'object' && value !== null
}

export default function ToolCallCard({ toolName, emoji, input, output }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="fade-in border border-indigo-900/60 bg-indigo-950/30 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-indigo-900/20">
        <div className="flex items-center gap-2">
          <span className="text-base">{emoji}</span>
          <span className="text-sm font-semibold text-indigo-300 font-mono">{toolName}</span>
          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">tool call</span>
        </div>
        <button
          onClick={() => setExpanded((p) => !p)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          {expanded ? (
            <>Hide details <ChevronUp className="w-3.5 h-3.5" /></>
          ) : (
            <>Show details <ChevronDown className="w-3.5 h-3.5" /></>
          )}
        </button>
      </div>

      {/* Input preview (always visible) */}
      <div className="px-4 py-2 border-t border-indigo-900/40">
        <p className="text-xs text-slate-500 mb-1 uppercase tracking-wide">Input</p>
        <div className="text-xs text-slate-300 font-mono bg-slate-900/50 rounded-lg px-3 py-2 overflow-x-auto scrollbar-thin max-h-24">
          {isObject(input) ? (
            <pre className="whitespace-pre-wrap break-all">{formatValue(input)}</pre>
          ) : (
            <span>{String(input)}</span>
          )}
        </div>
      </div>

      {/* Output (collapsible) */}
      {expanded && (
        <div className="px-4 pb-3 border-t border-indigo-900/40">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wide mt-2">Output</p>
          <div className="text-xs text-slate-200 font-mono bg-slate-900/70 rounded-lg px-3 py-2 overflow-x-auto scrollbar-thin max-h-64">
            {isObject(output) ? (
              <pre className="whitespace-pre-wrap break-all">{formatValue(output)}</pre>
            ) : (
              <span className="whitespace-pre-wrap">{String(output)}</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
