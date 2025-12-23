'use client';

import { useState } from 'react';
import { Upload } from 'lucide-react';

type LogoSource = 'upload' | 'generate' | 'later';

interface LogoUploaderProps {
    value: LogoSource | undefined;
    onChange: (source: LogoSource, logoUrl?: string | null) => void;
}

export default function LogoUploader({ value, onChange }: LogoUploaderProps) {
    const [preview, setPreview] = useState<string | null>(null);

    const handleFile = async (file?: File | null) => {
        if (!file) {
            setPreview(null);
            onChange('upload', null);
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            const url = reader.result as string;
            setPreview(url);
            onChange('upload', url);
        };
        reader.readAsDataURL(file);
    };

    return (
        <div className="space-y-3">
            <p className="text-sm text-gray-300 font-semibold">Avez-vous un logo ?</p>
            <div className="grid grid-cols-3 gap-3">
                <button
                    type="button"
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold transition-colors ${
                        value === 'upload'
                            ? 'border-purple-400 bg-purple-500/10 text-white'
                            : 'border-gray-700 bg-gray-800/60 text-gray-200 hover:border-purple-500/60'
                    }`}
                    onClick={() => onChange('upload', preview)}
                >
                    📤 Upload
                </button>
                <button
                    type="button"
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold transition-colors ${
                        value === 'generate'
                            ? 'border-purple-400 bg-purple-500/10 text-white'
                            : 'border-gray-700 bg-gray-800/60 text-gray-200 hover:border-purple-500/60'
                    }`}
                    onClick={() => onChange('generate', null)}
                >
                    🎨 Générer
                </button>
                <button
                    type="button"
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold transition-colors ${
                        value === 'later'
                            ? 'border-purple-400 bg-purple-500/10 text-white'
                            : 'border-gray-700 bg-gray-800/60 text-gray-200 hover:border-purple-500/60'
                    }`}
                    onClick={() => onChange('later', null)}
                >
                    ⏭️ Plus tard
                </button>
            </div>

            {value === 'upload' && (
                <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-gray-700 bg-gray-900/60 px-4 py-6 text-center hover:border-purple-400/60 transition-colors">
                    <Upload className="h-6 w-6 text-purple-300 mb-2" />
                    <span className="text-sm text-gray-300">Déposez un fichier (PNG/JPG)</span>
                    <input
                        type="file"
                        accept="image/png,image/jpeg"
                        className="hidden"
                        onChange={(e) => handleFile(e.target.files?.[0])}
                    />
                    {preview && (
                        <div className="mt-3 w-20 h-20 rounded-lg overflow-hidden border border-gray-700">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={preview} alt="Logo preview" className="h-full w-full object-cover" />
                        </div>
                    )}
                </label>
            )}

            {value === 'generate' && (
                <div className="rounded-xl border border-purple-500/40 bg-purple-500/10 px-4 py-3 text-sm text-purple-100">
                    Nous générerons votre logo plus tard automatiquement (LogoAgent). Aucun blocage à l’onboarding.
                </div>
            )}

            {value === 'later' && (
                <div className="rounded-xl border border-gray-700 bg-gray-900/60 px-4 py-3 text-sm text-gray-300">
                    Pas de souci, vous pourrez ajouter ou générer un logo plus tard.
                </div>
            )}
        </div>
    );
}
