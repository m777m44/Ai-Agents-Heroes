import { useRef, useState, type ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Check, Copy } from 'lucide-react';
import type { Lang } from '../types';
import { t } from '../i18n';

function CodeBlock({ children }: { children?: ReactNode }) {
  const ref = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);
  const lang = useMemoLang(ref);
  return (
    <div className="codeblock">
      <div className="codeblock-head">
        <span>{lang}</span>
        <button
          className="icon-btn small"
          onClick={() => {
            void navigator.clipboard?.writeText(ref.current?.innerText ?? '');
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          }}
          title="copy"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
        </button>
      </div>
      <pre ref={ref}>{children}</pre>
    </div>
  );
}

function useMemoLang(ref: React.RefObject<HTMLPreElement | null>): string {
  const cls = ref.current?.querySelector('code')?.className ?? '';
  const m = cls.match(/language-([\w-]+)/);
  return m ? m[1] : 'text';
}

export function Markdown({ text, lang }: { text: string; lang: Lang }) {
  return (
    <div className="md" dir="auto">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre: ({ children }) => <CodeBlock>{children}</CodeBlock>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {text || t(lang, 'emptyTurn')}
      </ReactMarkdown>
    </div>
  );
}
