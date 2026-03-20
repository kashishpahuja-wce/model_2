import { useCallback, useState } from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { Card } from './ui/card';

interface UploadSectionProps {
  onImageSelect: (file: File) => void;
  disabled?: boolean;
}

export function UploadSection({ onImageSelect, disabled }: UploadSectionProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0 && files[0].type.startsWith('image/')) {
        onImageSelect(files[0]);
      }
    },
    [onImageSelect, disabled]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;
      
      const files = e.target.files;
      if (files && files.length > 0 && files[0].type.startsWith('image/')) {
        onImageSelect(files[0]);
      }
    },
    [onImageSelect, disabled]
  );

  return (
    <Card
      className={`
        relative bg-zinc-900 border-2 border-dashed transition-all duration-200 shadow-lg
        ${isDragging 
          ? 'border-purple-500 bg-purple-500/10 scale-[1.02]' 
          : 'border-zinc-700 hover:border-zinc-600'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept="image/*"
        onChange={handleFileInput}
        disabled={disabled}
      />
      
      <label
        htmlFor="file-upload"
        className={`flex flex-col items-center justify-center p-12 ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl mb-6 shadow-lg">
          {isDragging ? (
            <ImageIcon className="w-10 h-10 text-purple-500" />
          ) : (
            <Upload className="w-10 h-10 text-purple-500" />
          )}
        </div>
        
        <h3 className="text-xl font-semibold text-white mb-2">
          {isDragging ? 'Drop your image here' : 'Upload an image'}
        </h3>
        
        <p className="text-zinc-400 text-center mb-4">
          Drag and drop your image here, or click to browse
        </p>
        
        <div className="flex gap-2 text-xs text-zinc-500">
          <span className="px-3 py-1 bg-zinc-800 rounded-full border border-zinc-700">PNG</span>
          <span className="px-3 py-1 bg-zinc-800 rounded-full border border-zinc-700">JPG</span>
          <span className="px-3 py-1 bg-zinc-800 rounded-full border border-zinc-700">WEBP</span>
        </div>
      </label>
    </Card>
  );
}
