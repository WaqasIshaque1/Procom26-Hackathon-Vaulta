"use client";

import React, { useState, useEffect } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import { MoveRight, ShieldCheck, MessageCircle, Lock, LayoutGrid, CheckCircle2, Landmark } from "lucide-react";
import { verifyAccessCode } from "@/app/actions/auth";

export default function IntroUI({ onAccessGranted }: { onAccessGranted: () => void }) {
    const [isChecked, setIsChecked] = useState(false);
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleStart = async () => {
        if (!isChecked || !code) return;
        setLoading(true);
        setError("");

        try {
            const isValid = await verifyAccessCode(code);
            if (isValid) {
                onAccessGranted();
            } else {
                setError("Invalid Access Code. Please try again.");
            }
        } catch (err) {
            setError("An error occurred. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-black text-white">
            {/* Background Video */}
            <video
                autoPlay
                loop
                muted
                playsInline
                className="absolute inset-0 h-full w-full object-cover opacity-60 blur-sm brightness-50"
            >
                <source src="/wave-bg.mp4" type="video/mp4" />
            </video>

            {/* Branding */}
            <div className="absolute top-6 left-6 z-20 flex items-center gap-3 md:gap-4">
                <div className="flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md border border-white/20 shadow-lg">
                    <Landmark className="h-5 w-5 md:h-7 md:w-7 text-white" />
                </div>
                <div className="flex flex-col">
                    <h1 className="text-lg md:text-xl font-bold tracking-wide text-white drop-shadow-md">
                        Vaulta
                    </h1>
                    <p className="text-[10px] md:text-xs font-medium text-white/60 tracking-wider uppercase">
                        Secure Banking AI Agent Portal
                    </p>
                </div>
            </div>

            {/* Language Switcher (Mock) */}
            <div className="absolute top-6 right-6 z-20">
                <div className="flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm backdrop-blur-md transition hover:bg-white/20 cursor-pointer">
                    <span className="font-medium">EN</span>
                    <span className="opacity-50">/</span>
                    <span className="font-medium opacity-50">ES</span>
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 w-full max-w-4xl px-4">
                <Swiper
                    modules={[Pagination, Navigation]}
                    pagination={{ clickable: true }}
                    navigation={true}
                    spaceBetween={30}
                    slidesPerView={1}
                    className="intro-swiper h-[500px] md:h-[600px] w-full max-w-[800px] mx-auto !pb-12"
                >
                    {/* Slide 1: Purpose */}
                    <SwiperSlide>
                        <div className="flex h-full flex-col items-center justify-center gap-4 md:gap-8 rounded-3xl border border-white/10 bg-white/10 p-6 md:p-8 text-center backdrop-blur-md shadow-2xl">
                            <div className="flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-blue-500/20 shadow-inner ring-1 ring-blue-500/50">
                                <LayoutGrid className="h-8 w-8 md:h-10 md:w-10 text-blue-300" />
                            </div>
                            <div className="space-y-3 md:space-y-4 max-w-lg">
                                <h2 className="text-2xl md:text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-200 to-white bg-clip-text text-transparent">
                                    Fast & Reliable Banking
                                </h2>
                                <p className="text-sm md:text-lg leading-relaxed text-blue-100/80">
                                    Experience seamless banking services without the wait.
                                    Check balances and get real-time support instantly,
                                    optimized for high-traffic situations.
                                </p>
                            </div>
                        </div>
                    </SwiperSlide>

                    {/* Slide 2: Security */}
                    <SwiperSlide>
                        <div className="flex h-full flex-col items-center justify-center gap-4 md:gap-8 rounded-3xl border border-white/10 bg-white/10 p-6 md:p-8 text-center backdrop-blur-md shadow-2xl">
                            <div className="flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-emerald-500/20 shadow-inner ring-1 ring-emerald-500/50">
                                <ShieldCheck className="h-8 w-8 md:h-10 md:w-10 text-emerald-300" />
                            </div>
                            <div className="space-y-3 md:space-y-4 max-w-lg">
                                <h2 className="text-2xl md:text-4xl font-bold tracking-tight bg-gradient-to-r from-emerald-200 to-white bg-clip-text text-transparent">
                                    Secure & Private
                                </h2>
                                <p className="text-sm md:text-lg leading-relaxed text-emerald-100/80">
                                    Your privacy is our priority. We verify necessary data for
                                    service improvements but never store your secret keys or passwords.
                                    Safe, transparent, and secure.
                                </p>
                            </div>
                        </div>
                    </SwiperSlide>

                    {/* Slide 3: Features */}
                    <SwiperSlide>
                        <div className="flex h-full flex-col items-center justify-center gap-4 md:gap-8 rounded-3xl border border-white/10 bg-white/10 p-6 md:p-8 text-center backdrop-blur-md shadow-2xl">
                            <div className="flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-purple-500/20 shadow-inner ring-1 ring-purple-500/50">
                                <MessageCircle className="h-8 w-8 md:h-10 md:w-10 text-purple-300" />
                            </div>
                            <div className="space-y-3 md:space-y-4 max-w-lg">
                                <h2 className="text-2xl md:text-4xl font-bold tracking-tight bg-gradient-to-r from-purple-200 to-white bg-clip-text text-transparent">
                                    Voice & Text Enabled
                                </h2>
                                <p className="text-sm md:text-lg leading-relaxed text-purple-100/80">
                                    Communicate your way. Use our advanced voice agent for
                                    hands-free assistance or text chat for quick queries.
                                    <br />
                                    <span className="text-xs md:text-sm opacity-75 mt-2 inline-block font-semibold">
                                        * Microphone access recommended
                                    </span>
                                </p>
                            </div>
                        </div>
                    </SwiperSlide>

                    {/* Slide 4: Access */}
                    <SwiperSlide>
                        <div className="flex h-full flex-col items-center justify-center gap-4 md:gap-8 rounded-3xl border border-white/10 bg-white/10 p-6 md:p-8 text-center backdrop-blur-md shadow-2xl">
                            <div className="flex h-16 w-16 md:h-20 md:w-20 items-center justify-center rounded-full bg-amber-500/20 shadow-inner ring-1 ring-amber-500/50">
                                <Lock className="h-8 w-8 md:h-10 md:w-10 text-amber-300" />
                            </div>

                            <div className="space-y-4 md:space-y-6 w-full max-w-md">
                                <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                                    Get Started
                                </h2>

                                <div className="flex items-start gap-3 md:gap-4 text-left bg-black/20 p-3 md:p-4 rounded-xl border border-white/5">
                                    <div className="pt-1">
                                        <input
                                            type="checkbox"
                                            id="policy"
                                            checked={isChecked}
                                            onChange={(e) => setIsChecked(e.target.checked)}
                                            className="h-4 w-4 md:h-5 md:w-5 rounded border-white/30 bg-white/10 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                                        />
                                    </div>
                                    <label htmlFor="policy" className="text-xs md:text-sm text-gray-300 cursor-pointer select-none">
                                        I accept the <span className="text-white underline decoration-white/30 underline-offset-4">Privacy Policy</span> and
                                        agree to the terms of service. I understand verification is required.
                                    </label>
                                </div>

                                <div className="space-y-3 md:space-y-4 pt-2">
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={code}
                                            onChange={(e) => setCode(e.target.value)}
                                            disabled={!isChecked}
                                            placeholder="Enter Access Code"
                                            className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 md:px-6 md:py-4 text-center text-base md:text-lg tracking-widest text-white placeholder-white/30 shadow-inner backdrop-blur-sm transition focus:border-white/50 focus:bg-white/10 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                                        />
                                        {isChecked && code.length > 0 && (
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-green-400">
                                                {/* Status icon could go here */}
                                            </div>
                                        )}
                                    </div>

                                    {error && (
                                        <p className="text-red-400 text-xs md:text-sm font-medium animate-pulse">
                                            {error}
                                        </p>
                                    )}

                                    <button
                                        onClick={handleStart}
                                        disabled={!isChecked || !code || loading}
                                        className="group relative w-full overflow-hidden rounded-xl bg-white px-4 py-3 md:px-6 md:py-4 text-base md:text-lg font-bold text-black transition hover:bg-white/90 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
                                    >
                                        <span className="relative z-10 flex items-center justify-center gap-2">
                                            {loading ? "Verifying..." : "START AGENT"}
                                            {!loading && <MoveRight className="h-4 w-4 md:h-5 md:w-5 transition-transform group-hover:translate-x-1" />}
                                        </span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </SwiperSlide>
                </Swiper>

                {/* Custom Styles for Swiper Pagination/Nav */}
                <style jsx global>{`
          .swiper-pagination-bullet {
            background: white !important;
            opacity: 0.4;
          }
          .swiper-pagination-bullet-active {
            opacity: 1;
            transform: scale(1.2);
          }
          .swiper-button-next, .swiper-button-prev {
            color: white !important;
            opacity: 0.6;
            transition: opacity 0.3s;
          }
          .swiper-button-next:hover, .swiper-button-prev:hover {
            opacity: 1;
          }
          .swiper-button-next::after, .swiper-button-prev::after {
            font-size: 24px !important;
            font-weight: bold;
          }
        `}</style>

                {/* Footer */}
                <div className="mt-8 text-center">
                    <p className="text-xs text-white/40">
                        © 2024 Voice Agent AI. Secure Environment.
                    </p>
                </div>
            </div>
        </div>
    );
}
