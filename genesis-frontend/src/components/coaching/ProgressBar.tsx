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
    return (
        <div className="flex justify-between items-center mb-8 px-4 w-full max-w-2xl mx-auto">
            {STEPS.map((step, index) => {
                const isCompleted = progress[step.key];
                const isCurrent = currentStep === step.key;
                
                return (
                    <div key={step.key} className="flex flex-col items-center relative z-10">
                        <div className={`
                            w-10 h-10 rounded-full flex items-center justify-center text-xl transition-all duration-300 border-2
                            ${isCompleted 
                                ? 'bg-green-500 border-green-400 text-white shadow-[0_0_10px_rgba(34,197,94,0.5)]' 
                                : isCurrent 
                                    ? 'bg-purple-600 border-purple-400 text-white animate-pulse shadow-[0_0_15px_rgba(147,51,234,0.6)]' 
                                    : 'bg-gray-800 border-gray-600 text-gray-400'}
                        `}>
                            {step.icon}
                        </div>
                        <span className={`text-xs mt-2 font-medium transition-colors duration-300 ${
                            isCurrent ? 'text-purple-300' : isCompleted ? 'text-green-400' : 'text-gray-500'
                        }`}>
                            {step.label}
                        </span>
                    </div>
                );
            })}
             {/* Ligne de fond pour relier les étapes (optionnel, pour l'esthétique) */}
             <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-700 -z-0 hidden md:block" />
        </div>
    );
}
