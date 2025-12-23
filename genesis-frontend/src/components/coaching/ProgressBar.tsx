import { CoachingStepEnum } from '@/types/coaching';

interface ProgressBarProps {
    progress: Record<string, boolean>;
    currentStep: CoachingStepEnum;
}

const STEPS = [
    { key: CoachingStepEnum.VISION, label: 'Vision', icon: '👁️' },
    { key: CoachingStepEnum.MISSION, label: 'Mission', icon: '🎯' },
    { key: CoachingStepEnum.CLIENTELE, label: 'Clientèle', icon: '👥' },
    { key: CoachingStepEnum.DIFFERENTIATION, label: 'Différenciation', icon: '⭐' },
    { key: CoachingStepEnum.OFFRE, label: 'Offre', icon: '💼' }
];

export default function ProgressBar({ progress, currentStep }: ProgressBarProps) {
    const currentIndex = STEPS.findIndex((s) => s.key === currentStep);

    return (
        <div className="relative mb-8 w-full max-w-3xl mx-auto px-2">
            {/* Ligne de fond */}
            <div className="absolute left-[6%] right-[6%] top-1/2 h-1 bg-gray-700/60 rounded-full -z-0" />

            <div className="flex justify-between items-center relative z-10">
                {STEPS.map((step, index) => {
                    const isCompleted = progress[step.key];
                    const isCurrent = currentStep === step.key;
                    const isPast = index < currentIndex;
                    const statusClass = isCompleted || isPast
                        ? 'bg-green-500 border-green-400 text-white shadow-[0_0_10px_rgba(34,197,94,0.5)]'
                        : isCurrent
                            ? 'bg-purple-600 border-purple-400 text-white animate-pulse shadow-[0_0_15px_rgba(147,51,234,0.6)]'
                            : 'bg-gray-800 border-gray-600 text-gray-400';

                    return (
                        <div key={step.key} className="flex flex-col items-center flex-1">
                            {/* Connecteur gauche rempli */}
                            {index > 0 && (
                                <div
                                    className={`w-full h-1 -mb-2 ${
                                        index <= currentIndex ? 'bg-gradient-to-r from-green-400 to-purple-500' : 'bg-transparent'
                                    } hidden md:block`}
                                />
                            )}
                            <div
                                className={`mx-auto w-10 h-10 rounded-full flex items-center justify-center text-xl transition-all duration-300 border-2 ${statusClass}`}
                            >
                                {step.icon}
                            </div>
                            <span
                                className={`text-xs mt-2 font-medium transition-colors duration-300 ${
                                    isCurrent ? 'text-purple-300' : isCompleted || isPast ? 'text-green-400' : 'text-gray-500'
                                }`}
                            >
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
