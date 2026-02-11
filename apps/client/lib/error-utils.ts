export const sanitizeError = (error: unknown, context?: string): string => {
    const errorMessage = error instanceof Error ? error.message : String(error);

    // Log the full technical error for developers
    console.error(`[Internal Error]${context ? ` [${context}]` : ''}:`, error);

    // Map specific technical errors to user-friendly messages
    if (errorMessage.toLowerCase().includes('vapi public key not configured') ||
        errorMessage.toLowerCase().includes('missing vapi credentials')) {
        return 'Environmental credentials not setup';
    }

    if (errorMessage.toLowerCase().includes('assistant configuration missing')) {
        return 'Service configuration is incomplete';
    }

    if (errorMessage.toLowerCase().includes('failed to initialize')) {
        return 'Unable to initialize secure connection';
    }

    if (errorMessage.toLowerCase().includes('permission denied') ||
        errorMessage.toLowerCase().includes('microphone')) {
        return 'Microphone access is required for this feature';
    }

    // Default safe message for unknown errors
    return 'An unexpected issue occurred. Please try again later.';
};
