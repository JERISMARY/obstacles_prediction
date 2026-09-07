/**
 * Voice Service using Web Speech API (window.speechSynthesis)
 * 
 * Handles playing voice warnings in the browser.
 * No external API required. Works fully offline.
 */

class VoiceService {
  constructor() {
    this.synth = window.speechSynthesis
    this.enabled = true
    this.volume = 1.0
    this.rate = 1.0
    
    // We don't want to interrupt critical warnings with low priority ones
    this.isSpeaking = false
    this.currentPriority = 0
  }

  setEnabled(enabled) {
    this.enabled = enabled
    if (!enabled) {
      this.stop()
    }
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume))
  }

  setRate(rate) {
    this.rate = Math.max(0.5, Math.min(2, rate))
  }

  stop() {
    if (this.synth) {
      this.synth.cancel()
      this.isSpeaking = false
      this.currentPriority = 0
    }
  }

  speak(text, priority = 1) {
    if (!this.enabled || !this.synth) return
    
    // Don't interrupt a higher priority message with a lower one
    if (this.isSpeaking && priority < this.currentPriority) {
      return
    }

    // Cancel current speech if we have a higher or equal priority message
    if (this.isSpeaking) {
      this.stop()
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.volume = this.volume
    utterance.rate = this.rate
    // Try to pick a clear English voice if available
    const voices = this.synth.getVoices()
    if (voices.length > 0) {
      const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Microsoft Zira') || v.name.includes('Siri')))
      if (preferred) utterance.voice = preferred
    }

    utterance.onstart = () => {
      this.isSpeaking = true
      this.currentPriority = priority
    }

    utterance.onend = () => {
      this.isSpeaking = false
      this.currentPriority = 0
    }

    utterance.onerror = (e) => {
      console.error("Speech synthesis error", e)
      this.isSpeaking = false
      this.currentPriority = 0
    }

    this.synth.speak(utterance)
  }
}

export const voiceService = new VoiceService()
