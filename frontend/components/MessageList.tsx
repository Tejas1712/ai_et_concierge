"use client";

import { useEffect, useRef } from "react";
import type { Message } from "../lib/types";
import AlphaAvatar from "./AlphaAvatar";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  personaType?: string;
}

/** Renders **bold** and *italic* markdown as actual HTML */
function renderMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")   // **bold**
    .replace(/\*(.+?)\*/g, "<em>$1</em>")               // *italic*
    .replace(/\n/g, "<br />");                           // newlines
}

export default function MessageList({ messages, isLoading, personaType = "default" }: MessageListProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-thread">
      {messages.length === 0 && (
        <p className="thread-empty">Start the conversation with your personal assistant</p>
      )}
      {messages.map((msg, index) => (
        <div
          key={`${msg.role}-${index}`}
          className={msg.role === "user" ? "bubble bubble-user" : "bubble bubble-assistant"}
        >
          {msg.role === "assistant" && (
            <div className="bubble-avatar">
              <AlphaAvatar persona={personaType} size={36} />
            </div>
          )}
          <div className="bubble-body">
            <div className="bubble-label">
              {msg.role === "user" ? "You" : "AlphaAssist"}
            </div>
            <div
              className="bubble-content"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
            />
          </div>
        </div>
      ))}
      {isLoading && (
        <div className="bubble bubble-assistant">
          <div className="bubble-avatar">
            <AlphaAvatar persona={personaType} size={36} />
          </div>
          <div className="bubble-body">
            <div className="bubble-label">AlphaAssist</div>
            <div className="thread-loading">Thinking...</div>
          </div>
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
