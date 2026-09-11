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
      <div className="glass-card rounded-2xl p-5 border border-amber-500/30 shadow-xl space-y-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-white font-['Outfit']">
              Knapsack & Drum Dosage Calculator
            </h4>
            <p className="text-[11px] text-slate-400">
              {pesticide.chemical_name || 'Chemical guidance'}
            </p>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-center space-y-1">
          <p className="text-sm font-bold text-amber-200">Verified dosage unavailable</p>
          <p className="text-xs text-slate-400">
            {pesticide.unavailable_reason ||
              'No verified per-litre dose is available for this recommendation. Do not apply an estimated default.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-5 border border-emerald-500/20 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-white font-['Outfit']">
              Knapsack & Drum Dosage Calculator
            </h4>
            <p className="text-[11px] text-slate-400">
              Calibrated for {pesticide.chemical_name} ({pesticide.active_ingredient})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-950/60 border border-amber-500/30 text-xs font-semibold text-amber-300">
          <Clock className="w-3.5 h-3.5" />
          <span>{pesticide.withholding_period_days} Days PHI</span>
        </div>
      </div>

      <div>
        <p className="text-xs text-slate-400 mb-2 font-medium">Select Sprayer Equipment Capacity:</p>
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
                  ? 'bg-emerald-500/20 border-emerald-500 text-white shadow-lg shadow-emerald-500/10'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <p className="text-xs font-bold">{item.label}</p>
              <p className="text-[10px] text-slate-400">{item.sub}</p>
            </button>
          ))}
        </div>
        <div className="mt-2">
          <label className="text-[10px] text-slate-500">Custom litres</label>
          <input
            type="number"
            min={1}
            value={customLitres}
            onChange={handleCustomChange}
            className="mt-1 w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg p-2 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/60 to-slate-900 border border-emerald-500/30 flex items-center justify-between">
        <div>
          <span className="text-[11px] text-emerald-400 uppercase tracking-wider font-semibold">
            Exact Measure Required
          </span>
          <div className="flex items-baseline gap-1.5 mt-0.5">
            <span className="text-3xl font-extrabold text-white font-['Outfit']">
              {totalRequirement}
            </span>
            <span className="text-sm font-bold text-emerald-400">{unitMatch}</span>
            <span className="text-xs text-slate-400">in {tankVolume} Litres water</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] text-slate-400">Base Formulation</span>
          <p className="text-xs font-mono font-bold text-slate-200">{doseString}</p>
        </div>
      </div>

      <div className="text-[11px] text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-800 flex items-start gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <span>
          <strong>Pre-Harvest Interval (PHI):</strong> Do not harvest {cropName} within{' '}
          {pesticide.withholding_period_days} days after application. Ensure spray drift does not
          enter water bodies or livestock pastures.
        </span>
      </div>
    </div>
  );
};
