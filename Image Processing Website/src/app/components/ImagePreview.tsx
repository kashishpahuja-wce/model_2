import { Download, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface ImagePreviewProps {
  originalImage: string;
  processedImage: string | null;
  onDownload: () => void;
  showSuccess: boolean;
}

export function ImagePreview({ originalImage, processedImage, onDownload, showSuccess }: ImagePreviewProps) {
  return (
    <div className="space-y-6">
      {/* Processed Image Only */}
      <Card className="bg-zinc-900 border-zinc-800 p-6 shadow-lg">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Your Processed Image</h3>
          
          <div className="aspect-video bg-zinc-800 rounded-lg overflow-hidden">
            {processedImage ? (
              <img
                src={processedImage}
                alt="Processed"
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-zinc-400">Processing your image...</p>
                </div>
              </div>
            )}
          </div>

          {/* Download Button */}
          {processedImage && !showSuccess && (
            <Button
              onClick={onDownload}
              size="lg"
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25"
            >
              <Download className="w-5 h-5 mr-2" />
              Download Processed Image
            </Button>
          )}
        </div>
      </Card>

      {/* Success Message */}
      {showSuccess && (
        <Card className="bg-green-500/10 border-green-500/20 p-6 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <h3 className="font-semibold text-white mb-1">Download Complete!</h3>
              <p className="text-sm text-zinc-300">
                Image has been downloaded to your device and we have deleted it from our end for your privacy.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
