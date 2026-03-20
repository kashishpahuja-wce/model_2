import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './ui/button';

interface AdModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export function AdModal({ isOpen, onClose, onComplete }: AdModalProps) {
  const [timeRemaining, setTimeRemaining] = useState(5);
  const [canSkip, setCanSkip] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setTimeRemaining(5);
      setCanSkip(false);
      return;
    }

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setTimeout(() => {
            onComplete();
          }, 100);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // Enable skip button after 5 seconds
    const skipTimer = setTimeout(() => {
      setCanSkip(true);
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(skipTimer);
    };
  }, [isOpen, onComplete]);

  if (!isOpen) return null;

  const handleSkip = () => {
    if (canSkip) {
      onClose();
      onComplete();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-4xl bg-zinc-900 rounded-2xl shadow-2xl overflow-hidden border border-zinc-800">
        {/* Ad Content */}
        <div className="relative aspect-video w-full">
          <img
            src="https://images.unsplash.com/photo-1763069227994-06906285b144?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBhYnN0cmFjdCUyMGFkdmVydGlzaW5nJTIwYmFubmVyfGVufDF8fHx8MTc3MzkzMDU5OXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
            alt="Advertisement"
            className="w-full h-full object-cover"
          />
          
          {/* Timer Badge */}
          <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm px-4 py-2 rounded-full border border-white/10">
            <span className="text-white text-sm font-medium">
              {timeRemaining > 0 ? `${timeRemaining}s` : 'Complete!'}
            </span>
          </div>

          {/* Processing Message */}
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-black/70 backdrop-blur-sm px-6 py-3 rounded-xl border border-white/10">
              <p className="text-white text-sm">
                Your image is being processed... Please wait while we enhance your photo.
              </p>
            </div>
          </div>
        </div>

        {/* Skip Button (appears after 5 seconds) */}
        {canSkip && (
          <div className="absolute top-4 left-4">
            <Button
              onClick={handleSkip}
              variant="outline"
              size="sm"
              className="bg-black/70 backdrop-blur-sm border-white/20 hover:bg-black/90 text-white"
            >
              <X className="w-4 h-4 mr-2" />
              Skip Ad
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}