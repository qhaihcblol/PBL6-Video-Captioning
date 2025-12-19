"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useTextToSpeech } from "@/hooks/use-text-to-speech"
import { videosApi } from "@/lib/api/videos"
import type { VideoResponse } from "@/lib/types"
import { ChevronLeft, ChevronRight, Clock, Copy, Eye, Square, Trash2, Volume2 } from "lucide-react"
import { useEffect, useState } from "react"

interface VideoHistoryProps {
  refreshTrigger?: number
}

export default function VideoHistory({ refreshTrigger }: VideoHistoryProps) {
  const [videos, setVideos] = useState<VideoResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalVideos, setTotalVideos] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const { speak, pause, stop, isPlaying, isPaused } = useTextToSpeech({ rate: 0.9 })

  const limit = 10
  const totalPages = Math.ceil(totalVideos / limit)

  const fetchVideos = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await videosApi.getVideoHistory(page, limit)
      setVideos(response.videos)
      setTotalVideos(response.total)
    } catch (err: any) {
      console.error("Failed to fetch videos:", err)
      setError(err.message || "Failed to load video history")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchVideos()
  }, [page, refreshTrigger])

  const handlePlayCaption = (id: string, caption: string) => {
    if (playingId === id && isPlaying) {
      pause()
    } else {
      setPlayingId(id)
      speak(caption)
    }
  }

  const handleStopCaption = (id: string) => {
    if (playingId === id) {
      stop()
      setPlayingId(null)
    }
  }

  const handleCopyCaption = (id: string, caption: string) => {
    navigator.clipboard.writeText(caption)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleDeleteItem = async (id: string) => {
    if (!confirm("Are you sure you want to delete this video?")) return

    try {
      await videosApi.deleteVideo(id)
      // Refresh the list
      await fetchVideos()
    } catch (err: any) {
      console.error("Failed to delete video:", err)
      alert(err.message || "Failed to delete video")
    }
  }

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to clear all history? This action cannot be undone.")) return

    try {
      await videosApi.clearHistory()
      // Refresh the list
      setPage(1)
      await fetchVideos()
    } catch (err: any) {
      console.error("Failed to clear history:", err)
      alert(err.message || "Failed to clear history")
    }
  }

  if (isLoading) {
    return (
      <Card className="p-8 text-center border-border/50">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-muted rounded w-3/4 mx-auto"></div>
          <div className="h-4 bg-muted rounded w-1/2 mx-auto"></div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-8 text-center border-border/50">
        <Clock className="w-12 h-12 text-destructive mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">Error loading history</h3>
        <p className="text-muted-foreground mb-4">{error}</p>
        <Button onClick={fetchVideos} variant="outline">
          Try Again
        </Button>
      </Card>
    )
  }

  if (videos.length === 0) {
    return (
      <Card className="p-8 text-center border-border/50">
        <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">No videos yet</h3>
        <p className="text-muted-foreground">Upload your first video to see it in your history</p>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Your Video History</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {totalVideos} video{totalVideos !== 1 ? "s" : ""} saved
            {totalPages > 1 && ` • Page ${page} of ${totalPages}`}
          </p>
        </div>
        {videos.length > 0 && (
          <Button
            onClick={handleClearAll}
            variant="outline"
            size="sm"
            className="border-destructive text-destructive hover:bg-destructive/10 bg-transparent"
          >
            Clear All
          </Button>
        )}
      </div>

      <div className="grid gap-4">
        {videos.map((video) => (
          <Card key={video.id} className="p-6 border-border/50 hover:shadow-md transition-shadow">
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground truncate">{video.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(video.created_at).toLocaleString()}
                    {video.duration && ` • ${video.duration}`}
                  </p>
                </div>
              </div>

              <div className="bg-secondary/30 p-4 rounded-lg border border-border/50">
                <p className="text-sm text-foreground leading-relaxed line-clamp-3">{video.caption}</p>
              </div>

              <div className="flex gap-2 flex-wrap">
                <Button
                  onClick={() => handlePlayCaption(video.id, video.caption)}
                  size="sm"
                  className="bg-accent hover:bg-accent/90 text-accent-foreground"
                >
                  <Volume2 className="w-4 h-4 mr-2" />
                  {playingId === video.id && isPlaying && !isPaused ? "Playing..." : "Listen"}
                </Button>
                {playingId === video.id && isPlaying && (
                  <>
                    <Button
                      onClick={pause}
                      variant="outline"
                      size="sm"
                      className="border-border text-foreground hover:bg-secondary bg-transparent"
                    >
                      {isPaused ? "Resume" : "Pause"}
                    </Button>
                    <Button
                      onClick={() => handleStopCaption(video.id)}
                      variant="outline"
                      size="sm"
                      className="border-border text-foreground hover:bg-secondary"
                    >
                      <Square className="w-4 h-4" />
                    </Button>
                  </>
                )}
                <Dialog>
                  <DialogTrigger asChild>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-border text-foreground hover:bg-secondary"
                      disabled={!video.video_url}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogTitle>{video.title}</DialogTitle>
                    <DialogDescription>
                      {new Date(video.created_at).toLocaleString()}
                    </DialogDescription>
                    {video.video_url ? (
                      <div className="mt-4">
                        <video
                          cont  rols
                          src={`${process.env.NEXT_PUBLIC_API_URL}${video.video_url}`}
                          className="w-full rounded-md bg-black"
                        />
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground mt-2">No video file available</p>
                    )}
                  </DialogContent>
                </Dialog>
                <Button
                  onClick={() => handleCopyCaption(video.id, video.caption)}
                  variant="outline"
                  size="sm"
                  className="border-border text-foreground hover:bg-secondary"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  {copiedId === video.id ? "Copied!" : "Copy"}
                </Button>
                <Button
                  onClick={() => handleDeleteItem(video.id)}
                  variant="outline"
                  size="sm"
                  className="border-destructive text-destructive hover:bg-destructive/10 ml-auto"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            variant="outline"
            size="sm"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground px-4">
            Page {page} of {totalPages}
          </span>
          <Button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            variant="outline"
            size="sm"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  )
}
