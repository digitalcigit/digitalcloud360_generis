'use client';

import React from 'react';
import { BriefResponse } from '@/types/dashboard';
import { FileText, MapPin, Target, Lightbulb, Compass, Flag, Edit3 } from 'lucide-react';

interface BusinessBriefViewerProps {
    brief: BriefResponse;
    onEdit?: () => void;
}

export default function BusinessBriefViewer({ brief, onEdit }: BusinessBriefViewerProps) {
    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <FileText className="text-[#2B4C7E]" size={20} />
                    <h3 className="font-semibold text-gray-900">Business Brief</h3>
                </div>
                {onEdit && (
                    <button
                        onClick={onEdit}
                        className="text-gray-400 hover:text-[#2B4C7E] p-1 rounded hover:bg-gray-50 transition-colors"
                        title="Modifier le brief"
                    >
                        <Edit3 size={18} />
                    </button>
                )}
            </div>

            <div className="p-6 grid grid-cols-1 gap-8">
                {/* Vision & Mission */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <div className="flex items-center gap-2 mb-2 text-gray-800 font-medium">
                            <Compass size={18} className="text-blue-600" />
                            Vision
                        </div>
                        <p className="text-gray-600 text-sm leading-relaxed p-3 bg-gray-50 rounded-lg border border-gray-100">
                            {brief.vision}
                        </p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-2 text-gray-800 font-medium">
                            <Flag size={18} className="text-blue-600" />
                            Mission
                        </div>
                        <p className="text-gray-600 text-sm leading-relaxed p-3 bg-gray-50 rounded-lg border border-gray-100">
                            {brief.mission}
                        </p>
                    </div>
                </div>

                <div className="border-t border-gray-100 my-2"></div>

                {/* Core Strategy */}
                <div className="space-y-6">
                    <div>
                        <div className="flex items-center gap-2 mb-2 text-gray-800 font-medium">
                            <Target size={18} className="text-indigo-600" />
                            Cible (Target Audience)
                        </div>
                        <p className="text-gray-600 text-sm leading-relaxed">
                            {brief.target_audience}
                        </p>
                    </div>

                    <div>
                        <div className="flex items-center gap-2 mb-2 text-gray-800 font-medium">
                            <Lightbulb size={18} className="text-amber-600" />
                            Proposition de Valeur
                        </div>
                        <p className="text-gray-600 text-sm leading-relaxed">
                            {brief.value_proposition}
                        </p>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Différenciation</h4>
                        <p className="text-gray-600 text-sm leading-relaxed">
                            {brief.differentiation}
                        </p>
                    </div>
                </div>

                {/* Meta Info */}
                <div className="flex flex-wrap gap-4 pt-4 border-t border-gray-100 text-xs text-gray-500">
                    <div className="flex items-center gap-1 bg-gray-100 px-2 py-1 rounded">
                        <MapPin size={14} />
                        {brief.location?.city}, {brief.location?.country}
                    </div>
                    <div className="px-2 py-1 rounded bg-gray-100">
                        Secteur: <span className="font-medium text-gray-700">{brief.sector}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
