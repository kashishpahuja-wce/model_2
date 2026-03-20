import { X, Check, Zap, ImageIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface PremiumModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpgrade: () => void;
}

export function PremiumModal({ isOpen, onClose, onUpgrade }: PremiumModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="relative w-full max-w-2xl bg-zinc-900 border-zinc-800 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-4 shadow-lg">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">
              Upgrade to Premium
            </h2>
            <p className="text-zinc-400">
              You've reached your free image limit. Upgrade to continue processing unlimited images!
            </p>
          </div>

          {/* Features Card */}
          <Card className="bg-zinc-800/50 border-zinc-700 p-6 mb-6 shadow-lg">
            <h3 className="text-xl font-semibold text-white mb-4">Premium Features</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
                  <Check className="w-4 h-4 text-green-500" />
                </div>
                <div>
                  <p className="text-white font-medium">Unlimited Photo Processing</p>
                  <p className="text-sm text-zinc-400">Process as many images as you want, no limits</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
                  <Check className="w-4 h-4 text-green-500" />
                </div>
                <div>
                  <p className="text-white font-medium">No Advertisements</p>
                  <p className="text-sm text-zinc-400">Skip all ads and get instant results</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
                  <Check className="w-4 h-4 text-green-500" />
                </div>
                <div>
                  <p className="text-white font-medium">Priority Processing</p>
                  <p className="text-sm text-zinc-400">Faster processing speeds for your images</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
                  <Check className="w-4 h-4 text-green-500" />
                </div>
                <div>
                  <p className="text-white font-medium">Advanced Filters</p>
                  <p className="text-sm text-zinc-400">Access to premium enhancement options</p>
                </div>
              </div>
            </div>
          </Card>

          {/* Pricing */}
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20 p-6 mb-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-white">Premium Plan</h3>
                <p className="text-sm text-zinc-300">Billed monthly</p>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold text-white">$9.99</div>
                <div className="text-sm text-zinc-300">/month</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-zinc-300">
              <ImageIcon className="w-4 h-4" />
              <span>Cancel anytime • No hidden fees</span>
            </div>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1 bg-transparent border-zinc-700 text-white hover:bg-zinc-800"
            >
              Maybe Later
            </Button>
            <Button
              onClick={onUpgrade}
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25"
            >
              Upgrade Now
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
