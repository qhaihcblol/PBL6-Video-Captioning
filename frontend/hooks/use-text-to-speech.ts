"use client"

import { useCallback, useState } from "react"

interface UseTextToSpeechOptions {
  rate?: number
  pitch?: number
  volume?: number
}

export function useTextToSpeech(options: UseTextToSpeechOptions = {}) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  const speak = useCallback(
    (text: string) => {
      if (!("speechSynthesis" in window)) {
        console.error("Speech Synthesis not supported")
        return
      }

      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'en-GB'
      utterance.rate = options.rate || 0.9
      utterance.pitch = options.pitch || 1
      utterance.volume = options.volume || 1

      utterance.onstart = () => {
        setIsPlaying(true)
        setIsPaused(false)
      }

      utterance.onend = () => {
        setIsPlaying(false)
        setIsPaused(false)
      }

      utterance.onerror = () => {
        setIsPlaying(false)
        setIsPaused(false)
      }

      window.speechSynthesis.speak(utterance)
    },
    [options.rate, options.pitch, options.volume],
  )

  const pause = useCallback(() => {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume()
      setIsPaused(false)
    } else {
      window.speechSynthesis.pause()
      setIsPaused(true)
    }
  }, [])

  const stop = useCallback(() => {
    window.speechSynthesis.cancel()
    setIsPlaying(false)
    setIsPaused(false)
  }, [])

  return { speak, pause, stop, isPlaying, isPaused }
}
