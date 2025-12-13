"use client"

import { Button } from "@/components/ui/button"
import { LogOut, Menu } from "lucide-react"
import { useState } from "react"

interface DashboardHeaderProps {
  user: { email: string; full_name?: string }
  onLogout: () => void
}

export default function DashboardHeader({ user, onLogout }: DashboardHeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">S</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">See For Me</h1>
            <p className="text-xs text-muted-foreground">Video Captioning Platform</p>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-foreground">{user.full_name || "User"}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
          <Button
            onClick={onLogout}
            variant="outline"
            size="sm"
            className="border-border text-foreground hover:bg-secondary bg-transparent"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>

        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 hover:bg-secondary rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5 text-foreground" />
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border p-4 space-y-3">
          <div className="text-sm">
            <p className="font-medium text-foreground">{user.full_name || "User"}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
          <Button
            onClick={onLogout}
            variant="outline"
            size="sm"
            className="w-full border-border text-foreground hover:bg-secondary bg-transparent"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      )}
    </header>
  )
}
