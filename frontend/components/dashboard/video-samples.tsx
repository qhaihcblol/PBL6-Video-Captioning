"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Volume2, Square } from "lucide-react"
import { useState } from "react"
import { useTextToSpeech } from "@/hooks/use-text-to-speech"

interface VideoSample {
  id: string
  title: string
  description: string
  thumbnail: string
  duration: string
  caption: string
}

const SAMPLE_VIDEOS: VideoSample[] = [
  {
    id: "1",
    title: "Introduction to Web Accessibility",
    description: "Learn the basics of creating accessible web experiences for all users.",
    thumbnail: "/web-accessibility-tutorial.jpg",
    duration: "5:32",
    caption:
      "This video introduces fundamental concepts of web accessibility, including WCAG guidelines, semantic HTML, and ARIA attributes.",
  },
  {
    id: "2",
    title: "Building Inclusive Design Systems",
    description: "Explore how to design systems that work for everyone.",
    thumbnail: "/inclusive-design-system.png",
    duration: "8:15",
    caption:
      "Discover best practices for creating design systems that prioritize accessibility and inclusivity from the ground up.",
  },
  {
    id: "3",
    title: "Screen Reader Navigation Tips",
    description: "Master screen reader navigation techniques and shortcuts.",
    thumbnail: "/screen-reader-navigation.jpg",
    duration: "6:45",
    caption:
      "Learn essential screen reader navigation techniques to improve your productivity and accessibility experience.",
  },
  {
    id: "4",
    title: "Color Contrast and Readability",
    description: "Understand color contrast requirements for better readability.",
    thumbnail: "/color-contrast-accessibility.jpg",
    duration: "4:20",
    caption:
      "Explore WCAG color contrast standards and how to ensure your content is readable for users with color blindness.",
  },
]

export default function VideoSamples() {
  const [selectedVideo, setSelectedVideo] = useState<VideoSample | null>(null)
  const { speak, pause, stop, isPlaying, isPaused } = useTextToSpeech({ rate: 0.9 })

  const handlePlayCaption = (video: VideoSample) => {
    setSelectedVideo(video)
    speak(video.caption)
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {SAMPLE_VIDEOS.map((video) => (
          <Card
            key={video.id}
            className="overflow-hidden hover:shadow-lg transition-shadow border-border/50 cursor-pointer group"
            onClick={() => setSelectedVideo(video)}
          >
            <div className="relative overflow-hidden bg-muted h-48">
              <img
                src={video.thumbnail || "/placeholder.svg"}
                alt={video.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-black/40 group-hover:bg-black/50 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                <Play className="w-12 h-12 text-white fill-white" />
              </div>
              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                {video.duration}
              </div>
            </div>

            <div className="p-4 space-y-3">
              <div>
                <h3 className="font-semibold text-foreground line-clamp-2">{video.title}</h3>
                <p className="text-sm text-muted-foreground mt-1">{video.description}</p>
              </div>

              <Button
                onClick={(e) => {
                  e.stopPropagation()
                  handlePlayCaption(video)
                }}
                size="sm"
                className="w-full bg-accent hover:bg-accent/90 text-accent-foreground"
              >
                <Volume2 className="w-4 h-4 mr-2" />
                Listen to Caption
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Caption Preview */}
      {selectedVideo && (
        <Card className="p-6 border-border/50 bg-secondary/30">
          <div className="space-y-3">
            <div>
              <h3 className="font-semibold text-foreground mb-2">Caption Preview</h3>
              <p className="text-sm text-foreground leading-relaxed">{selectedVideo.caption}</p>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button
                onClick={() => speak(selectedVideo.caption)}
                disabled={isPlaying && !isPaused}
                size="sm"
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                <Volume2 className="w-4 h-4 mr-2" />
                {isPlaying && !isPaused ? "Playing..." : "Play Audio"}
              </Button>
              {isPlaying && (
                <Button
                  onClick={pause}
                  variant="outline"
                  size="sm"
                  className="border-border text-foreground hover:bg-secondary bg-transparent"
                >
                  {isPaused ? "Resume" : "Pause"}
                </Button>
              )}
              <Button
                onClick={stop}
                disabled={!isPlaying}
                variant="outline"
                size="sm"
                className="border-border text-foreground hover:bg-secondary bg-transparent"
              >
                <Square className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
