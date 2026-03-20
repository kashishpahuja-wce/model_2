import { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import { UploadSection } from './components/UploadSection';
import { ImagePreview } from './components/ImagePreview';
import { AdModal } from './components/AdModal';
import { PremiumModal } from './components/PremiumModal';
import { PaymentModal } from './components/PaymentModal';
import { AccountButton } from './components/AccountButton';
import { processImage, downloadImage } from './utils/imageProcessing';
import { getAccount, incrementImageCount, upgradeToPremium, UserAccount, FREE_IMAGE_LIMIT } from './types/account';
import { toast } from 'sonner';

export default function App() {
  const [account, setAccount] = useState<UserAccount>(getAccount());
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showAdModal, setShowAdModal] = useState(false);
  const [showPremiumModal, setShowPremiumModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const canProcessMore = account.accountType === 'premium' || account.imagesRemaining > 0;

  const handleImageSelect = async (file: File) => {
    if (!canProcessMore) {
      setShowPremiumModal(true);
      return;
    }

    setIsProcessing(true);
    setShowSuccess(false);
    
    // Read the original image
    const reader = new FileReader();
    reader.onload = (e) => {
      setOriginalImage(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Show ad modal for free users
    if (account.accountType === 'free') {
      setShowAdModal(true);
    } else {
      // Process immediately for premium users
      processImageFile(file);
    }
  };

  const processImageFile = async (file: File) => {
    try {
      const processed = await processImage(file);
      setProcessedImage(processed);
      setIsProcessing(false);
    } catch (error) {
      console.error('Error processing image:', error);
      toast.error('Failed to process image. Please try again.');
      setIsProcessing(false);
    }
  };

  const handleAdComplete = async () => {
    setShowAdModal(false);
    
    // Continue processing after ad
    if (originalImage) {
      const response = await fetch(originalImage);
      const blob = await response.blob();
      const file = new File([blob], 'image.png', { type: 'image/png' });
      processImageFile(file);
    }
  };

  const handleDownload = () => {
    if (processedImage) {
      downloadImage(processedImage);
      setShowSuccess(true);
      
      // Increment the counter
      const updated = incrementImageCount();
      setAccount(updated);
      
      // Reset after 3 seconds
      setTimeout(() => {
        setOriginalImage(null);
        setProcessedImage(null);
        setShowSuccess(false);
        
        // Show premium modal if limit reached
        if (updated.accountType === 'free' && updated.imagesRemaining === 0) {
          setTimeout(() => setShowPremiumModal(true), 500);
        }
      }, 3000);
    }
  };

  const handleUpgradeClick = () => {
    setShowPremiumModal(false);
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = () => {
    setShowPaymentModal(false);
    const updated = upgradeToPremium();
    setAccount(updated);
    toast.success('Welcome to Premium! 🎉');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">ImagePro</h1>
                <p className="text-xs text-zinc-400">Professional Image Processing</p>
              </div>
            </div>
            
            <AccountButton account={account} onUpgrade={() => setShowPremiumModal(true)} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-white">Protect Your Image</h2>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
              Upload your image and watch the AI hallucinate while being absolutely same for human eye.
              {account.accountType === 'free' && ` You have ${account.imagesRemaining} free ${account.imagesRemaining === 1 ? 'image' : 'images'} remaining.`}
            </p>
          </div>

          {/* Upload Section */}
          {!originalImage && (
            <UploadSection 
              onImageSelect={handleImageSelect} 
              disabled={isProcessing || !canProcessMore}
            />
          )}

          {/* Image Preview */}
          {originalImage && (
            <ImagePreview
              originalImage={originalImage}
              processedImage={processedImage}
              onDownload={handleDownload}
              showSuccess={showSuccess}
            />
          )}

          {/* Limit Warning */}
          {account.accountType === 'free' && account.imagesRemaining === 0 && !originalImage && (
            <div className="text-center">
              <button
                onClick={() => setShowPremiumModal(true)}
                className="text-purple-400 hover:text-purple-300 underline"
              >
                You've reached your free limit. Upgrade to Premium for unlimited processing!
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      <AdModal
        isOpen={showAdModal}
        onClose={() => setShowAdModal(false)}
        onComplete={handleAdComplete}
      />
      
      <PremiumModal
        isOpen={showPremiumModal}
        onClose={() => setShowPremiumModal(false)}
        onUpgrade={handleUpgradeClick}
      />
      
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onSuccess={handlePaymentSuccess}
      />
    </div>
  );
}