import React from 'react'
import { Sparkles } from 'lucide-react'

interface Props {
  content: string
}

function renderMarkdown(text: string): React.ReactNode[] {
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let keyCounter = 0

  for (const line of lines) {
    const k = keyCounter++

    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={k} className="text-base font-bold text-white mt-4 mb-1">
          {line.slice(3)}
        </h2>
      )
    } else if (line.startsWith('### ')) {
      elements.push(
        <h3 key={k} className="text-sm font-semibold text-emerald-300 mt-3 mb-1">
          {line.slice(4)}
        </h3>
      )
    } else if (line.startsWith('- ')) {
      const inner = line.slice(2)
      elements.push(
        <li key={k} className="text-sm text-slate-300 leading-relaxed ml-4 list-disc">
          <span dangerouslySetInnerHTML={{ __html: styleBold(styleLinks(inner)) }} />
        </li>
      )
    } else if (line.startsWith('> ')) {
      elements.push(
        <blockquote
          key={k}
          className="border-l-2 border-emerald-600 pl-3 text-sm text-slate-400 italic my-1"
        >
          {line.slice(2)}
        </blockquote>
      )
    } else if (line.trim() === '') {
      elements.push(<div key={k} className="h-1" />)
    } else {
      elements.push(
        <p key={k} className="text-sm text-slate-300 leading-relaxed">
          <span dangerouslySetInnerHTML={{ __html: styleBold(styleCode(line)) }} />
        </p>
      )
    }
  }
  return elements
}

function styleBold(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
}

function styleCode(text: string): string {
  return text.replace(/`(.+?)`/g, '<code class="bg-slate-700 px-1 rounded text-emerald-300 font-mono text-xs">$1</code>')
}

function styleLinks(text: string): string {
  return text.replace(
    /\[(.+?)\]\((.+?)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-indigo-400 underline hover:text-indigo-300">$1</a>'
  )
}

export default function FinalAnswer({ content }: Props) {
  return (
    <div className="fade-in border-2 border-emerald-600/50 bg-emerald-950/20 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3 bg-emerald-900/20 border-b border-emerald-700/30">
        <Sparkles className="w-4 h-4 text-emerald-400" />
        <span className="text-sm font-semibold text-emerald-300">Final Answer</span>
      </div>

      {/* Body */}
      <div className="px-5 py-4 space-y-1">
        {renderMarkdown(content)}
      </div>
    </div>
  )
}
