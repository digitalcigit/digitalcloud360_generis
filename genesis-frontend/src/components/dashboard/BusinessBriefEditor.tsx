'use client';

import React, { useState } from 'react';
import { BriefResponse, BriefUpdateRequest } from '@/types/dashboard';
import { Save, X, Edit3, Compass, Flag, Target, Lightbulb, Info } from 'lucide-react';

interface BusinessBriefEditorProps {
    brief: BriefResponse;
    onSave: (updates: BriefUpdateRequest) => Promise<void>;
    onCancel: () => void;
}

export default function BusinessBriefEditor({ brief, onSave, onCancel }: BusinessBriefEditorProps) {
    const [formData, setFormData] = useState<BriefUpdateRequest>({
        business_name: brief.business_name,
        vision: brief.vision,
        mission: brief.mission,
        target_audience: brief.target_audience,
        differentiation: brief.differentiation,
        value_proposition: brief.value_proposition,
    });

    const [isSaving, setIsSaving] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            await onSave(formData);
        } catch (err) {
            console.error(err);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border-2 border-blue-100 shadow-md overflow-hidden">
            <div className="bg-blue-50 px-6 py-4 flex items-center justify-between border-b border-blue-100">
                <div className="flex items-center gap-2 text-[#2B4C7E]">
                    <Edit3 size={20} />
                    <h3 className="font-semibold">Modifier le Brief</h3>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-white rounded-lg transition-colors"
                        disabled={isSaving}
                    >
                        <X size={20} />
                    </button>
                    <button
                        type="submit"
                        disabled={isSaving}
                        className="flex items-center gap-2 px-4 py-2 bg-[#2B4C7E] text-white rounded-lg hover:bg-[#1A365D] transition-colors disabled:opacity-50"
                    >
                        <Save size={18} />
                        {isSaving ? 'Enregistrement...' : 'Enregistrer'}
                    </button>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {/* Business Name */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nom de l'entreprise</label>
                    <input
                        type="text"
                        name="business_name"
                        value={formData.business_name}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                        placeholder="Ex: My Awesome Startup"
                    />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Vision */}
                    <div>
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                            <Compass size={16} className="text-blue-600" />
                            Vision
                        </label>
                        <textarea
                            name="vision"
                            value={formData.vision}
                            onChange={handleChange}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none text-sm"
                        />
                    </div>
                    {/* Mission */}
                    <div>
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                            <Flag size={16} className="text-blue-600" />
                            Mission
                        </label>
                        <textarea
                            name="mission"
                            value={formData.mission}
                            onChange={handleChange}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none text-sm"
                        />
                    </div>
                </div>

                {/* Target Audience */}
                <div>
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                        <Target size={16} className="text-indigo-600" />
                        Cible (Target Audience)
                    </label>
                    <textarea
                        name="target_audience"
                        value={formData.target_audience}
                        onChange={handleChange}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none text-sm"
                    />
                </div>

                {/* Value Proposition */}
                <div>
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                        <Lightbulb size={16} className="text-amber-600" />
                        Proposition de Valeur
                    </label>
                    <textarea
                        name="value_proposition"
                        value={formData.value_proposition}
                        onChange={handleChange}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none text-sm"
                    />
                </div>

                {/* Differentiation */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Différenciation</label>
                    <textarea
                        name="differentiation"
                        value={formData.differentiation}
                        onChange={handleChange}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none text-sm"
                    />
                </div>

                <div className="flex items-start gap-2 p-3 bg-amber-50 rounded-lg border border-amber-100">
                    <Info size={18} className="text-amber-600 shrink-0 mt-0.5" />
                    <p className="text-xs text-amber-800">
                        <strong>Note :</strong> Les modifications apportées ici m'aideront à regénérer un site plus précis.
                        Vous devrez cliquer sur "Régénérer le site" pour voir les changements sur l'aperçu.
                    </p>
                </div>
            </div>
        </form>
    );
}
