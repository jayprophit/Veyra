import { FormEvent, useMemo, useState } from "react";
import { Bot, ChevronLeft, ChevronRight, Globe, Loader2, Sparkles } from "lucide-react";

type ResearchPage = {
  document_id: string;
  url: string;
  title: string;
  created_at: string;
  page: number;
  page_count: number;
  page_size: number;
  has_previous: boolean;
  has_next: boolean;
  text: string;
  source_pages?: SourcePage[];
};

type ChatResponse = {
  content: string;
  model: string;
  provider: string;
};

type SourcePage = {
  sequence: number;
  url: string;
  title: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function VeyraResearchReader() {
  const [url, setUrl] = useState("https://example.com");
  const [document, setDocument] = useState<ResearchPage | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [sourcePages, setSourcePages] = useState<SourcePage[]>([]);
  const [followPagination, setFollowPagination] = useState(true);
  const [maxSourcePages, setMaxSourcePages] = useState(5);
  const [loading, setLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [error, setError] = useState<string>("");

  const pageLabel = useMemo(() => {
    if (!document) return "No document loaded";
    return `Page ${document.page} of ${document.page_count}`;
  }, [document]);

  async function crawlUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSummary("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/research/crawl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url,
          page_size: 1400,
          follow_pagination: followPagination,
          max_source_pages: maxSourcePages,
        }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Unable to crawl this URL");
      setDocument(body);
      setSourcePages(body.source_pages ?? []);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to crawl this URL");
    } finally {
      setLoading(false);
    }
  }

  async function loadPage(page: number) {
    if (!document) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/research/documents/${document.document_id}?page=${page}`,
      );
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Unable to load page");
      setDocument(body);
      setSummary("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load page");
    } finally {
      setLoading(false);
    }
  }

  async function summarizeCurrentPage() {
    if (!document) return;
    setSummarizing(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: `Summarize the following research page in concise bullet points:\n\n${document.text}`,
          system_prompt:
            "You are a cautious research assistant. State what the source says and do not invent missing facts.",
          temperature: 0.1,
        }),
      });
      const body = (await response.json()) as ChatResponse & { detail?: string };
      if (!response.ok) throw new Error(body.detail ?? "Unable to summarize page");
      setSummary(body.content);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to summarize page");
    } finally {
      setSummarizing(false);
    }
  }

  return (
    <section className="space-y-6">
      <form
        onSubmit={crawlUrl}
        className="space-y-4 border border-white/10 bg-white/[0.03] p-4"
      >
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="flex flex-1 items-center gap-3 border border-white/10 bg-black px-4">
            <Globe size={16} className="text-slate-500" />
            <input
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              className="h-12 w-full bg-transparent text-sm text-white outline-none"
              placeholder="https://example.com/research"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex h-12 items-center justify-center gap-2 bg-white px-5 text-xs font-black uppercase tracking-widest text-black disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Crawl
          </button>
        </div>

        <div className="flex flex-col gap-3 text-sm text-slate-300 md:flex-row md:items-center">
          <label className="inline-flex items-center gap-2">
            <input
              checked={followPagination}
              onChange={(event) => setFollowPagination(event.target.checked)}
              type="checkbox"
              className="h-4 w-4 accent-white"
            />
            Follow next-page links
          </label>
          <label className="inline-flex items-center gap-2">
            Max source pages
            <input
              type="number"
              min={1}
              max={25}
              value={maxSourcePages}
              onChange={(event) => setMaxSourcePages(Number(event.target.value) || 1)}
              className="h-9 w-20 border border-white/10 bg-black px-3 text-white outline-none"
            />
          </label>
        </div>
      </form>

      {error && (
        <div className="border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <article className="min-h-[520px] border border-white/10 bg-white/[0.02]">
          <header className="flex flex-col gap-3 border-b border-white/10 px-5 py-4 md:flex-row md:items-center md:justify-between">
            <div className="min-w-0">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                Research Reader
              </p>
              <h3 className="truncate text-lg font-bold text-white">
                {document?.title ?? "Load a page to begin"}
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={!document?.has_previous || loading}
                onClick={() => document && loadPage(document.page - 1)}
                className="inline-flex h-10 w-10 items-center justify-center border border-white/10 text-slate-300 disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Previous page"
              >
                <ChevronLeft size={18} />
              </button>
              <span className="min-w-28 text-center text-xs font-bold uppercase tracking-widest text-slate-400">
                {pageLabel}
              </span>
              <button
                type="button"
                disabled={!document?.has_next || loading}
                onClick={() => document && loadPage(document.page + 1)}
                className="inline-flex h-10 w-10 items-center justify-center border border-white/10 text-slate-300 disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Next page"
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </header>

          <div className="whitespace-pre-wrap px-5 py-5 text-sm leading-7 text-slate-200">
            {document?.text ??
              "Use the crawler to fetch readable source text. Documents are stored locally and split into pages for review."}
          </div>
        </article>

        <aside className="space-y-4 border border-white/10 bg-white/[0.02] p-5">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">
              Local AI
            </p>
            <h3 className="mt-1 text-lg font-bold text-white">Page Notes</h3>
          </div>

          <button
            type="button"
            disabled={!document || summarizing}
            onClick={summarizeCurrentPage}
            className="inline-flex h-11 w-full items-center justify-center gap-2 border border-white/10 bg-white text-xs font-black uppercase tracking-widest text-black disabled:cursor-not-allowed disabled:opacity-50"
          >
            {summarizing ? <Loader2 size={16} className="animate-spin" /> : <Bot size={16} />}
            Summarize Page
          </button>

          <div className="min-h-48 whitespace-pre-wrap border border-white/10 bg-black/40 p-4 text-sm leading-6 text-slate-300">
            {summary || "Summaries use your configured Ollama model when it is available."}
          </div>

          <div className="space-y-3 border-t border-white/10 pt-4">
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                Source Pages
              </p>
              <p className="mt-1 text-sm text-slate-300">
                {sourcePages.length
                  ? `${sourcePages.length} crawled page${sourcePages.length === 1 ? "" : "s"}`
                  : "No source pages loaded"}
              </p>
            </div>

            <div className="space-y-2">
              {sourcePages.map((sourcePage) => (
                <div
                  key={`${sourcePage.sequence}-${sourcePage.url}`}
                  className="border border-white/10 bg-black/40 p-3 text-xs text-slate-300"
                >
                  <p className="font-bold text-white">Page {sourcePage.sequence}</p>
                  <p className="mt-1 break-all text-slate-500">{sourcePage.url}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
