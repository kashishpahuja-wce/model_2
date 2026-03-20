export interface UserAccount {
  accountType: 'free' | 'premium';
  imagesProcessed: number;
  imagesRemaining: number;
  createdAt: string;
}

export const FREE_IMAGE_LIMIT = 3;

export const getAccount = (): UserAccount => {
  const stored = localStorage.getItem('userAccount');
  if (stored) {
    return JSON.parse(stored);
  }
  
  const newAccount: UserAccount = {
    accountType: 'free',
    imagesProcessed: 0,
    imagesRemaining: FREE_IMAGE_LIMIT,
    createdAt: new Date().toISOString(),
  };
  
  localStorage.setItem('userAccount', JSON.stringify(newAccount));
  return newAccount;
};

export const updateAccount = (updates: Partial<UserAccount>) => {
  const account = getAccount();
  const updated = { ...account, ...updates };
  localStorage.setItem('userAccount', JSON.stringify(updated));
  return updated;
};

export const incrementImageCount = () => {
  const account = getAccount();
  const updated = {
    ...account,
    imagesProcessed: account.imagesProcessed + 1,
    imagesRemaining: account.accountType === 'premium' ? Infinity : Math.max(0, account.imagesRemaining - 1),
  };
  localStorage.setItem('userAccount', JSON.stringify(updated));
  return updated;
};

export const upgradeToPremium = () => {
  return updateAccount({
    accountType: 'premium',
    imagesRemaining: Infinity,
  });
};
