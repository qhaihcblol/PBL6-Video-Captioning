"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { videosApi } from "@/lib/api/videos"
import type { VideoResponse } from "@/lib/types"
import { AlertCircle, CheckCircle, Copy, FileVideo, Upload, Zap } from "lucide-react"
import { useRef, useState } from "react"

interface UploadSectionProps {
  onUploadSuccess?: () => void
}

export default function UploadSection({ onUploadSuccess }: UploadSectionProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [captionResult, setCaptionResult] = useState<VideoResponse | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      const file = files[0]
      if (file.type.startsWith("video/")) {
        setSelectedFile(file)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setCaptionResult(null)
    setUploadError(null)
    setUploadProgress(0)

    try {
      // Upload video with real API
      const result = await videosApi.uploadVideo(
        selectedFile,
        selectedFile.name.replace(/\.[^/.]+$/, ""), // Use filename as title
        (progress) => {
          setUploadProgress(progress)
        }
      )

      // Set result from backend
      setCaptionResult(result)
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }

      // Notify parent component
      onUploadSuccess?.()
    } catch (error: any) {
      console.error("Upload failed:", error)
      setUploadError(error.message || "Failed to upload video. Please try again.")
    } finally {
      setIsProcessing(false)
      setUploadProgress(0)
    }
  }

  const handlePlayCaption = (caption: string) => {
    const utterance = new SpeechSynthesisUtterance(caption)
    utterance.lang = 'en-GB'
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  }

  const handleCopyCaption = (caption: string, id: string) => {
    navigator.clipboard.writeText(caption)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleNewUpload = () => {
    setCaptionResult(null)
    setSelectedFile(null)
    setUploadError(null)
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      {!captionResult && (
        <Card
          className={`border-2 border-dashed p-12 text-center transition-colors cursor-pointer ${dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
            }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
            aria-label="Upload video file"
          />

          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-foreground mb-1">Drop your video here</h3>
              <p className="text-muted-foreground">or click to browse from your computer</p>
            </div>

            <p className="text-xs text-muted-foreground">Supported formats: MP4, WebM, Ogg (Max 500MB)</p>
          </div>
        </Card>
      )}

      {/* Selected File Info */}
      {selectedFile && !captionResult && (
        <Card className="p-6 border-border/50 space-y-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <FileVideo className="w-6 h-6 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-foreground truncate">{selectedFile.name}</h4>
              <p className="text-sm text-muted-foreground">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
          </div>

          {uploadError && (
            <div className="flex items-start gap-3 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <p className="text-sm text-destructive">{uploadError}</p>
            </div>
          )}

          {isProcessing && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground font-medium">
                  {uploadProgress < 100 ? "Uploading..." : "Processing..."}
                </span>
                <span className="text-muted-foreground">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary h-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              onClick={handleUpload}
              disabled={isProcessing}
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {isProcessing ? "Processing..." : "Generate Caption"}
            </Button>
            <Button
              onClick={() => {
                setSelectedFile(null)
                if (fileInputRef.current) {
                  fileInputRef.current.value = ""
                }
              }}
              disabled={isProcessing}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              Cancel
            </Button>
          </div>
        </Card>
      )}

      {/* Caption Result with Video Player */}
      {captionResult && (
        <Card className="p-6 border-border/50 space-y-4 bg-accent/5">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-6 h-6 text-accent flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-foreground mb-1">Caption Generated Successfully</h3>
              <p className="text-sm text-muted-foreground">
                {new Date(captionResult.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {captionResult.video_url && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Video Preview</p>
              <video
                ref={videoRef}
                src={`${process.env.NEXT_PUBLIC_API_URL}${captionResult.video_url}`}
                controls
                className="w-full max-h-[60vh] rounded-lg bg-black border border-border/50"
                aria-label="Uploaded video preview"
              />
            </div>
          )}

          <div className="space-y-3 bg-card p-4 rounded-lg border border-border/50">
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Video Title</p>
              <p className="font-medium text-foreground">{captionResult.title}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                Generated Caption
              </p>
              <p className="text-sm text-foreground leading-relaxed">{captionResult.caption}</p>
            </div>
            {captionResult.duration && (
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Duration</p>
                <p className="text-sm text-foreground">{captionResult.duration}</p>
              </div>
            )}
          </div>

          <div className="flex gap-3 flex-wrap">
            <Button
              onClick={() => handlePlayCaption(captionResult.caption)}
              className="flex-1 min-w-[150px] bg-accent hover:bg-accent/90 text-accent-foreground"
            >
              <Zap className="w-4 h-4 mr-2" />
              Listen Caption
            </Button>
            <Button
              onClick={() => handleCopyCaption(captionResult.caption, captionResult.id)}
              variant="outline"
              className="flex-1 min-w-[150px] border-border text-foreground hover:bg-secondary"
            >
              <Copy className="w-4 h-4 mr-2" />
              {copiedId === captionResult.id ? "Copied!" : "Copy Caption"}
            </Button>
            <Button
              onClick={handleNewUpload}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              Upload Another
            </Button>
          </div>
        </Card>
      )}

      {/* Info Box */}
      <Card className="p-4 border-border/50 bg-accent/5 flex gap-3">
        <AlertCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
        <div className="text-sm text-foreground">
          <p className="font-medium mb-1">How it works:</p>
          <ul className="space-y-1 text-muted-foreground list-disc list-inside">
            <li>Upload your video file (MP4, WebM, or Ogg)</li>
            <li>Our AI analyzes and generates accurate captions</li>
            <li>Listen to captions with text-to-speech</li>
            <li>Save to history for future reference</li>
          </ul>
        </div>
      </Card>
    </div>
  )
}
