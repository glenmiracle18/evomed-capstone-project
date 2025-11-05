"use client";

import { SignInButton, SignUpButton, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function LandingPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [contentVisible, setContentVisible] = useState(false);

  useEffect(() => {
    if (isLoaded && user) {
      router.push("/app");
    }
  }, [isLoaded, user, router]);

  useEffect(() => {
    // Trigger fade-in animation after component mounts
    const timer = setTimeout(() => {
      setContentVisible(true);
    }, 100); // Small delay to ensure smooth animation

    return () => clearTimeout(timer);
  }, []);

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-center">
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (user) {
    return null; // Will redirect to /app
  }

  return (
    <div className="min-h-screen relative flex flex-col overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
      >
        <source src="/landingpage-video2.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Dark tinted overlay */}
      <div className="absolute inset-0 bg-black/60 z-10"></div>

      {/* Content overlay */}
      <div className={`relative z-20 min-h-screen text-white flex flex-col transition-all duration-1000 ease-out ${
        contentVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center space-y-8 max-w-2xl">
            <h1 className="text-7xl md:text-8xl font-light drop-shadow-2xl">
              EvoMed
            </h1>

            <h2 className="text-3xl md:text-4xl font-light drop-shadow-lg">
              African Variant Analysis ML Model
            </h2>

            <p className="text-xl md:text-2xl text-gray-100 leading-relaxed drop-shadow-md">
              Advanced genomic variant analysis powered by machine learning.
              Explore genetic variants, analyze gene sequences, and discover insights
              from comprehensive genomic data.
            </p>

            <div className="space-y-4 pt-8">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <SignInButton>
                  <button className="px-10 py-4 border border-white text-white hover:bg-white hover:text-black transition-all duration-300 text-xl backdrop-blur-sm bg-white/10 hover:bg-white/90 shadow-xl">
                    Sign In
                  </button>
                </SignInButton>

                <SignUpButton>
                  <button className="px-10 py-4 bg-white text-black hover:bg-gray-200 transition-all duration-300 text-xl shadow-xl hover:shadow-2xl">
                    Get Started
                  </button>
                </SignUpButton>
              </div>

              <p className="text-base text-gray-200 drop-shadow-sm">
                Sign up to access the genomic analysis platform
              </p>
            </div>
          </div>
        </div>

        <footer className="border-t border-white/20 p-6 text-center text-sm text-gray-200 backdrop-blur-sm bg-black/20">
          <p>© {new Date().getFullYear()} • Author: Glen Miracle • School: African Leadership University</p>
        </footer>
      </div>
    </div>
  );
}
