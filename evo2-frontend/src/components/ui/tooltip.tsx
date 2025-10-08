"use client";

import { useState } from "react";
import { Info } from "lucide-react";

interface TooltipProps {
  content: string;
}

export function Tooltip({ content }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="flex items-center gap-1 cursor-help"
      >
        <Info className="h-3 w-3 text-[#3c4f3d]/40 hover:text-[#3c4f3d]/70" />
        <span className="text-[10px] text-[#3c4f3d]/30 hover:text-[#3c4f3d]/50">hover me</span>
      </div>
      {isVisible && (
        <div className="absolute bottom-full right-0 mb-2 z-50">
          <div className="text-white text-xs rounded-md px-4 py-3 w-80 whitespace-normal shadow-lg" style={{ backgroundColor: '#3C4F3C' }}>
            {content}
            <div className="absolute top-full right-4 border-4 border-transparent" style={{ borderTopColor: '#3C4F3C' }}></div>
          </div>
        </div>
      )}
    </div>
  );
}