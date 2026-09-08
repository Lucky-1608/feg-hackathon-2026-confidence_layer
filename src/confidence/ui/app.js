// State
let telemetry = {
    sessionAge: 0.0,
    backtracks: 0,
    dwellTime: 0.0,
    selectionChanges: 0,
    stakeChanges: 0,
    oddsChanged: false,
    slipAge: 0.0,
    attempts: 0,
    velocity: 0.0
};
const sessionId = crypto.randomUUID();

// Check Backend Connection
fetch('/docs')
    .then(r => {
        if(r.ok) {
            const banner = document.getElementById('connection-status');
            banner.className = 'bg-emerald-100 text-emerald-800 px-4 py-3 rounded-lg mb-8 text-sm font-semibold flex items-center gap-2 border border-emerald-200 shadow-sm';
            banner.innerHTML = '<span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span> Backend Connected — AI pipeline active';
        }
    }).catch(e => { console.warn("Backend unreachable."); });

// Timer
setInterval(() => {
    telemetry.sessionAge += 0.1;
    // Decay velocity
    if (telemetry.velocity > 0) telemetry.velocity *= 0.95;
    
    if (document.getElementById('betslip-popup').classList.contains('hidden') === false) {
        telemetry.dwellTime += 0.1;
        telemetry.slipAge += 0.1;
    }
    updateTelemetryUI();
}, 100);

function updateTelemetryUI() {
    document.getElementById('val-session-age').textContent = telemetry.sessionAge.toFixed(3);
    document.getElementById('val-dwell').textContent = telemetry.dwellTime.toFixed(1);
    document.getElementById('val-slip-age').textContent = telemetry.slipAge.toFixed(1);
    document.getElementById('val-backtracks').textContent = telemetry.backtracks;
    document.getElementById('val-sel-changes').textContent = telemetry.selectionChanges;
    document.getElementById('val-stake-changes').textContent = telemetry.stakeChanges;
    document.getElementById('val-odds-changed').textContent = telemetry.oddsChanged;
    document.getElementById('val-attempts').textContent = telemetry.attempts;
    document.getElementById('val-velocity').textContent = telemetry.velocity.toFixed(1);
}

// UI Controls
function toggleSelection(btn) {
    telemetry.selectionChanges += 1;
    telemetry.velocity += 2.0;
    updateTelemetryUI();
    
    const isSelected = btn.classList.contains('bg-yellow-300');
    if (isSelected) {
        btn.classList.remove('bg-yellow-300');
        btn.classList.add('bg-gray-100');
    } else {
        btn.classList.add('bg-yellow-300');
        btn.classList.remove('bg-gray-100');
        openBetslip();
    }
}

function openBetslip() {
    document.getElementById('betslip-popup').classList.remove('hidden');
    document.getElementById('slip-badge').textContent = '1';
}

function closeBetslip() {
    document.getElementById('betslip-popup').classList.add('hidden');
    document.getElementById('slip-badge').textContent = '0';
    telemetry.backtracks += 1;
    updateTelemetryUI();
}

function triggerOddsChange() {
    telemetry.oddsChanged = true;
    updateTelemetryUI();
    const slipOdds = document.getElementById('slip-odds');
    slipOdds.textContent = '1,20'; // changed from 1,45
    slipOdds.classList.add('bg-red-200', 'text-red-700');
    setTimeout(() => { slipOdds.classList.remove('bg-red-200', 'text-red-700'); }, 1000);
}

function simulateHesitation() {
    telemetry.dwellTime += 20.0;
    telemetry.slipAge += 20.0;
    updateTelemetryUI();
}

function resetTelemetry() {
    telemetry = {
        sessionAge: 0.0,
        backtracks: 0,
        dwellTime: 0.0,
        selectionChanges: 0,
        stakeChanges: 0,
        oddsChanged: false,
        slipAge: 0.0,
        attempts: 0,
        velocity: 0.0
    };
    updateTelemetryUI();
    document.getElementById('intervention-container').classList.add('hidden');
    document.getElementById('pipeline-visualization').classList.add('hidden');
    document.getElementById('last-decision-status').innerHTML = '<span class="text-slate-500">— no decision yet</span>';
    const slipOdds = document.getElementById('slip-odds');
    slipOdds.textContent = '1,45';
}

