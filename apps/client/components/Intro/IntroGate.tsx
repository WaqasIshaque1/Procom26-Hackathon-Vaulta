"use client";

import React, { useEffect, useState } from "react";
import LandingPage from "./LandingPage";

const SESSION_KEY = "intro_gate_passed";

export default function IntroGate({ children }: { children: React.ReactNode }) {
    const [authorized, setAuthorized] = useState<boolean | null>(null);

    useEffect(() => {
        // Check session storage on mount
        // If not set, user is unauthorized
        const isPassed = sessionStorage.getItem(SESSION_KEY);
        setAuthorized(isPassed === "true");
    }, []);

    const handleAccessGranted = () => {
        sessionStorage.setItem(SESSION_KEY, "true");
        setAuthorized(true);
    };

    // Prevent flash of content (optional: show loading or nothing while checking)
    if (authorized === null) {
        return null; // Or a loading spinner
    }

    if (!authorized) {
        return <LandingPage onAccessGranted={handleAccessGranted} />;
    }

    return <>{children}</>;
}
