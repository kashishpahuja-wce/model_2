import { Download, Clock, ExternalLink } from 'lucide-react';
import { downloadImage } from '../utils/imageProcessing';

interface HistoryItem {
  id: string;
  original: string;
  processed: string;
  timestamp: number;
}

interface HistorySectionProps {
  items: HistoryItem[];
}

export function HistorySection({ items }: HistorySectionProps) {
  if (items.length === 0) return null;

  return (
    <div className="space-y-6 pt-12 border-t border-zinc-800">
      <div className="flex items-center gap-2">
        <Clock className="w-5 h-5 text-purple-400" />
        <h3 className="text-xl font-bold text-white">Recent Predictions</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((item) => (
          <div key={item.id} className="group relative bg-zinc-900/50 border border-zinc-800 rounded-2xl overflow-hidden hover:border-purple-500/50 transition-all duration-300">
            <div className="aspect-video relative overflow-hidden">
              <img 
                src={item.processed} 
                alt="Processed" 
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                <button
                  onClick={() => downloadImage(item.processed)}
                  className="p-2 bg-white/10 backdrop-blur-md rounded-full hover:bg-white/20 transition-colors"
                  title="Download"
                >
                  <Download className="w-5 h-5 text-white" />
                </button>
                <a
                  href={item.processed}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-white/10 backdrop-blur-md rounded-full hover:bg-white/20 transition-colors"
                  title="Open original"
                >
                  <ExternalLink className="w-5 h-5 text-white" />
                </a>
              </div>
            </div>
            
            <div className="p-4">
              <div className="flex justify-between items-center">
                <span className="text-xs text-zinc-500">
                  {new Date(item.timestamp).toLocaleDateString()}
                </span>
                <span className="text-xs font-medium px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded-full border border-purple-500/20">
                  Protected
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
