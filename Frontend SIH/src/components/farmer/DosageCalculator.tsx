import React, { useState } from 'react';
import { Calculator, Clock, ShieldAlert } from 'lucide-react';
import { PesticideRecommendation } from '../../types';

interface DosageCalculatorProps {
  pesticide: PesticideRecommendation;
  cropName: string;
}

export const DosageCalculator: React.FC<DosageCalculatorProps> = ({
  pesticide,
  cropName
}) => {
  const [tankVolume, setTankVolume] = useState<number>(15);
  const [customLitres, setCustomLitres] = useState<string>('15');

  const doseMissing =
    !pesticide.exact_dose_per_liter ||
    pesticide.exact_dose_per_liter.trim() === '' ||
    pesticide.guidance_available === false;

  const doseString = pesticide.exact_dose_per_liter?.trim() || '';
  const numMatch = doseString.match(/([0-9.]+)/);
  const unitMatch = doseString.toLowerCase().includes('ml') ? 'ml' : 'g';
  const unitDose = numMatch ? parseFloat(numMatch[1]) : NaN;
  const canCalculate = !doseMissing && !Number.isNaN(unitDose) && unitDose > 0;
  const totalRequirement = canCalculate ? (unitDose * tankVolume).toFixed(1) : null;

  const handleVolumeSelect = (vol: number) => {
    setTankVolume(vol);
    setCustomLitres(vol.toString());
  };

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setCustomLitres(val);
    const parsed = parseFloat(val);
    if (!isNaN(parsed) && parsed > 0) {
      setTankVolume(parsed);
    }
  };

  if (doseMissing) {
    return (
      <div className="bg-white rounded-2xl p-5 border border-amber-300 shadow-sm space-y-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-50 text-amber-700 border border-amber-200">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-900 font-['Outfit']">
              Knapsack & Drum Dosage Calculator
            </h4>
            <p className="text-[11px] text-slate-600 font-medium">
              {pesticide.chemical_name || 'Chemical guidance'}
            </p>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-center space-y-1">
          <p className="text-sm font-bold text-amber-900">Verified dosage unavailable</p>
          <p className="text-xs text-amber-800">
            {pesticide.unavailable_reason ||
              'No verified per-litre dose is available for this recommendation. Do not apply an estimated default.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-900 font-['Outfit']">
              Knapsack & Drum Dosage Calculator
            </h4>
            <p className="text-[11px] text-slate-600 font-medium">
              Calibrated for {pesticide.chemical_name} ({pesticide.active_ingredient})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-300 text-xs font-bold text-amber-900">
          <Clock className="w-3.5 h-3.5 text-amber-700" />
          <span>{pesticide.withholding_period_days} Days PHI</span>
        </div>
      </div>

      <div>
        <p className="text-xs text-slate-700 mb-2 font-bold">Select Sprayer Equipment Capacity:</p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { label: '15 L Knapsack', vol: 15, sub: 'Backpack manual' },
            { label: '50 L Power', vol: 50, sub: 'Motorized sprayer' },
            { label: '200 L Drum', vol: 200, sub: 'Tractor mounted' }
          ].map((item) => (
            <button
              key={item.vol}
              onClick={() => handleVolumeSelect(item.vol)}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                tankVolume === item.vol
                  ? 'bg-emerald-700 border-emerald-700 text-white shadow-sm'
                  : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'
              }`}
            >
              <p className={`text-xs font-bold ${tankVolume === item.vol ? 'text-white' : 'text-slate-900'}`}>{item.label}</p>
              <p className={`text-[10px] ${tankVolume === item.vol ? 'text-emerald-100' : 'text-slate-500'}`}>{item.sub}</p>
            </button>
          ))}
        </div>
        <div className="mt-2">
          <label className="text-[11px] font-semibold text-slate-700">Custom litres</label>
          <input
            type="number"
            min={1}
            value={customLitres}
            onChange={handleCustomChange}
            className="mt-1 w-full bg-slate-50 border border-slate-300 text-xs text-slate-900 font-bold rounded-lg p-2 focus:outline-none focus:border-emerald-600"
          />
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-white shadow-md flex items-center justify-between">
        <div>
          <span className="text-[11px] text-emerald-400 uppercase tracking-wider font-bold">
            Exact Measure Required
          </span>
          <div className="flex items-baseline gap-1.5 mt-0.5">
            <span className="text-3xl font-extrabold text-white font-['Outfit']">
              {totalRequirement}
            </span>
            <span className="text-sm font-bold text-emerald-400">{unitMatch}</span>
            <span className="text-xs text-slate-300 font-medium">in {tankVolume} Litres water</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] text-slate-400 font-medium">Base Formulation</span>
          <p className="text-xs font-mono font-bold text-white mt-0.5">{doseString}</p>
        </div>
      </div>

      <div className="text-[11px] text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 flex items-start gap-2 leading-relaxed">
        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <span>
          <strong className="text-slate-900">Pre-Harvest Interval (PHI):</strong> Do not harvest {cropName} within{' '}
          {pesticide.withholding_period_days} days after application. Ensure spray drift does not
          enter water bodies or livestock pastures.
        </span>
      </div>
    </div>
  );
};
