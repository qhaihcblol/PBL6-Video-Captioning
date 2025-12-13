"use client"

import DashboardHeader from "@/components/dashboard/dashboard-header"
import UploadSection from "@/components/dashboard/upload-section"
import VideoHistory from "@/components/dashboard/video-history"
import VideoSamples from "@/components/dashboard/video-samples"
import { Clock, Play, Upload } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<{ email: string; full_name?: string } | null>(null)
  const [activeTab, setActiveTab] = useState<"samples" | "upload" | "history">("samples")
  const [historyRefresh, setHistoryRefresh] = useState(0)

  useEffect(() => {
    const userData = localStorage.getItem("user")
    if (!userData) {
      router.push("/")
    } else {
      setUser(JSON.parse(userData))
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("user")
    router.push("/")
  }

  const handleHistoryUpdate = () => {
    setHistoryRefresh((prev) => prev + 1)
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <DashboardHeader user={user} onLogout={handleLogout} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Welcome back, {user.full_name || "User"}</h1>
          <p className="text-muted-foreground">Upload videos to generate captions and support accessibility</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-8 border-b border-border overflow-x-auto">
          <button
            onClick={() => setActiveTab("samples")}
            className={`px-4 py-3 font-medium transition-colors border-b-2 whitespace-nowrap ${activeTab === "samples"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
          >
            <div className="flex items-center gap-2">
              <Play className="w-4 h-4" />
              Sample Videos
            </div>
          </button>
          <button
            onClick={() => setActiveTab("upload")}
            className={`px-4 py-3 font-medium transition-colors border-b-2 whitespace-nowrap ${activeTab === "upload"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
          >
            <div className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload Video
            </div>
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`px-4 py-3 font-medium transition-colors border-b-2 whitespace-nowrap ${activeTab === "history"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
          >
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              History
            </div>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "samples" && <VideoSamples />}
        {activeTab === "upload" && <UploadSection onUploadSuccess={handleHistoryUpdate} />}
        {activeTab === "history" && <VideoHistory refreshTrigger={historyRefresh} />}
      </main>
    </div>
  )
}