// Dummy mapping function (normally this would be real server state, but we mock it here for the demo)
function updateSafetyState() {
    // Triggers automatically via element change events in HTML
    document.getElementById('pipeline-visualization').classList.add('hidden');
}

async function evaluateDecision() {
    telemetry.attempts += 1;
    telemetry.velocity += 5.0;
    
    // Determine mock IDs based on toggles
    let actorId = "actor-normal";
    if (document.getElementById('toggle-self-excluded').checked) actorId = "actor-self-excluded";
    else if (document.getElementById('toggle-chasing').checked) actorId = "actor-harm";
    else if (document.getElementById('toggle-stale').checked) actorId = "actor-safety-down";
    else if (document.getElementById('toggle-escalating').checked) actorId = "actor-harm";
    
    let slipId = "slip-normal";
    
    const payload = {
        session_id: sessionId,
        anonymous_actor_id: actorId,
        client_version: "1.0.0-web",
        slip_id: slipId,
        interaction: {
            selection_changes: telemetry.selectionChanges,
            stake_changes: telemetry.stakeChanges,
            odds_changed: telemetry.oddsChanged,
            time_since_slip_creation_seconds: telemetry.slipAge,
            confirmation_attempts: telemetry.attempts,
            interaction_velocity: telemetry.velocity,
            recent_backtracks: telemetry.backtracks,
            dwell_time_seconds: telemetry.dwellTime
        }
    };
    
    // UI Loading state
    document.getElementById('btn-confirm-text').classList.add('opacity-50');
    document.getElementById('btn-spinner').classList.remove('hidden');
    document.getElementById('intervention-container').classList.add('hidden');
    
    try {
        const response = await fetch('/v1/decisions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer demo-token' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        // Show Intervention on Betslip if any
        if (data.action !== 'NO_INTERVENTION' && data.response_text) {
            const container = document.getElementById('intervention-container');
            container.innerHTML = `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-3">
                    <div class="text-blue-500 mt-0.5">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <div class="text-sm text-blue-900 font-semibold">${data.response_text}</div>
                </div>
            `;
            container.classList.remove('hidden');
        } else if (data.safety_status !== 'SAFE') {
            const container = document.getElementById('intervention-container');
            container.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-3">
                    <div class="text-red-500 mt-0.5">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    </div>
                    <div class="text-sm text-red-900 font-semibold">Action blocked by Safety Authority. Code: ${data.safety_status}</div>
                </div>
            `;
            container.classList.remove('hidden');
        }

        // Update Judge Panel
        document.getElementById('last-decision-status').innerHTML = `<span class="text-white font-bold bg-blue-900/50 px-2 py-1 rounded">${data.action}</span>`;
        
        // Update Pipeline View
        document.getElementById('pipeline-visualization').classList.remove('hidden');
        document.getElementById('pipe-safety-res').textContent = data.safety_status;
        
        if (data.safety_status === 'SAFE') {
            document.getElementById('pipe-safety-res').className = 'text-emerald-400';
            document.getElementById('pipe-state-res').textContent = `${data.state} (Conf: ${data.confidence ? data.confidence.toFixed(2) : 'N/A'})`;
            document.getElementById('pipe-policy-res').textContent = `${data.action} - ${data.reason}`;
        } else {
            document.getElementById('pipe-safety-res').className = 'text-red-400 font-bold';
            document.getElementById('pipe-state-res').textContent = `SKIPPED (Blocked by Safety Gate)`;
            document.getElementById('pipe-policy-res').textContent = `SKIPPED (Blocked by Safety Gate)`;
        }
        
    } catch (e) {
        console.error(e);
        document.getElementById('last-decision-status').innerHTML = `<span class="text-red-500 font-bold">Error connecting to API</span>`;
    } finally {
        document.getElementById('btn-confirm-text').classList.remove('opacity-50');
        document.getElementById('btn-spinner').classList.add('hidden');
    }
}
