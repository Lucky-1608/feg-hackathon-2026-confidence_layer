// State for Client Telemetry
let telemetry = {
    dwell_time_seconds: 0.0,
    backtracks: 0,
    stake_changes: 0,
    odds_changed: false
};

// Generate a random session ID
const sessionId = crypto.randomUUID();
document.getElementById('header-session-id').textContent = sessionId.substring(0, 8) + '...';

// Timer for dwell time
let dwellTimer = setInterval(() => {
    telemetry.dwell_time_seconds += 0.5;
    document.getElementById('dwell-display').textContent = telemetry.dwell_time_seconds.toFixed(1) + 's';
}, 500);

// UI Actions
function markInteracted() {
    telemetry.stake_changes += 1;
    document.getElementById('stake-changes-display').textContent = telemetry.stake_changes;
}

function triggerOddsChange() {
    telemetry.odds_changed = true;
    document.getElementById('odds-changed-display').textContent = 'True';
    document.getElementById('old-odds-display').classList.remove('hidden');
    document.getElementById('current-odds-display').textContent = '2.50';
    document.getElementById('old-odds-display').textContent = '2.30';
    
    // Animate odds change
    const el = document.getElementById('current-odds-display');
    el.classList.add('text-red-500');
    setTimeout(() => el.classList.remove('text-red-500'), 1000);
}

function triggerBacktrack() {
    telemetry.backtracks += 1;
    document.getElementById('backtracks-display').textContent = telemetry.backtracks;
}

function resetTelemetry() {
    telemetry = {
        dwell_time_seconds: 0.0,
        backtracks: 0,
        stake_changes: 0,
        odds_changed: false
    };
    document.getElementById('dwell-display').textContent = '0.0s';
    document.getElementById('backtracks-display').textContent = '0';
    document.getElementById('stake-changes-display').textContent = '0';
    document.getElementById('odds-changed-display').textContent = 'False';
    document.getElementById('old-odds-display').classList.add('hidden');
    
    // Hide intervention
    document.getElementById('intervention-overlay').classList.add('hidden');
    
    // Reset Pipeline Visuals
    ['pipe-safety', 'pipe-state', 'pipe-policy'].forEach(id => {
        const el = document.getElementById(id);
        el.className = 'bg-slate-800 p-4 rounded border border-slate-700 transition-all opacity-50';
    });
    document.getElementById('res-safety-status').textContent = '-';
    document.getElementById('res-state').textContent = '-';
    document.getElementById('res-confidence').textContent = '-';
    document.getElementById('res-action').textContent = '-';
    document.getElementById('res-reason').textContent = '-';
    document.getElementById('audit-json').textContent = 'Awaiting decision...';
}

// Evaluate Decision against FastAPI backend
async function evaluateDecision() {
    const loading = document.getElementById('loading-overlay');
    loading.classList.remove('hidden');
    
    // Hide previous intervention
    document.getElementById('intervention-overlay').classList.add('hidden');
    
    // Gather state
    const actorId = document.getElementById('actor-override').value;
    const slipId = document.getElementById('slip-override').value;
    
    const payload = {
        session_id: sessionId,
        anonymous_actor_id: actorId,
        client_version: "1.0.0-web",
        slip_id: slipId,
        interaction: {
            selection_changes: telemetry.backtracks, // map backtracks to selection_changes for the API
            stake_changes: telemetry.stake_changes,
            odds_changed: telemetry.odds_changed,
            time_since_slip_creation_seconds: telemetry.dwell_time_seconds,
            confirmation_attempts: 0,
            interaction_velocity: 0.0,
            recent_backtracks: telemetry.backtracks,
            dwell_time_seconds: telemetry.dwell_time_seconds
        }
    };
    
    try {
        const response = await fetch('/v1/decisions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer demo-token' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        // Show Audit
        document.getElementById('audit-json').textContent = JSON.stringify(data, null, 2);
        
        // Update Pipeline UI
        updatePipeline(data);
        
        // Show Intervention if applicable
        if (data.action !== 'NO_INTERVENTION' && data.response_text) {
            document.getElementById('intervention-text').textContent = data.response_text;
            document.getElementById('intervention-overlay').classList.remove('hidden');
        }
        
    } catch (e) {
        document.getElementById('audit-json').textContent = 'Error: ' + e.message;
    } finally {
        loading.classList.add('hidden');
    }
}

function updatePipeline(data) {
    // 1. Safety
    const pipeSafety = document.getElementById('pipe-safety');
    const resSafety = document.getElementById('res-safety-status');
    pipeSafety.classList.remove('opacity-50');
    if (data.safety_status === 'SAFE') {
        pipeSafety.classList.add('border-green-500', 'glow-safe');
        resSafety.textContent = 'SAFE';
        resSafety.className = 'text-sm font-bold text-green-400';
    } else {
        pipeSafety.classList.add('border-red-500', 'glow-blocked');
        resSafety.textContent = data.safety_status || 'BLOCKED';
        resSafety.className = 'text-sm font-bold text-red-400';
    }
    
    // 2. State
    const pipeState = document.getElementById('pipe-state');
    pipeState.classList.remove('opacity-50');
    pipeState.classList.add('border-blue-500');
    document.getElementById('res-state').textContent = data.state;
    document.getElementById('res-confidence').textContent = data.confidence ? data.confidence.toFixed(2) : 'N/A';
    
    // 3. Policy
    const pipePolicy = document.getElementById('pipe-policy');
    const resAction = document.getElementById('res-action');
    pipePolicy.classList.remove('opacity-50');
    
    resAction.textContent = data.action;
    document.getElementById('res-reason').textContent = data.reason || 'Pipeline complete';
    
    if (data.action === 'NO_INTERVENTION') {
        pipePolicy.classList.add('border-slate-500');
        resAction.className = 'text-sm font-bold text-slate-300';
    } else {
        pipePolicy.classList.add('border-blue-500', 'glow-action');
        resAction.className = 'text-sm font-bold text-blue-400';
    }
}

// Attach place bet listener
document.getElementById('btn-place-bet').addEventListener('click', () => {
    evaluateDecision();
});
