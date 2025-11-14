"use client";

import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { Info } from "lucide-react";

interface TooltipProps {
  content: string;
}

export function Tooltip({ content }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setPosition({
        top: rect.top - 10, // Position above the trigger
        left: rect.right - 320, // Align to the right (320px is tooltip width)
      });
    }
  }, [isVisible]);

  const tooltipContent = isVisible ? (
    <div 
      className="fixed z-[99999] pointer-events-none"
      style={{ 
        top: `${position.top}px`, 
        left: `${Math.max(10, position.left)}px` // Ensure it doesn't go off-screen
      }}
    >
      <div className="text-white text-xs rounded-md px-4 py-3 w-80 whitespace-normal shadow-lg" style={{ backgroundColor: '#3C4F3C' }}>
        {content}
        <div className="absolute top-full right-4 border-4 border-transparent" style={{ borderTopColor: '#3C4F3C' }}></div>
      </div>
    </div>
  ) : null;

  return (
    <>
      <div 
        ref={triggerRef}
        className="relative inline-block"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        <div className="flex items-center gap-1 cursor-help">
          <Info className="h-3 w-3 text-[#3c4f3d]/40 hover:text-[#3c4f3d]/70" />
          <span className="text-[10px] text-[#3c4f3d]/30 hover:text-[#3c4f3d]/50">hover me</span>
        </div>
      </div>
      {typeof window !== 'undefined' && tooltipContent && createPortal(tooltipContent, document.body)}
    </>
  );
}