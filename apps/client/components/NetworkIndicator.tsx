"use client";

import React, { useEffect, useState, useRef } from "react";
import { Signal, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface NetworkInfo {
    ip: string;
    city: string;
    region: string;
    country: string;
    org: string;
    userAgent: string;
}

export default function NetworkIndicator() {
    const [isOnline, setIsOnline] = useState(true);
    const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null);
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [quality, setQuality] = useState<'good' | 'moderate' | 'poor'>('good');
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (typeof window === "undefined") return;

        const updateNetworkStatus = () => {
            const online = navigator.onLine;
            setIsOnline(online);

            if (!online) {
                setQuality('poor');
                return;
            }

            // @ts-ignore - navigator.connection is not standard
            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

            if (connection) {
                const type = connection.effectiveType; // '4g', '3g', '2g', 'slow-2g'
                const rtt = connection.rtt; // Round-trip time

                if (type === 'slow-2g' || type === '2g') {
                    setQuality('poor');
                } else if (type === '3g') {
                    setQuality('moderate');
                } else {
                    // 4g or better, check RTT to refine
                    if (rtt && rtt > 500) {
                        setQuality('moderate');
                    } else {
                        setQuality('good');
                    }
                }
            } else {
                // Fallback if API not supported
                setQuality('good');
            }
        };

        window.addEventListener("online", updateNetworkStatus);
        window.addEventListener("offline", updateNetworkStatus);

        // Initial check
        updateNetworkStatus();

        // Listen to connection changes if supported
        // @ts-ignore
        const connection = navigator.connection;
        if (connection) {
            connection.addEventListener('change', updateNetworkStatus);
        }

        // Close popup when clicking outside
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);

        return () => {
            window.removeEventListener("online", updateNetworkStatus);
            window.removeEventListener("offline", updateNetworkStatus);
            document.removeEventListener("mousedown", handleClickOutside);
            if (connection) {
                connection.removeEventListener('change', updateNetworkStatus);
            }
        };
    }, []);

    const fetchNetworkInfo = async () => {
        if (networkInfo) return; // Cache logic: fetch once
        setLoading(true);
        try {
            const res = await fetch("https://ipapi.co/json/");
            const data = await res.json();
            setNetworkInfo({
                ip: data.ip,
                city: data.city,
                region: data.region,
                country: data.country_name,
                org: data.org,
                userAgent: navigator.userAgent,
            });
        } catch (error) {
            console.error("Failed to fetch network info", error);
            // Fallback
            setNetworkInfo({
                ip: "Unknown",
                city: "Unknown",
                region: "Unknown",
                country: "Unknown",
                org: "Unknown",
                userAgent: navigator.userAgent,
            });
        } finally {
            setLoading(false);
        }
    };

    const togglePopup = () => {
        if (!isOpen) {
            setIsOpen(true);
            fetchNetworkInfo();
        } else {
            setIsOpen(false);
        }
    };

    const getSignalIcon = () => {
        if (!isOnline) return <WifiOff className="h-4 w-4" />;
        if (quality === 'poor') return <Signal className="h-4 w-4" />; // Or SignalLow if imported
        if (quality === 'moderate') return <Signal className="h-4 w-4" />; // Or SignalMedium
        return <Signal className="h-4 w-4" />;
    };

    const getStatusColor = () => {
        if (!isOnline) return "bg-red-100 border-red-200 text-red-600 dark:bg-red-900/30 dark:border-red-800 dark:text-red-400";
        switch (quality) {
            case 'good':
                return "bg-emerald-100 border-emerald-200 text-emerald-600 dark:bg-emerald-900/30 dark:border-emerald-800 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-900/50";
            case 'moderate':
                return "bg-amber-100 border-amber-200 text-amber-600 dark:bg-amber-900/30 dark:border-amber-800 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-900/50";
            case 'poor':
                return "bg-red-100 border-red-200 text-red-600 dark:bg-red-900/30 dark:border-red-800 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50";
        }
    };

    return (
        <div className="relative" ref={containerRef}>
            <div
                className={cn(
                    "flex items-center justify-center h-8 w-8 rounded-full border transition-colors cursor-pointer",
                    getStatusColor()
                )}
                onClick={togglePopup}
                title={`Network: ${isOnline ? quality.charAt(0).toUpperCase() + quality.slice(1) : 'Offline'}`}
            >
                {getSignalIcon()}
            </div>

            {isOpen && (
                <>
                    {/* Backdrop for mobile to handle outside clicks better and dim background */}
                    <div className="fixed inset-0 z-40 bg-black/5 md:hidden" onClick={() => setIsOpen(false)} />

                    <div className="absolute left-0 top-10 z-50 w-[280px] sm:w-80 rounded-xl border border-slate-200 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-950 animate-in fade-in zoom-in-95 duration-200 origin-top-left">
                        <div className="bg-slate-50 dark:bg-slate-900/50 p-3 sm:p-4 border-b border-slate-200 dark:border-slate-800 rounded-t-xl">
                            <h4 className="font-semibold text-sm flex items-center gap-2 text-foreground">
                                {isOnline ? (
                                    <Wifi className={cn("h-4 w-4",
                                        quality === 'good' ? "text-emerald-500" :
                                            quality === 'moderate' ? "text-amber-500" : "text-red-500"
                                    )} />
                                ) : <WifiOff className="h-4 w-4 text-red-500" />}
                                Network Information
                            </h4>
                            <p className="text-xs text-muted-foreground mt-1">
                                {isOnline
                                    ? `Connected (${quality === 'good' ? 'Strong' : quality === 'moderate' ? 'Moderate' : 'Poor'} Signal)`
                                    : "No internet connection"}
                            </p>
                        </div>
                        <div className="p-3 sm:p-4 space-y-3 text-xs text-foreground">
                            {loading ? (
                                <div className="flex justify-center py-4">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-emerald-500"></div>
                                </div>
                            ) : networkInfo ? (
                                <>
                                    <div className="grid grid-cols-[70px_1fr] sm:grid-cols-[80px_1fr] gap-1">
                                        <span className="text-muted-foreground">IP Addr:</span>
                                        <span className="font-medium font-mono select-all break-all">{networkInfo.ip}</span>
                                    </div>
                                    <div className="grid grid-cols-[70px_1fr] sm:grid-cols-[80px_1fr] gap-1">
                                        <span className="text-muted-foreground">Location:</span>
                                        <span className="font-medium break-words">{networkInfo.city}, {networkInfo.region}, {networkInfo.country}</span>
                                    </div>
                                    <div className="grid grid-cols-[70px_1fr] sm:grid-cols-[80px_1fr] gap-1">
                                        <span className="text-muted-foreground">Provider:</span>
                                        <span className="font-medium break-words">{networkInfo.org}</span>
                                    </div>
                                    <div className="grid grid-cols-[70px_1fr] sm:grid-cols-[80px_1fr] gap-1">
                                        <span className="text-muted-foreground">Device ID:</span>
                                        <span className="font-medium text-muted-foreground italic truncate" title="Browsers do not provide MAC Address access">
                                            (Hidden/Protected)
                                        </span>
                                    </div>
                                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 mt-2">
                                        <span className="text-muted-foreground block mb-1">User Agent:</span>
                                        <div className="max-h-20 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-700">
                                            <span className="font-mono text-[10px] text-slate-500 break-all leading-tight block">
                                                {networkInfo.userAgent}
                                            </span>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="text-red-500 text-center py-2">Could not load details</div>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
