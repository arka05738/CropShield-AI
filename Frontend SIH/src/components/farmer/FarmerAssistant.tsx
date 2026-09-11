import React, { useState } from 'react';
import { Bot, Send, User as UserIcon, Sparkles, MessageSquare, BookOpen } from 'lucide-react';
import { api } from '../../services/api';
import { SupportedLanguage } from '../../i18n/translations';

interface FarmerAssistantProps {
  activeCrop?: string;
  language: SupportedLanguage;
}

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  time: string;
}

const QUICK_PROMPTS = [
  "What is the exact dosage for Early Blight on Tomato?",
  "Should I irrigate today given current humidity?",
  "What are the non-chemical IPM steps for aphids?",
  "How should I adjust NPK fertilizers for recovery?"
];

export const FarmerAssistant: React.FC<FarmerAssistantProps> = ({
  activeCrop,
  language
}) => {
  const cropLabel = activeCrop || 'your crop';
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: `Namaste! I am your CropShield Agronomic Copilot. I can help with ICAR Package of Practices guidance for ${cropLabel}. How can I assist your crop protection today?`,
      time: 'Just now'
    }
  ]);
  const [input, setInput] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    const userMsg: Message = {
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setIsSending(true);

    try {
      const res = await api.chatAssistant(query, activeCrop, language);
      const botMsg: Message = {
        sender: 'assistant',
        text: res.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: "I am having trouble connecting to the RAG knowledge service right now. Please verify your internet connection or try again shortly.",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="glass-card rounded-2xl p-5 border border-emerald-500/20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-700 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-500/20">
            <Bot className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white font-['Outfit']">
                CropShield Agronomic Copilot
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                ICAR POP RAG
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Active Context: <strong className="text-emerald-300">{cropLabel}</strong> • Responds in your selected language
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950/70 px-3 py-1.5 rounded-xl border border-slate-800">
          <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
          <span>Grounded in official ICAR manuals</span>
        </div>
      </div>

      {/* Chat Container */}
      <div className="glass-card rounded-2xl border border-slate-800 flex flex-col h-[520px] overflow-hidden">
        {/* Messages List */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-500/30">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-lg p-3.5 rounded-2xl text-xs leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-emerald-500 text-slate-950 font-medium rounded-tr-none shadow-md shadow-emerald-500/20'
                    : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none space-y-1'
                }`}
              >
                <div className="whitespace-pre-line">{m.text}</div>
                <span className={`block text-[9px] mt-1 ${m.sender === 'user' ? 'text-slate-800' : 'text-slate-500'}`}>
                  {m.time}
                </span>
              </div>

              {m.sender === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center shrink-0">
                  <UserIcon className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isSending && (
            <div className="flex items-center gap-2 text-xs text-slate-400 italic">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-spin" />
              <span>Querying ChromaDB vector index & synthesizing response...</span>
            </div>
          )}
        </div>

        {/* Quick Prompt Chips */}
        <div className="px-4 py-2 bg-slate-950/70 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto text-xs">
          <span className="text-slate-400 font-medium shrink-0">Suggestions:</span>
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors whitespace-nowrap text-[11px]"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={`Ask about ${cropLabel} diseases, dosage, knapsack calibration, or IPM...`}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
          <button
            onClick={() => handleSend()}
            disabled={isSending || !input.trim()}
            className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Ask</span>
          </button>
        </div>
      </div>
    </div>
  );
};
