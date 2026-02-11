import { useState } from "react";
import VideoThumb from "@/public/images/hero-image-01.jpg";
import ModalVideo from "@/components/Intro/ModalVideo";
import { verifyAccessCode } from "@/app/actions/auth";

export default function HeroHome({ onAccessGranted }: { onAccessGranted: () => void }) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleStart = async () => {
    if (!code) return;
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
    <section>
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        {/* Hero content */}
        <div className="py-12 md:py-20">
          {/* Section header */}
          <div className="pb-12 text-center md:pb-20">
            <h1
              className="animate-gradient bg-gradient-to-r from-gray-200 via-indigo-200 to-gray-200 bg-[length:200%_auto] bg-clip-text pb-5 font-nacelle text-4xl font-semibold text-transparent md:text-5xl"
              data-aos="fade-up"
            >
              Vaulta
            </h1>
            <div className="mx-auto max-w-3xl">
              <p
                className="mb-8 text-xl text-indigo-200/65"
                data-aos="fade-up"
                data-aos-delay={200}
              >
                Your voice is your password. Bank securely with biometric voice verification, instant card blocking, and real-time balance checks—all through natural conversation.
              </p>
              <div className="mx-auto max-w-md sm:flex sm:max-w-none sm:justify-center">
                <div data-aos="fade-up" data-aos-delay={400} className="w-full sm:w-auto">
                  <div className="relative flex items-center gap-2">
                    <input
                      type="text"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="Enter Access Code"
                      className="h-12 w-full rounded-lg border-0 bg-white/10 px-4 text-white placeholder-white/50 backdrop-blur-sm focus:ring-2 focus:ring-indigo-500 sm:w-64"
                    />
                    <button
                      onClick={handleStart}
                      disabled={loading || !code}
                      className="btn h-12 group bg-gradient-to-t from-indigo-600 to-indigo-500 bg-[length:100%_100%] bg-[bottom] text-white shadow-[inset_0px_1px_0px_0px_--theme(--color-white/.16)] hover:bg-[length:100%_150%] rounded-lg px-6 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? "Verifying..." : "Connect"}
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-2 h-4 w-4 text-white/50 transition-transform group-hover:translate-x-0.5">
                        <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                  {error && (
                    <p className="mt-2 text-sm text-red-400 font-medium animate-pulse">
                      {error}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <ModalVideo
            thumb={VideoThumb}
            thumbWidth={1104}
            thumbHeight={576}
            thumbAlt="Modal video thumbnail"
            video="videos/video.mp4"
            videoWidth={1920}
            videoHeight={1080}
          />
        </div>
      </div>
    </section>
  );
}
