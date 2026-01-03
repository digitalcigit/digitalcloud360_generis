'use client';

import { motion, useAnimation, useInView } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface RevealProps {
    children: React.ReactNode;
    width?: 'fit-content' | '100%';
    delay?: number;
    duration?: number;
    className?: string;
    variant?: 'fadeIn' | 'slideUp' | 'slideLeft' | 'slideRight' | 'scale';
}

export const Reveal = ({ 
    children, 
    width = '100%', 
    delay = 0.25, 
    duration = 0.5,
    className = "",
    variant = 'slideUp'
}: RevealProps) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-10% 0px -10% 0px" });
    const mainControls = useAnimation();

    useEffect(() => {
        if (isInView) {
            mainControls.start("visible");
        }
    }, [isInView, mainControls]);

    const getVariants = () => {
        switch (variant) {
            case 'fadeIn':
                return {
                    hidden: { opacity: 0 },
                    visible: { opacity: 1 }
                };
            case 'slideLeft':
                return {
                    hidden: { opacity: 0, x: -75 },
                    visible: { opacity: 1, x: 0 }
                };
            case 'slideRight':
                return {
                    hidden: { opacity: 0, x: 75 },
                    visible: { opacity: 1, x: 0 }
                };
            case 'scale':
                return {
                    hidden: { opacity: 0, scale: 0.8 },
                    visible: { opacity: 1, scale: 1 }
                };
            case 'slideUp':
            default:
                return {
                    hidden: { opacity: 0, y: 75 },
                    visible: { opacity: 1, y: 0 }
                };
        }
    };

    return (
        <div ref={ref} style={{ position: 'relative', width }} className={className}>
            <motion.div
                variants={getVariants()}
                initial="hidden"
                animate={mainControls}
                transition={{ duration, delay, ease: "easeOut" }}
            >
                {children}
            </motion.div>
        </div>
    );
};
