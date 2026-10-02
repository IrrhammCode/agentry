import React, { useEffect, useRef, useState } from 'react';

export type RevealAnimation = 
  | 'fade-up' 
  | 'fade-down' 
  | 'fade-left' 
  | 'fade-right' 
  | 'zoom-in' 
  | 'blur-in';

interface ScrollRevealProps {
  children: React.ReactNode;
  animation?: RevealAnimation;
  delayMs?: number;
  durationMs?: number;
  threshold?: number;
  once?: boolean;
  className?: string;
}

export const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  animation = 'fade-up',
  delayMs = 0,
  durationMs = 700,
  threshold = 0.15,
  once = true,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const domRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = domRef.current;
    if (!node) return;

    // Check if IntersectionObserver is available
    if (!('IntersectionObserver' in window)) {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            if (once) {
              observer.unobserve(entry.target);
            }
          } else if (!once) {
            setIsVisible(false);
          }
        });
      },
      {
        threshold,
        rootMargin: '0px 0px -40px 0px', // Triggers slightly before element enters view
      }
    );

    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, [threshold, once]);

  const getAnimationStyles = () => {
    const baseTransition = `opacity ${durationMs}ms cubic-bezier(0.16, 1, 0.3, 1) ${delayMs}ms, transform ${durationMs}ms cubic-bezier(0.16, 1, 0.3, 1) ${delayMs}ms, filter ${durationMs}ms cubic-bezier(0.16, 1, 0.3, 1) ${delayMs}ms`;

    if (isVisible) {
      return {
        opacity: 1,
        transform: 'translate3d(0, 0, 0) scale(1)',
        filter: 'blur(0px)',
        transition: baseTransition,
        willChange: 'opacity, transform, filter',
      };
    }

    switch (animation) {
      case 'fade-up':
        return {
          opacity: 0,
          transform: 'translate3d(0, 40px, 0) scale(0.98)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      case 'fade-down':
        return {
          opacity: 0,
          transform: 'translate3d(0, -40px, 0) scale(0.98)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      case 'fade-left':
        return {
          opacity: 0,
          transform: 'translate3d(40px, 0, 0)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      case 'fade-right':
        return {
          opacity: 0,
          transform: 'translate3d(-40px, 0, 0)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      case 'zoom-in':
        return {
          opacity: 0,
          transform: 'translate3d(0, 20px, 0) scale(0.92)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      case 'blur-in':
        return {
          opacity: 0,
          transform: 'translate3d(0, 0, 0)',
          filter: 'blur(12px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
      default:
        return {
          opacity: 0,
          transform: 'translate3d(0, 30px, 0)',
          filter: 'blur(4px)',
          transition: baseTransition,
          willChange: 'opacity, transform, filter',
        };
    }
  };

  return (
    <div
      ref={domRef}
      style={getAnimationStyles()}
      className={className}
    >
      {children}
    </div>
  );
};
