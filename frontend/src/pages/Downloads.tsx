import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { downloadModel, type DownloadResponse } from "../api/client";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const val = bytes / Math.pow(1024, i);
  return `${val.toFixed(i > 1 ? 1 : 0)} ${units[i]}`;
}

export default function Downloads() {
  const queryClient = useQueryClient();
  const [modelInput, setModelInput] = useState("");
  const [source, setSource] = useState("huggingface");
  const [force, setForce] = useState(false);
  const [includePatterns, setIncludePatterns] = useState("");
  const [result, setResult] = useState<DownloadResponse | null>(null);

  const dlMut = useMutation({
    mutationFn: downloadModel,
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ["models"] });
      queryClient.invalidateQueries({ queryKey: ["storage-status"] });
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!modelInput.trim()) return;

    setResult(null);
    const patterns = includePatterns
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    dlMut.mutate({
      model_id: modelInput.trim(),
      source,
      force,
      include_patterns: patterns.length > 0 ? patterns : undefined,
    });
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-4">Download Model</h2>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="rounded-lg border border-ctp-surface0 bg-ctp-mantle p-5 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-ctp-subtext1">Model ID or URL</span>
            <input
              type="text"
              value={modelInput}
              onChange={(e) => setModelInput(e.target.value)}
              placeholder="e.g. Qwen/Qwen2.5-7B-Instruct or https://huggingface.co/..."
              className="mt-1 block w-full rounded-md border border-ctp-surface1 bg-ctp-surface0 px-3 py-2 text-sm text-ctp-text placeholder-ctp-overlay0 focus:border-ctp-blue focus:outline-none focus:ring-1 focus:ring-ctp-blue"
            />
          </label>

          <div className="grid grid-cols-2 gap-4">
            <label className="block">
              <span className="text-sm font-medium text-ctp-subtext1">Source</span>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="mt-1 block w-full rounded-md border border-ctp-surface1 bg-ctp-surface0 px-3 py-2 text-sm text-ctp-text focus:border-ctp-blue focus:outline-none focus:ring-1 focus:ring-ctp-blue"
              >
                <option value="huggingface">HuggingFace</option>
              </select>
            </label>

            <label className="block">
              <span className="text-sm font-medium text-ctp-subtext1">Include patterns</span>
              <input
                type="text"
                value={includePatterns}
                onChange={(e) => setIncludePatterns(e.target.value)}
                placeholder="e.g. *.safetensors, config.json"
                className="mt-1 block w-full rounded-md border border-ctp-surface1 bg-ctp-surface0 px-3 py-2 text-sm text-ctp-text placeholder-ctp-overlay0 focus:border-ctp-blue focus:outline-none focus:ring-1 focus:ring-ctp-blue"
              />
              <span className="text-xs text-ctp-overlay1 mt-1 block">Comma-separated glob patterns (leave empty for all files)</span>
            </label>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={force}
              onChange={(e) => setForce(e.target.checked)}
              className="rounded border-ctp-surface1 bg-ctp-surface0 text-ctp-blue focus:ring-ctp-blue"
            />
            <span className="text-sm text-ctp-subtext1">Force re-download if already exists</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={!modelInput.trim() || dlMut.isPending}
          className="rounded-lg bg-ctp-blue px-5 py-2.5 text-sm font-medium text-ctp-crust hover:bg-ctp-blue/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {dlMut.isPending ? "Downloading..." : "Download"}
        </button>
      </form>

      {/* Download in progress */}
      {dlMut.isPending && (
        <div className="rounded-lg border border-ctp-blue/30 bg-ctp-blue/5 px-4 py-3 mb-4">
          <div className="flex items-center gap-3">
            <svg
              className="animate-spin h-5 w-5 text-ctp-blue"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-ctp-blue">Downloading model...</p>
              <p className="text-xs text-ctp-subtext0 mt-0.5">
                This may take a while for large models. Keep this page open.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {dlMut.isError && (
        <div className="rounded-lg bg-ctp-red/10 border border-ctp-red/30 px-4 py-3 mb-4 text-sm text-ctp-red">
          {(dlMut.error as Error).message}
        </div>
      )}

      {/* Success */}
      {result && (
        <div className="rounded-lg border border-ctp-green/30 bg-ctp-green/5 p-4">
          <p className="text-sm font-medium text-ctp-green mb-3">Download complete</p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-ctp-subtext0">Model</span>
              <span className="text-ctp-text">{result.model_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ctp-subtext0">Source</span>
              <span className="text-ctp-text">{result.source}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ctp-subtext0">Size</span>
              <span className="text-ctp-text">{formatBytes(result.size_bytes)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ctp-subtext0">Files</span>
              <span className="text-ctp-text">{result.files.length}</span>
            </div>
            <div>
              <span className="text-ctp-subtext0">Path</span>
              <p className="text-ctp-text font-mono text-xs mt-1 break-all">{result.path}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
