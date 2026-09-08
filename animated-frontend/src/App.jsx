import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Search, Menu, Trophy, Activity, CheckCircle2, AlertCircle, X, ShieldAlert, Zap, Clock, ShieldCheck } from 'lucide-react';

const API_URL = 'http://localhost:8000/v1/decisions';

export default function App() {
  const [telemetry, setTelemetry] = useState({
    sessionAge: 0.0, backtracks: 0, dwellTime: 0.0,
    selectionChanges: 0, stakeChanges: 0, oddsChanged: false,
    slipAge: 0.0, attempts: 0, velocity: 0.0
  });
  
  const [sessionInfo] = useState(() => crypto.randomUUID());
  const [betslipOpen, setBetslipOpen] = useState(false);
  const [selectedOdd, setSelectedOdd] = useState(null);
  const [oddsValue, setOddsValue] = useState('1,45');
  const [oddsFlashing, setOddsFlashing] = useState(false);
  
  const [judgeState, setJudgeState] = useState({
    selfExcluded: false,
    limits: false,
    chasing: false,
    escalating: false,
    stale: false,
  });

  const [loading, setLoading] = useState(false);
  const [decision, setDecision] = useState(null);
  const [backendUp, setBackendUp] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/docs').then(r => setBackendUp(r.ok)).catch(() => setBackendUp(false));

    const interval = setInterval(() => {
      setTelemetry(prev => {
        let v = prev.velocity > 0 ? prev.velocity * 0.95 : 0;
        let d = betslipOpen ? prev.dwellTime + 0.1 : prev.dwellTime;
        let s = betslipOpen ? prev.slipAge + 0.1 : prev.slipAge;
        return { ...prev, sessionAge: prev.sessionAge + 0.1, velocity: v, dwellTime: d, slipAge: s };
      });
    }, 100);
    return () => clearInterval(interval);
  }, [betslipOpen]);

  const toggleSelection = (id, val) => {
    setTelemetry(p => ({ ...p, selectionChanges: p.selectionChanges + 1, velocity: p.velocity + 2.0 }));
    if (selectedOdd === id) {
      setSelectedOdd(null);
      setBetslipOpen(false);
      setTelemetry(p => ({ ...p, backtracks: p.backtracks + 1 }));
    } else {
      setSelectedOdd(id);
      setOddsValue(val);
      setBetslipOpen(true);
    }
  };

  const closeBetslip = () => {
    setBetslipOpen(false);
    setSelectedOdd(null);
    setTelemetry(p => ({ ...p, backtracks: p.backtracks + 1 }));
  };

  const triggerOddsChange = () => {
    setTelemetry(p => ({ ...p, oddsChanged: true }));
    setOddsValue('1,20');
    setOddsFlashing(true);
    setTimeout(() => setOddsFlashing(false), 1000);
  };

  const simulateHesitation = () => {
    setTelemetry(p => ({ ...p, dwellTime: p.dwellTime + 20.0, slipAge: p.slipAge + 20.0 }));
  };

  const resetSession = () => {
    setTelemetry({
      sessionAge: 0.0, backtracks: 0, dwellTime: 0.0,
      selectionChanges: 0, stakeChanges: 0, oddsChanged: false,
      slipAge: 0.0, attempts: 0, velocity: 0.0
    });
    setDecision(null);
    setOddsValue('1,45');
    setBetslipOpen(false);
    setSelectedOdd(null);
  };

  const evaluateDecision = async () => {
    setTelemetry(p => ({ ...p, attempts: p.attempts + 1, velocity: p.velocity + 5.0 }));
    setLoading(true);
    
    let actorId = 'actor-normal';
    if (judgeState.selfExcluded) actorId = 'actor-self-excluded';
    else if (judgeState.chasing || judgeState.escalating) actorId = 'actor-harm';
    else if (judgeState.stale) actorId = 'actor-safety-down';

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer demo-token' },
        body: JSON.stringify({
          session_id: sessionInfo,
          anonymous_actor_id: actorId,
          client_version: "1.0.0-react",
          slip_id: "slip-normal",
          interaction: {
            selection_changes: telemetry.selectionChanges,
            stake_changes: telemetry.stakeChanges,
            odds_changed: telemetry.oddsChanged,
            time_since_slip_creation_seconds: telemetry.slipAge,
            confirmation_attempts: telemetry.attempts + 1,
            interaction_velocity: telemetry.velocity,
            recent_backtracks: telemetry.backtracks,
            dwell_time_seconds: telemetry.dwellTime
          }
        })
      });
      const data = await res.json();
      setDecision(data);
    } catch (e) {
      setDecision({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-screen w-full bg-[#111318] text-slate-300 font-sans overflow-hidden">
      
      {/* LEFT: PSK Mobile App Simulator */}
      <div className="w-full md:w-[420px] h-full flex flex-col bg-[#f1f3f6] relative shadow-[0_0_50px_rgba(0,0,0,0.5)] z-10 shrink-0">
        
        {/* Header */}
        <div className="bg-[#0f2c59] text-white pt-5 pb-0 px-4 shrink-0 shadow-md z-10">
          <div className="flex justify-between items-center mb-5">
            <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.5)]"></span> PSK
            </div>
            <div className="flex items-center gap-3">
              <div className="bg-white/10 px-3 py-1.5 rounded-full text-sm font-bold text-emerald-400">250,00 €</div>
              <button className="bg-white/10 p-2 rounded-full hover:bg-white/20 transition"><Search size={16} /></button>
              <button className="bg-white/10 p-2 rounded-full hover:bg-white/20 transition"><Menu size={16} /></button>
            </div>
          </div>
          
          <div className="flex gap-6 overflow-x-auto text-sm font-semibold text-white/70 no-scrollbar border-b border-white/10">
            <div className="pb-3 text-white border-b-2 border-yellow-400 whitespace-nowrap cursor-pointer">Nogomet</div>
            <div className="pb-3 whitespace-nowrap cursor-pointer hover:text-white transition">Košarka</div>
            <div className="pb-3 whitespace-nowrap cursor-pointer hover:text-white transition">Tenis</div>
            <div className="pb-3 whitespace-nowrap cursor-pointer hover:text-white transition">Hokej</div>
            <div className="pb-3 whitespace-nowrap cursor-pointer hover:text-white transition">Rukomet</div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto pb-24 px-3 relative">
          
          {/* UZIVO */}
          <div className="flex justify-between items-center mt-5 mb-3 px-1">
            <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Uživo</h2>
            <span className="text-xs text-blue-700 font-bold hover:underline cursor-pointer">Sve ></span>
          </div>
          
          <div className="flex gap-3 overflow-x-auto no-scrollbar mb-6 px-1">
            {[ {min: "63'", lg: "SERIE A", home: "Napoli", away: "Roma", s1: 1, s2: 0},
               {min: "71'", lg: "LA LIGA", home: "Sevilla", away: "Betis", s1: 2, s2: 2}
             ].map((match, i) => (
              <motion.div whileHover={{ scale: 1.02 }} key={i} className="bg-white rounded-2xl p-4 min-w-[150px] shadow-sm shrink-0 border border-gray-100 cursor-pointer">
                <div className="text-[10px] font-bold text-orange-600 flex items-center gap-1.5 mb-3 tracking-wider">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-600 animate-pulse"></span> {match.min} - {match.lg}
                </div>
                <div className="text-sm font-semibold text-gray-800 leading-tight">{match.home}<br/>{match.away}</div>
                <div className="text-xl font-black text-[#0f2c59] mt-3">{match.s1} : {match.s2}</div>
              </motion.div>
            ))}
          </div>

          {/* NAJPOPULARNIJE */}
          <div className="flex justify-between items-center mb-3 px-1">
            <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Najpopularnije</h2>
            <span className="text-xs text-blue-700 font-bold hover:underline cursor-pointer">Sve lige ></span>
          </div>
          
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden mb-6 border border-gray-100">
            <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100 bg-gray-50/50">
              <div className="flex items-center gap-2 font-bold text-sm text-[#0f2c59]"><span>🇭🇷</span> SuperSport HNL</div>
              <div className="text-[11px] font-semibold text-gray-400">9. kolo</div>
            </div>
            
            {/* Match Rows */}
            {[ {d: "Sub", t: "18:00", h: "Dinamo Zagreb", a: "Slaven Belupo", o1: "1,45", ox: "4,20", o2: "6,50", id: 1},
               {d: "Sub", t: "20:15", h: "Hajduk Split", a: "Varaždin", o1: "1,75", ox: "3,60", o2: "4,40", id: 2},
               {d: "Ned", t: "15:00", h: "Rijeka", a: "Lokomotiva", o1: "1,90", ox: "3,50", o2: "3,90", id: 3}
             ].map((m) => (
              <div key={m.id} className="px-3 py-4 border-b border-gray-100 flex justify-between items-center hover:bg-blue-50/30 transition">
                <div className="flex flex-col w-12 text-center">
                  <span className="text-xs font-bold text-gray-400 uppercase">{m.d}</span>
                  <span className="text-xs font-bold text-gray-500">{m.t}</span>
                </div>
                <div className="flex-1 px-2">
                  <div className="text-sm font-bold text-[#0f2c59] leading-tight">{m.h}</div>
                  <div className="text-sm font-bold text-[#0f2c59] leading-tight mt-1">{m.a}</div>
                  <div className="text-[10px] font-semibold text-gray-400 mt-1.5">Osnovna ponuda</div>
                </div>
                <div className="flex gap-1.5">
                  <motion.button whileTap={{scale: 0.95}} onClick={() => toggleSelection(m.id+'-1', m.o1)} className={`rounded-lg p-2 flex flex-col items-center min-w-[48px] transition-colors ${selectedOdd === m.id+'-1' ? 'bg-yellow-300' : 'bg-gray-100 hover:bg-gray-200'}`}>
                    <span className="text-[10px] font-bold text-gray-500">1</span>
                    <span className="text-sm font-extrabold text-[#0f2c59]">{m.o1}</span>
                  </motion.button>
                  <motion.button whileTap={{scale: 0.95}} onClick={() => toggleSelection(m.id+'-x', m.ox)} className={`rounded-lg p-2 flex flex-col items-center min-w-[48px] transition-colors ${selectedOdd === m.id+'-x' ? 'bg-yellow-300' : 'bg-gray-100 hover:bg-gray-200'}`}>
                    <span className="text-[10px] font-bold text-gray-500">X</span>
                    <span className="text-sm font-extrabold text-[#0f2c59]">{m.ox}</span>
                  </motion.button>
                  <motion.button whileTap={{scale: 0.95}} onClick={() => toggleSelection(m.id+'-2', m.o2)} className={`rounded-lg p-2 flex flex-col items-center min-w-[48px] transition-colors ${selectedOdd === m.id+'-2' ? 'bg-yellow-300' : 'bg-gray-100 hover:bg-gray-200'}`}>
                    <span className="text-[10px] font-bold text-gray-500">2</span>
                    <span className="text-sm font-extrabold text-[#0f2c59]">{m.o2}</span>
                  </motion.button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* BETSLIP POPUP */}
        <AnimatePresence>
          {betslipOpen && (
            <motion.div 
              initial={{ y: "100%", opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: "100%", opacity: 0 }}
              transition={{ type: "spring", bounce: 0, duration: 0.4 }}
              className="absolute bottom-16 w-full bg-white rounded-t-3xl shadow-[0_-20px_40px_rgba(0,0,0,0.15)] border-t border-gray-200 p-5 z-20 flex flex-col"
            >
              <div className="flex justify-between items-center mb-5">
                <h3 className="font-black text-[#0f2c59] text-lg">Listić (1)</h3>
                <button className="text-gray-400 hover:text-gray-700 bg-gray-100 rounded-full p-1" onClick={closeBetslip}><X size={18} /></button>
              </div>
              
              <div className="bg-gray-50 rounded-xl p-4 mb-4 border border-gray-200 shadow-sm">
                <div className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Dinamo Zagreb - Slaven Belupo</div>
                <div className="flex justify-between items-center">
                  <span className="font-bold text-[#0f2c59]">1 (Osnovna ponuda)</span>
                  <motion.span 
                    animate={oddsFlashing ? { backgroundColor: '#fecaca', color: '#b91c1c', scale: 1.1 } : { backgroundColor: '#fef08a', color: '#0f2c59', scale: 1 }}
                    className="font-black px-2.5 py-1 rounded-md text-sm"
                  >
                    {oddsValue}
                  </motion.span>
                </div>
              </div>
              
              <div className="flex justify-between items-center mb-5">
                <span className="font-bold text-gray-500 text-sm">Uplata:</span>
                <input type="text" value="10,00 €" className="font-black text-right text-xl text-[#0f2c59] bg-transparent w-24 border-b-2 border-gray-300 focus:border-blue-500 outline-none" readOnly />
              </div>

              {/* Intervention Area */}
              <AnimatePresence>
                {decision && decision.action !== 'NO_INTERVENTION' && decision.response_text && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mb-5 overflow-hidden">
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-3.5 flex items-start gap-3 shadow-inner">
                      <ShieldAlert className="text-blue-500 shrink-0 mt-0.5" size={20} />
                      <div className="text-sm text-blue-900 font-bold leading-tight">{decision.response_text}</div>
                    </div>
                  </motion.div>
                )}
                {decision && decision.safety_status !== 'SAFE' && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mb-5 overflow-hidden">
                    <div className="bg-red-50 border border-red-200 rounded-xl p-3.5 flex items-start gap-3 shadow-inner">
                      <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
                      <div className="text-sm text-red-900 font-bold leading-tight">Action blocked by Safety Authority.<br/>Status: {decision.safety_status}</div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              
              <motion.button 
                whileTap={{ scale: 0.98 }} 
                onClick={evaluateDecision} 
                disabled={loading}
                className="w-full bg-[#0f2c59] hover:bg-blue-900 text-white font-black py-4 rounded-2xl shadow-lg flex justify-center items-center gap-2"
              >
                {loading ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div> : "UPLATI (10,00 €)"}
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bottom Nav */}
        <div className="absolute bottom-0 w-full bg-white border-t border-gray-200 flex justify-around items-center pt-3 pb-6 px-2 text-[10px] font-bold text-gray-400 z-30 shadow-[0_-5px_15px_rgba(0,0,0,0.05)]">
          <div className="flex flex-col items-center gap-1.5 hover:text-blue-800 cursor-pointer"><div className="p-1"><Menu size={20}/></div><span>Naslovna</span></div>
          <div className="flex flex-col items-center gap-1.5 hover:text-blue-800 cursor-pointer"><div className="p-1"><Activity size={20}/></div><span>Uživo</span></div>
          <div className="flex flex-col items-center gap-1.5 text-[#0f2c59] cursor-pointer"><div className="bg-blue-50 text-blue-800 p-1 rounded-lg"><Trophy size={20}/></div><span>Sport</span></div>
          <div className="flex flex-col items-center gap-1.5 hover:text-blue-800 cursor-pointer relative" onClick={() => setBetslipOpen(true)}>
            <div className="absolute top-0 right-0 bg-red-500 text-white text-[9px] w-4 h-4 flex items-center justify-center rounded-full font-bold shadow-sm">{betslipOpen ? '1' : '0'}</div>
            <div className="p-1"><CheckCircle2 size={20}/></div><span>Listići</span>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Judge Panel */}
      <div className="flex-1 bg-[#111318] text-slate-300 p-8 flex flex-col h-full overflow-y-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <Zap className="text-amber-400" /> Confidence Layer — kontrolna ploča
          </h1>
          <p className="text-sm text-slate-500 mt-1 font-medium">Shadcn / Animated Judge Panel · real-time inference</p>
        </div>
        
        {/* Status Banner */}
        <motion.div animate={{ opacity: backendUp ? 1 : 0.8 }} className={`px-4 py-3.5 rounded-xl mb-8 text-sm font-bold flex items-center gap-3 border shadow-sm ${backendUp ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border-amber-500/20'}`}>
          <span className={`w-2.5 h-2.5 rounded-full ${backendUp ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
          {backendUp ? 'Backend Connected — AI pipeline active' : 'Backend unreachable — embedded rules engine'}
        </motion.div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-10">
          
          <div className="space-y-10">
            {/* Player State */}
            <div>
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mb-5 flex items-center gap-2"><Settings size={14}/> Server-Side Truth</h3>
              <div className="space-y-1 bg-slate-900/50 p-3 rounded-2xl border border-slate-800">
                {Object.entries({
                  selfExcluded: "Self-excluded (register)",
                  limits: "Protective limits set",
                  chasing: "Harm marker · loss chasing",
                  escalating: "Harm marker · escalating stakes",
                  stale: "Safety data stale (>300s)"
                }).map(([key, label]) => (
                  <label key={key} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/80 cursor-pointer transition-colors">
                    <span className="text-sm font-semibold text-slate-300">{label}</span>
                    <div className="relative inline-block w-11 h-6 transition duration-200 ease-in-out">
                      <input type="checkbox" className="peer absolute opacity-0 w-0 h-0" checked={judgeState[key]} onChange={(e) => setJudgeState(p => ({...p, [key]: e.target.checked}))} />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer-checked:bg-blue-600 transition-colors"></div>
                      <div className="absolute left-[2px] top-[2px] bg-white border border-gray-300 rounded-full h-5 w-5 transition-transform peer-checked:translate-x-full"></div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Live Simulation */}
            <div>
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mb-5 flex items-center gap-2"><Activity size={14}/> Live Simulation</h3>
              <div className="space-y-3">
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={triggerOddsChange} className="w-full bg-white text-[#111318] font-bold py-3.5 px-4 rounded-xl text-sm shadow-lg">Move the odds on a selection</motion.button>
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={simulateHesitation} className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3.5 px-4 rounded-xl text-sm border border-slate-700 shadow-lg transition-colors">Simulate hesitation (dwell 20s)</motion.button>
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={resetSession} className="w-full bg-transparent hover:bg-red-500/10 text-red-400 font-bold py-3.5 px-4 rounded-xl text-sm border border-red-500/20 transition-colors">Reset session</motion.button>
              </div>
            </div>
          </div>

          <div className="space-y-10">
            {/* Telemetry */}
            <div>
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mb-5 flex items-center gap-2"><Clock size={14}/> Live Telemetry</h3>
              <div className="font-mono text-sm space-y-0.5 text-slate-400 bg-slate-900/50 p-5 rounded-2xl border border-slate-800">
                {Object.entries({
                  "session age seconds": telemetry.sessionAge.toFixed(3),
                  "recent backtracks": telemetry.backtracks,
                  "dwell time seconds": telemetry.dwellTime.toFixed(1),
                  "selection changes": telemetry.selectionChanges,
                  "stake changes": telemetry.stakeChanges,
                  "odds changed": telemetry.oddsChanged.toString(),
                  "time since slip creation seconds": telemetry.slipAge.toFixed(1),
                  "confirmation attempts": telemetry.attempts,
                  "interaction velocity": telemetry.velocity.toFixed(2)
                }).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-2 border-b border-slate-800/50 last:border-0">
                    <span>{k}</span>
                    <span className="text-white font-bold text-amber-400">{v}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pipeline */}
            <div>
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mb-5 flex items-center gap-2"><ShieldCheck size={14}/> Pipeline Execution</h3>
              
              <AnimatePresence mode="wait">
                {!decision ? (
                  <motion.div key="waiting" initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}} className="bg-slate-900/30 border border-slate-800 border-dashed rounded-2xl p-6 text-center text-slate-500 text-sm font-medium">
                    Waiting for UPLATI event...
                  </motion.div>
                ) : decision.error ? (
                  <motion.div key="error" initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}} className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-red-400 text-sm font-bold">
                    {decision.error}
                  </motion.div>
                ) : (
                  <motion.div key="success" initial="hidden" animate="show" variants={{
                    hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.15 } }
                  }} className="space-y-3 font-mono text-[12px]">
                    
                    {/* Step 1 */}
                    <motion.div variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }} className={`p-4 rounded-xl border-l-4 shadow-md ${decision.safety_status === 'SAFE' ? 'bg-slate-900 border-l-emerald-500' : 'bg-red-900/20 border-l-red-500'}`}>
                      <span className={`${decision.safety_status === 'SAFE' ? 'text-emerald-400' : 'text-red-400'} font-bold block mb-1`}>1. Safety Authority</span>
                      <span className="text-white font-bold text-sm">{decision.safety_status}</span>
                    </motion.div>

                    {/* Step 2 */}
                    <motion.div variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }} className="bg-slate-900 p-4 rounded-xl border-l-4 border-l-blue-500 shadow-md">
                      <span className="text-blue-400 font-bold block mb-1">2. State Authority</span>
                      {decision.safety_status === 'SAFE' ? (
                        <span className="text-white font-bold text-sm">{decision.state} <span className="text-slate-500 font-normal ml-2">(Conf: {decision.confidence?.toFixed(2)})</span></span>
                      ) : (
                        <span className="text-slate-500 italic">SKIPPED (Blocked by Safety Gate)</span>
                      )}
                    </motion.div>

                    {/* Step 3 */}
                    <motion.div variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }} className="bg-slate-900 p-4 rounded-xl border-l-4 border-l-purple-500 shadow-md">
                      <span className="text-purple-400 font-bold block mb-1">3. Policy Selector</span>
                      {decision.safety_status === 'SAFE' ? (
                        <div>
                          <span className="text-white font-bold text-sm bg-purple-500/20 px-2 py-0.5 rounded">{decision.action}</span>
                          <span className="text-slate-500 block mt-2 whitespace-nowrap overflow-hidden text-ellipsis">{decision.reason}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">SKIPPED (Blocked by Safety Gate)</span>
                      )}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
