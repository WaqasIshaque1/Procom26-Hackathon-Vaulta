"use server";

export async function verifyAccessCode(inputCode: string): Promise<boolean> {
    // Simple check against environment variable
    // In a real app, uses strict equality or a more secure comparison if needed
    // This runs on the server, so ACCESS_CODE is hidden
    const correctCode = process.env.ACCESS_CODE;

    if (!correctCode) {
        console.warn("ACCESS_CODE is not defined in environment variables.");
        return false;
    }

    return inputCode === correctCode;
}
