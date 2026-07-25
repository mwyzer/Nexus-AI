'use client';

import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function useAuth() {
  const { user, isAuthenticated, isLoading, login, register, logout, fetchUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchUser();
    }
  }, [isAuthenticated, user, fetchUser]);

  return { user, isAuthenticated, isLoading, login, register, logout };
}
