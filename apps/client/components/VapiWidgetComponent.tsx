declare global {
    namespace JSX {
        interface IntrinsicElements {
            'vapi-widget': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
                'public-key': string;
                'assistant-id': string;
                mode: string;
                theme: string;
                position: string;
                size: string;
                'start-button-text': string;
                'end-button-text': string;
            };
        }
    }
}

import Script from 'next/script';

const VapiWidgetComponent = () => {
    return (
        <>
            <Script
                src="https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js"
                strategy="afterInteractive"
            />
            <vapi-widget
                public-key={process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY || ''}
                assistant-id={process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID || ''}
                mode="chat"
                theme="dark"
                position="bottom-right"
                size="full"
                main-label="Chat with Vaulta"
                start-button-text="Start Voice Chat"
                end-button-text="End Call"
                base-color="#030616"
                accent-color="#3B82F6"
                button-base-color="#030616"
                button-accent-color="#FFFFFF"
            />
        </>
    );
};

export default VapiWidgetComponent;
