import { User, Crown } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from './ui/popover';
import { UserAccount } from '../types/account';

interface AccountButtonProps {
  account: UserAccount;
  onUpgrade: () => void;
}

export function AccountButton({ account, onUpgrade }: AccountButtonProps) {
  const isPremium = account.accountType === 'premium';

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className="bg-zinc-800/50 border-zinc-700 text-white hover:bg-zinc-800 shadow-lg"
        >
          {isPremium ? (
            <Crown className="w-4 h-4 mr-2 text-yellow-500" />
          ) : (
            <User className="w-4 h-4 mr-2" />
          )}
          Account
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 bg-zinc-900 border-zinc-800 shadow-2xl" align="end">
        <div className="space-y-4">
          {/* Account Status */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              {isPremium ? (
                <>
                  <Crown className="w-5 h-5 text-yellow-500" />
                  <h3 className="font-semibold text-white">Premium Account</h3>
                </>
              ) : (
                <>
                  <User className="w-5 h-5 text-zinc-400" />
                  <h3 className="font-semibold text-white">Free Account</h3>
                </>
              )}
            </div>
            <p className="text-sm text-zinc-400">
              {isPremium ? 'Enjoy unlimited processing!' : 'Limited to 3 images'}
            </p>
          </div>

          {/* Usage Stats */}
          <Card className="bg-zinc-800/50 border-zinc-700 p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-zinc-400">Images Processed</span>
                <span className="text-white font-medium">{account.imagesProcessed}</span>
              </div>
              
              {!isPremium && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-400">Images Remaining</span>
                  <span className="text-white font-medium">
                    {account.imagesRemaining}
                  </span>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-zinc-400">Account Type</span>
                <span className={`text-sm font-medium ${isPremium ? 'text-yellow-500' : 'text-zinc-300'}`}>
                  {isPremium ? 'Premium' : 'Free'}
                </span>
              </div>
            </div>
          </Card>

          {/* Premium Features Preview */}
          {isPremium && (
            <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20 p-4">
              <h4 className="text-sm font-semibold text-white mb-2">Premium Benefits</h4>
              <ul className="space-y-1 text-xs text-zinc-300">
                <li>✓ Unlimited photo processing</li>
                <li>✓ No advertisements</li>
                <li>✓ Priority processing speed</li>
                <li>✓ Advanced enhancement filters</li>
              </ul>
            </Card>
          )}

          {/* Upgrade Button for Free Users */}
          {!isPremium && (
            <Button
              onClick={onUpgrade}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25"
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade to Premium
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
