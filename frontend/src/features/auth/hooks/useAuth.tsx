'use client'

import { useState, useEffect, createContext, useContext } from 'react'
import { User } from '@supabase/supabase-js'
import { authService } from  '../services/authServices'
import { LoginCredentials, RegisterData, UserProfile, AuthState } from '@/types/auth.types'

const AuthContext = createContext<{
  authState: AuthState
  login: (credentials: LoginCredentials) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>
  changePassword: (newPassword: string) => Promise<void>
  refreshProfile: () => Promise<void>
}>({} as any)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const useAuthProvider = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    profile: null,
    loading: true,
    initialized: false,
  })

  const login = async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      await authService.login(credentials)
      // Auth state change listener will handle the state update
    } catch (error) {
      setAuthState(prev => ({ ...prev, loading: false }))
      throw error
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      await authService.register(userData)
      // Auth state change listener will handle the state update
    } catch (error) {
      setAuthState(prev => ({ ...prev, loading: false }))
      throw error
    }
  }

  const logout = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }))
      await authService.logout()
      setAuthState({
        user: null,
        profile: null,
        loading: false,
        initialized: true,
      })
    } catch (error) {
      setAuthState(prev => ({ ...prev, loading: false }))
      throw error
    }
  }

  const updateProfile = async (updates: Partial<UserProfile>) => {
    try {
      const updatedProfile = await authService.updateProfile(updates)
      setAuthState(prev => ({
        ...prev,
        profile: updatedProfile,
      }))
    } catch (error) {
      throw error
    }
  }

  const changePassword = async (newPassword: string) => {
    try {
      await authService.changePassword(newPassword)
    } catch (error) {
      throw error
    }
  }

  const refreshProfile = async () => {
    try {
      if (authState.user) {
        const profile = await authService.getProfile()
        setAuthState(prev => ({ ...prev, profile }))
      }
    } catch (error) {
      console.error('Error refreshing profile:', error)
    }
  }

  useEffect(() => {
    // Listen for auth changes
    const { data: { subscription } } = authService.onAuthStateChange(
      async (event, session) => {
        if (session?.user) {
          const profile = await authService.getProfile()
          setAuthState({
            user: session.user as User,
            profile,
            loading: false,
            initialized: true,
          })
        } else {
          setAuthState({
            user: null,
            profile: null,
            loading: false,
            initialized: true,
          })
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  return {
    authState,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshProfile,
  }
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const auth = useAuthProvider()

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  )
}