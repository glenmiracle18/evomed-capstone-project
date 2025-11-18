import * as React from "react";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline";
}

function Badge({ className = "", variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-[#3c4f3d] text-white",
    secondary: "bg-[#e9eeea] text-[#3c4f3d]",
    destructive: "bg-red-500 text-white",
    outline: "border border-[#3c4f3d]/20 text-[#3c4f3d]",
  };

  return (
    <div
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors ${variants[variant]} ${className}`}
      {...props}
    />
  );
}

export { Badge };
