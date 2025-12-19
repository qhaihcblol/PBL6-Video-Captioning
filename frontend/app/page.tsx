"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"
import { authApi } from "@/lib/api/auth"
import { Eye, EyeOff, Play } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem("token")
    const user = localStorage.getItem("user")
    if (token && user) {
      router.push("/dashboard")
    } else {
      setIsCheckingAuth(false)
    }
  }, [router])

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    )
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      // Call real API
      const response = await authApi.login({ email, password })

      // Show success message
      toast({
        title: "Login successful",
        description: `Welcome back, ${response.full_name}!`,
      })

      // Redirect to dashboard
      router.push("/dashboard")
    } catch (err: any) {
      // Handle error
      const errorMessage = err.message || "Login failed. Please try again."
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Login failed",
        description: errorMessage,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
        {/* Left side - Branding */}
        <div className="hidden lg:flex flex-col justify-center space-y-8">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                <Play className="w-6 h-6 text-primary-foreground fill-primary-foreground" />
              </div>
              <h1 className="text-3xl font-bold text-foreground">See For Me</h1>
            </div>
            <p className="text-xl text-muted-foreground font-medium">Video Captioning for Everyone</p>
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Accessibility First</h3>
              <p className="text-muted-foreground">
                Automatic video captions with text-to-speech support for blind and visually impaired users.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Smart Captioning</h3>
              <p className="text-muted-foreground">
                AI-powered caption generation that understands context and delivers accurate descriptions.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Easy to Use</h3>
              <p className="text-muted-foreground">
                Upload videos, get captions instantly, and listen with our integrated text-to-speech.
              </p>
            </div>
          </div>
        </div>

        {/* Right side - Login Form */}
        <div className="flex justify-center">
          <Card className="w-full max-w-md p-8 shadow-lg border-border/50">
            <div className="space-y-8">
              <div className="space-y-2 text-center lg:text-left">
                <h2 className="text-2xl font-bold text-foreground">Welcome Back</h2>
                <p className="text-muted-foreground">Sign in to your account to continue</p>
              </div>

              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-foreground font-medium">
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="bg-input border-border text-foreground placeholder:text-muted-foreground"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-foreground font-medium">
                    Password
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-input border-border text-foreground placeholder:text-muted-foreground pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-2 h-10"
                >
                  {isLoading ? "Signing in..." : "Sign In"}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-card text-muted-foreground">Don't have an account?</span>
                </div>
              </div>

              <Link href="/register">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full border-border text-foreground hover:bg-secondary bg-transparent"
                >
                  Create Account
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
