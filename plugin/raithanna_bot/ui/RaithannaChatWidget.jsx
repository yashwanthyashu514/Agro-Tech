import React, { useState, useEffect, useRef } from 'react';
import './RaithannaChatWidget.css';

export function RaithannaChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [lang, setLang] = useState('kn'); // 'kn' for Kannada, 'en' for English
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [quickActions, setQuickActions] = useState([]);
  const [contextChips, setContextChips] = useState([]);
  const [chatContext, setChatContext] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const photoInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Speech Recognition if supported
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = lang === 'kn' ? 'kn-IN' : 'en-IN';

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setRecording(false);
        handleSend(transcript);
      };

      recognition.onerror = () => {
        setRecording(false);
      };

      recognition.onend = () => {
        setRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, [lang]);

  // Load greeting and quick actions
  useEffect(() => {
    fetch('/api/v1/plugin/raithanna/quick-actions')
      .then(res => res.json())
      .then(data => {
        if (data.actions) setQuickActions(data.actions);
      })
      .catch(() => {});

    // Initial greeting
    const initialGreetingKn = "ನಮಸ್ಕಾರ ರೈತ ಬಂಧುವೇ! 🙏 ನಾನು ನಿಮ್ಮ ರೈತಣ್ಣ (Raithanna).\nಬೆಳೆ ಶಿಫಾರಸು, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ, ರೋಗ-ಕೀಟ ಬಾಧೆ, ಗೊಬ್ಬರದ ಪ್ರಮಾಣ, ಮಾರುಕಟ್ಟೆ ಎಪಿಎಂಸಿ ದರ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆ ಇದ್ದರೂ ಕೇಳಿ.\nಧ್ವನಿ ಮೂಲಕ ಮಾತನಾಡಬಹುದು (🎙️) ಅಥವಾ ನಿಮ್ಮ ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ (📷) ಕಳುಹಿಸಬಹುದು!";
    const initialGreetingEn = "Namaskara Farmer Friend! 🙏 I am your Raithanna (ರೈತಣ್ಣ).\nAsk me anything about crop recommendations, weather, pest remedies, fertilizer dosage, APMC mandi rates, or Karnataka government schemes.\nYou can speak via voice (🎙️) or send a leaf photo (📷)!";

    setMessages([
      {
        id: 'welcome',
        sender: 'bot',
        text: lang === 'kn' ? initialGreetingKn : initialGreetingEn,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [lang]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current) {
      alert(lang === 'kn' 
        ? "ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ನೇರ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಧ್ವನಿ ಫೈಲ್ ಅಪ್ಲೋಡ್ ಮಾಡಿ."
        : "Browser speech recognition not available. Please type your query.");
      return;
    }

    if (recording) {
      recognitionRef.current.stop();
      setRecording(false);
    } else {
      try {
        recognitionRef.current.lang = lang === 'kn' ? 'kn-IN' : 'en-IN';
        recognitionRef.current.start();
        setRecording(true);
      } catch (e) {
        setRecording(false);
      }
    }
  };

  const speakText = (text) => {
    if (!window.speechSynthesis) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Strip markdown formatting for cleaner speech
    const cleanText = text.replace(/[*_#`~[\]]/g, '').replace(/https?:\/\/\S+/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang === 'kn' ? 'kn-IN' : 'en-IN';
    utterance.rate = 0.95;

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async (customText) => {
    const textToSend = customText || input;
    if (!textToSend.trim()) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/plugin/raithanna/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          district: 'Davanagere',
          season: 'Kharif',
          lang: lang,
          context: chatContext
        })
      });

      const data = await res.json();
      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
      if (data.chips && data.chips.length > 0) {
        setContextChips(data.chips);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: lang === 'kn' ? 'ಕ್ಷಮಿಸಿ, ಸಂಪರ್ಕ ದೋಷವಾಗಿದೆ. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.' : 'Sorry, connection error. Please try again.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const fn = (file.name || '').toLowerCase();
    const isSoil = fn.includes('soil') || fn.includes('mannu') || fn.includes('mitti') || fn.includes('sample');
    const isLeaf = fn.includes('leaf') || fn.includes('plant') || fn.includes('crop') || fn.includes('disease');
    let uploadLabel;
    if (isSoil) {
      uploadLabel = lang === 'kn' ? `🌱 ಮಣ್ಣಿನ ಮಾದರಿ ಫೋಟೋ: ${file.name}` : `🌱 Soil sample photo: ${file.name}`;
    } else if (isLeaf) {
      uploadLabel = lang === 'kn' ? `🍃 ಸಸ್ಯ/ಎಲೆಯ ಫೋಟೋ: ${file.name}` : `🍃 Plant/leaf photo: ${file.name}`;
    } else {
      uploadLabel = lang === 'kn' ? `📷 ಫೋಟೋ ಅಪ್ಲೋಡ್: ${file.name}` : `📷 Uploaded photo: ${file.name}`;
    }

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: uploadLabel,
      filePreview: URL.createObjectURL(file),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('district', 'Davanagere');
    formData.append('lang', lang);

    try {
      const res = await fetch('/api/v1/plugin/raithanna/analyze-photo', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      const imgType = data.image_type || (data.diagnosis && data.diagnosis.image_type) || (isSoil ? 'soil' : 'leaf');
      setChatContext(imgType === 'soil' ? 'soil_analysis' : 'leaf_disease');

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: data.reply,
          imageType: imgType,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);

      if (data.chips && data.chips.length > 0) {
        setContextChips(data.chips);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: lang === 'kn' ? 'ಫೋಟೋ ಪರೀಕ್ಷೆಯಲ್ಲಿ ದೋಷವಾಗಿದೆ. ದಯವಿಟ್ಟು ಪುನಃ ಕಳುಹಿಸಿ.' : 'Photo diagnosis error. Please re-upload.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  const handleDocUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: lang === 'kn' ? `📎 ದಾಖಲೆ ಲಗತ್ತಿಸಲಾಗಿದೆ: ${file.name}` : `📎 Document attached: ${file.name}`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('district', 'Davanagere');
    formData.append('lang', lang);

    try {
      const res = await fetch('/api/v1/plugin/raithanna/upload-file', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.diagnosis && data.diagnosis.image_type) {
        setChatContext(data.diagnosis.image_type === 'soil' ? 'soil_analysis' : 'leaf_disease');
      }
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: data.reply,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      if (data.chips && data.chips.length > 0) {
        setContextChips(data.chips);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: lang === 'kn' ? 'ಫೈಲ್ ಪರಿಶೀಲನೆಯಲ್ಲಿ ದೋಷವಾಗಿದೆ.' : 'File processing error.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  return (
    <>
      {/* Floating launcher trigger */}
      {!isOpen && (
        <button
          className="raithanna-floating-btn"
          onClick={() => setIsOpen(true)}
          title={lang === 'kn' ? "ರೈತಣ್ಣ ಕೃಷಿ AI ಸಹಾಯವಾಣಿ" : "Ask Raithanna Farmer Assistant"}
        >
          <span className="raithanna-pulse"></span>
          <span style={{ fontSize: '1.4rem' }}>👨‍🌾</span>
          <div style={{ textAlign: 'left', lineHeight: 1.1 }}>
            <div style={{ fontWeight: 800, fontSize: '0.92rem' }}>ರೈತಣ್ಣ (Raithanna)</div>
            <div style={{ fontSize: '0.7rem', opacity: 0.85 }}>AI ಕೃಷಿ ಮಿತ್ರ</div>
          </div>
        </button>
      )}

      {/* Main Chat Window */}
      {isOpen && (
        <div className="raithanna-chat-window">
          {/* Header */}
          <div className="raithanna-header">
            <div className="raithanna-header-title">
              <div className="raithanna-avatar">👨‍🌾</div>
              <div>
                <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#ffffff' }}>
                  {lang === 'kn' ? 'ರೈತಣ್ಣ' : 'Raithanna'}
                  <span style={{ fontSize: '0.72rem', background: '#22c55e', color: '#000', padding: '1px 6px', borderRadius: '10px', marginLeft: '6px', fontWeight: 700 }}>
                    AI
                  </span>
                </div>
                <div style={{ fontSize: '0.73rem', color: '#86efac' }}>
                  {lang === 'kn' ? 'ಕರ್ನಾಟಕ ಕೃಷಿ ಮಿತ್ರ · ಸದಾ ನಿಮ್ಮೊಂದಿಗೆ' : 'Karnataka Agriculture Companion'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                className="raithanna-lang-toggle"
                onClick={() => setLang(l => l === 'kn' ? 'en' : 'kn')}
                title="Switch Language / ಭಾಷೆ ಬದಲಿಸಿ"
              >
                {lang === 'kn' ? 'English' : 'ಕನ್ನಡ'}
              </button>

              <button
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#94a3b8',
                  fontSize: '1.25rem',
                  cursor: 'pointer',
                  padding: '4px',
                  lineHeight: 1
                }}
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="raithanna-messages">
            {messages.map(m => (
              <div
                key={m.id}
                className={`raithanna-msg ${m.sender === 'user' ? 'raithanna-msg-user' : 'raithanna-msg-bot'}`}
              >
                {m.filePreview && (
                  <img
                    src={m.filePreview}
                    alt="Upload Preview"
                    style={{ width: '100%', maxHeight: '160px', objectFit: 'cover', borderRadius: '8px', marginBottom: '8px' }}
                  />
                )}
                <div style={{ whiteSpace: 'pre-wrap' }}>{m.text}</div>

                {m.sender === 'bot' && (
                  <button
                    className="raithanna-audio-btn"
                    onClick={() => speakText(m.text)}
                    title={lang === 'kn' ? "ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ" : "Listen aloud"}
                  >
                    <span>{isSpeaking ? '⏹️ ನಿಲ್ಲಿಸಿ' : '🔊 ಕೇಳಿ (Listen)'}</span>
                  </button>
                )}

                <div style={{ fontSize: '0.68rem', opacity: 0.6, marginTop: '4px', textAlign: 'right' }}>
                  {m.time}
                </div>
              </div>
            ))}

            {loading && (
              <div className="raithanna-msg raithanna-msg-bot" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                <span>{lang === 'kn' ? 'ರೈತಣ್ಣ ಯೋಚಿಸುತ್ತಿದ್ದಾರೆ…' : 'Raithanna is thinking…'}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Action Chips & Follow-up Suggestions */}
          <div className="raithanna-chips">
            {contextChips && contextChips.length > 0 ? (
              contextChips.map((chip, idx) => (
                <button
                  key={`ctx-${idx}`}
                  className="raithanna-chip-btn"
                  style={{ borderColor: '#22c55e', background: 'rgba(34, 197, 94, 0.12)' }}
                  onClick={() => handleSend(chip)}
                >
                  <span>✨</span>
                  <span>{chip}</span>
                </button>
              ))
            ) : (
              quickActions.map(act => (
                <button
                  key={act.id}
                  className="raithanna-chip-btn"
                  onClick={() => handleSend(lang === 'kn' ? act.prompt_kn : act.prompt_en)}
                >
                  <span>{act.icon}</span>
                  <span>{lang === 'kn' ? act.title_kn : act.title_en}</span>
                </button>
              ))
            )}
          </div>

          {/* Input Bar */}
          <div className="raithanna-input-bar">
            {/* Hidden file inputs */}
            <input
              type="file"
              accept="image/*"
              capture="environment"
              ref={photoInputRef}
              style={{ display: 'none' }}
              onChange={handlePhotoUpload}
            />
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleDocUpload}
            />

            <div className="raithanna-input-row">
              {/* Photo Upload Button */}
              <button
                className="raithanna-icon-btn"
                onClick={() => photoInputRef.current?.click()}
                title={lang === 'kn' ? "ಎಲೆಯ ರೋಗದ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ" : "Upload Leaf Disease Photo"}
              >
                📷
              </button>

              {/* Document Attachment Button */}
              <button
                className="raithanna-icon-btn"
                onClick={() => fileInputRef.current?.click()}
                title={lang === 'kn' ? "ಮಣ್ಣು ವರದಿ / ಫೈಲ್ ಲಗತ್ತಿಸಿ" : "Attach Soil Report / File"}
              >
                📎
              </button>

              {/* Voice Speech Button */}
              <button
                className={`raithanna-icon-btn ${recording ? 'recording' : ''}`}
                onClick={toggleVoiceRecording}
                title={lang === 'kn' ? "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ (Voice)" : "Speak via Voice"}
              >
                {recording ? '🔴' : '🎙️'}
              </button>

              {/* Text Input */}
              <input
                className="raithanna-input"
                type="text"
                placeholder={lang === 'kn' ? "ಕನ್ನಡದಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ..." : "Ask your farm question..."}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
              />

              {/* Send Button */}
              <button
                className="raithanna-send-btn"
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
