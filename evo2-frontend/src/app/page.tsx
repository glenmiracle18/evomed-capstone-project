"use client";

import { SignInButton, SignUpButton, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LandingPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && user) {
      router.push("/app");
    }
  }, [isLoaded, user, router]);

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
    <div className="min-h-screen bg-black text-white flex flex-col">
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-8 max-w-2xl">
          <h1 className="text-6xl font-light">
            EvoMed
          </h1>
          
          <h2 className="text-2xl font-light">
            African Variant Analysis ML Model
          </h2>
          
          <p className="text-lg text-gray-300 leading-relaxed">
            Advanced genomic variant analysis powered by machine learning. 
            Explore genetic variants, analyze gene sequences, and discover insights 
            from comprehensive genomic data.
          </p>
          
          <div className="space-y-4 pt-8">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <SignInButton>
                <button className="px-8 py-3 border border-white text-white hover:bg-white hover:text-black transition-colors duration-200 text-lg">
                  Sign In
                </button>
              </SignInButton>
              
              <SignUpButton>
                <button className="px-8 py-3 bg-white text-black hover:bg-gray-200 transition-colors duration-200 text-lg">
                  Get Started
                </button>
              </SignUpButton>
            </div>
            
            <p className="text-sm text-gray-400">
              Sign up to access the genomic analysis platform
            </p>
          </div>
        </div>
      </div>
      
      <footer className="border-t border-gray-700 p-6 text-center text-sm text-gray-300 bg-gray-900">
        <p>© {new Date().getFullYear()} • Author: Glen Miracle • School: African Leadership University</p>
      </footer>
    </div>
  );
}