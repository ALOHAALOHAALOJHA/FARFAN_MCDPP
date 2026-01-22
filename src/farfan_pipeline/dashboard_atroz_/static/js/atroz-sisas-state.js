/**
 * AtroZ SISAS State Management Extension
 * ==========================================
 *
 * Extends DashboardStateManager with SISAS-specific state tracking:
 * - Real-time signal metrics
 * - Consumer status tracking
 * - Gate validation statistics
 * - Signal extraction progress
 * - Evidence stream management
 * - Job progress with SISAS data
 *
 * @version 2.0.0
 * @requires atroz-dashboard-integration.js
 */

// ============================================================================
// ENHANCED STATE MANAGER WITH SISAS
// ============================================================================

class SISASEnhancedStateManager extends DashboardStateManager {
    constructor() {
        super();

        // Extend base state with SISAS-specific state
        this.state = {
            ...this.state,

            // SISAS Integration State
            sisas: {
                enabled: false,
                status: 'OFFLINE',  // ONLINE | DEGRADED | OFFLINE
                lastUpdate: null,

                // Consumer tracking
                consumers: {
                    total: 17,
                    active: 0,
                    byPhase: {},  // {P00: [...], P01: [...], ...}
                    byStatus: {   // IDLE | ACTIVE | PROCESSING | ERROR
                        idle: 0,
                        active: 0,
                        processing: 0,
                        error: 0
                    }
                },

                // Signal metrics
                signals: {
                    emitted: 0,
                    consumed: 0,
                    pending: 0,
                    deadLetter: 0,
                    errorRate: 0,
                    throughput: 0  // signals per second
                },

                // Gate validation statistics
                gates: {
                    gate_1_scope: { passed: 0, failed: 0, rate: 1.0 },
                    gate_2_value: { passed: 0, failed: 0, rate: 1.0 },
                    gate_3_capability: { passed: 0, failed: 0, rate: 1.0 },
                    gate_4_channel: { passed: 0, failed: 0, rate: 1.0 }
                },

                // Signal extraction progress (MC01-MC10)
                extractors: {
                    MC01: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC02: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC03: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC04: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC05: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC06: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC07: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC08: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC09: { status: 'IDLE', progress: 0, patterns_extracted: 0 },
                    MC10: { status: 'IDLE', progress: 0, patterns_extracted: 0 }
                },

                // Policy area signal packs (PA01-PA10)
                signalPacks: {
                    PA01: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA02: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA03: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA04: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA05: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA06: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA07: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA08: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA09: { loaded: false, patterns: 0, indicators: 0, entities: 0 },
                    PA10: { loaded: false, patterns: 0, indicators: 0, entities: 0 }
                },

                // Recent signal events
                recentSignals: [],
                maxRecentSignals: 50
            },

            // Active Job State (enhanced with SISAS)
            activeJob: {
                id: null,
                filename: null,
                status: 'IDLE',  // IDLE | QUEUED | RUNNING | COMPLETED | FAILED
                currentPhase: null,
                progress: 0,
                phaseResults: {},
                startedAt: null,
                estimatedCompletion: null,

                // SISAS-specific job data
                sisasMetrics: {
                    signalsEmitted: 0,
                    signalsConsumed: 0,
                    deadLetterRate: 0
                },

                // Micro/Meso/Macro progress
                scoringProgress: {
                    microCompleted: 0,
                    microTotal: 300,
                    mesoCompleted: 0,
                    mesoTotal: 4,
                    macroComputed: false
                }
            },

            // Evidence Stream State
            evidenceStream: {
                items: [],
                lastUpdated: null,
                autoScroll: true,
                maxItems: 100,
                filterByRegion: null,
                filterByQuestion: null
            },

            // Analysis Level State (Macro/Meso/Micro)
            analysisLevel: {
                current: 'macro',  // macro | meso | micro
                macroScore: null,
                macroData: null,
                mesoScores: {},  // {CL01: score, CL02: score, ...}
                microScores: {}  // {Q001: score, Q002: score, ...}
            }
        };
    }

    /**
     * Update SISAS metrics from backend
     * @param {Object} metrics - SISAS metrics payload
     */
    updateSISASMetrics(metrics) {
        const updates = {
            sisas: {
                ...this.state.sisas,
                enabled: true,
                status: 'ONLINE',
                lastUpdate: new Date().toISOString()
            }
        };

        // Update signal metrics
        if (metrics.signals) {
            updates.sisas.signals = {
                ...this.state.sisas.signals,
                ...metrics.signals
            };
        }

        // Update gate statistics
        if (metrics.gates) {
            updates.sisas.gates = metrics.gates;
        }

        // Update consumer status
        if (metrics.activeConsumers) {
            updates.sisas.consumers.active = metrics.activeConsumers.length;
        }

        this.updateState(updates);
    }

    /**
     * Update job progress with SISAS data
     * @param {Object} jobData - Job progress payload from WebSocket
     */
    updateJobProgress(jobData) {
        const updates = {
            activeJob: {
                ...this.state.activeJob,
                id: jobData.job_id,
                status: jobData.status || 'RUNNING',
                currentPhase: jobData.phase,
                progress: jobData.progress || 0
            }
        };

        // Add SISAS metrics if present
        if (jobData.sisas_metrics) {
            updates.activeJob.sisasMetrics = {
                signalsEmitted: jobData.sisas_metrics.signals_emitted || 0,
                signalsConsumed: jobData.sisas_metrics.signals_consumed || 0,
                deadLetterRate: jobData.sisas_metrics.dead_letter_rate || 0
            };
        }

        // Add scoring progress if present
        if (jobData.scoring_progress) {
            updates.activeJob.scoringProgress = jobData.scoring_progress;
        }

        // Estimate completion
        if (jobData.progress > 0 && !updates.activeJob.estimatedCompletion) {
            updates.activeJob.estimatedCompletion = this._calculateETA(jobData);
        }

        this.updateState(updates);
    }

    /**
     * Append evidence item to stream
     * @param {Object} evidence - Evidence item
     */
    appendEvidence(evidence) {
        const items = [
            evidence,
            ...this.state.evidenceStream.items
        ].slice(0, this.state.evidenceStream.maxItems);

        this.updateState({
            evidenceStream: {
                ...this.state.evidenceStream,
                items,
                lastUpdated: new Date().toISOString()
            }
        });
    }

    /**
     * Update signal extraction progress
     * @param {string} extractorId - Extractor ID (MC01-MC10)
     * @param {Object} progress - Progress data
     */
    updateExtractorProgress(extractorId, progress) {
        const updates = {
            sisas: {
                ...this.state.sisas,
                extractors: {
                    ...this.state.sisas.extractors,
                    [extractorId]: {
                        status: progress.status || 'PROCESSING',
                        progress: progress.progress || 0,
                        patterns_extracted: progress.patterns_extracted || 0
                    }
                }
            }
        };

        this.updateState(updates);
    }

    /**
     * Add signal event to recent signals
     * @param {Object} signal - Signal event data
     */
    addRecentSignal(signal) {
        const recentSignals = [
            {
                ...signal,
                timestamp: new Date().toISOString()
            },
            ...this.state.sisas.recentSignals
        ].slice(0, this.state.sisas.maxRecentSignals);

        this.updateState({
            sisas: {
                ...this.state.sisas,
                recentSignals
            }
        });
    }

    /**
     * Update analysis level and scores
     * @param {string} level - Analysis level (macro | meso | micro)
     * @param {Object} data - Score data
     */
    updateAnalysisLevel(level, data) {
        const updates = {
            analysisLevel: {
                ...this.state.analysisLevel,
                current: level
            }
        };

        if (level === 'macro') {
            updates.analysisLevel.macroScore = data.score;
            updates.analysisLevel.macroData = data;
        } else if (level === 'meso') {
            updates.analysisLevel.mesoScores = data.clusterScores;
        } else if (level === 'micro') {
            updates.analysisLevel.microScores = data.questionScores;
        }

        this.updateState(updates);
    }

    /**
     * Calculate ETA for job completion
     * @param {Object} jobData - Job data
     * @returns {string} ISO timestamp
     */
    _calculateETA(jobData) {
        if (!jobData.startedAt || !jobData.progress) {
            return null;
        }

        const startTime = new Date(jobData.startedAt).getTime();
        const now = Date.now();
        const elapsed = now - startTime;
        const remaining = (elapsed / jobData.progress) * (100 - jobData.progress);

        return new Date(now + remaining).toISOString();
    }

    /**
     * Get SISAS summary for display
     * @returns {Object} SISAS summary
     */
    getSISASSummary() {
        const { sisas } = this.state;

        return {
            online: sisas.enabled && sisas.status === 'ONLINE',
            consumers: `${sisas.consumers.active}/${sisas.consumers.total}`,
            signals: {
                total: sisas.signals.emitted,
                pending: sisas.signals.pending,
                failed: sisas.signals.deadLetter
            },
            health: {
                errorRate: sisas.signals.errorRate,
                deadLetterRate: sisas.signals.deadLetter / Math.max(sisas.signals.emitted, 1),
                gatePassRate: this._calculateGatePassRate()
            }
        };
    }

    /**
     * Calculate overall gate pass rate
     * @returns {number} Pass rate (0-1)
     */
    _calculateGatePassRate() {
        const { gates } = this.state.sisas;
        const totalPassed = Object.values(gates).reduce((sum, gate) => sum + gate.passed, 0);
        const totalAttempts = Object.values(gates).reduce((sum, gate) => sum + gate.passed + gate.failed, 0);

        return totalAttempts > 0 ? totalPassed / totalAttempts : 1.0;
    }
}

// ============================================================================
// WEBSOCKET INTEGRATION FOR SISAS
// ============================================================================

class SISASWebSocketHandler {
    constructor(stateManager, socketURL) {
        this.stateManager = stateManager;
        this.socketURL = socketURL;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        console.log('[SISAS WS] Connecting to', this.socketURL);

        this.socket = io(this.socketURL, {
            transports: ['websocket', 'polling']
        });

        // System status
        this.socket.on('system_status', (data) => {
            console.log('[SISAS WS] System status:', data);
            this.stateManager.updateState({
                sisas: {
                    ...this.stateManager.state.sisas,
                    enabled: data.sisas_enabled || false,
                    status: data.status === 'online' ? 'ONLINE' : 'OFFLINE'
                }
            });
        });

        // SISAS metrics update
        this.socket.on('sisas_metrics_update', (data) => {
            console.log('[SISAS WS] Metrics update:', data);
            this.stateManager.updateSISASMetrics(data.metrics);
        });

        // Pipeline progress (enhanced with SISAS)
        this.socket.on('pipeline_progress', (data) => {
            console.log('[SISAS WS] Pipeline progress:', data);
            this.stateManager.updateJobProgress(data);
        });

        // Job created
        this.socket.on('job_created', (data) => {
            console.log('[SISAS WS] Job created:', data);
            this.stateManager.updateState({
                activeJob: {
                    ...this.stateManager.state.activeJob,
                    id: data.job_id,
                    filename: data.filename,
                    status: 'QUEUED',
                    startedAt: new Date().toISOString()
                }
            });
        });

        // Job completed
        this.socket.on('pipeline_completed', (data) => {
            console.log('[SISAS WS] Job completed:', data);
            this.stateManager.updateState({
                activeJob: {
                    ...this.stateManager.state.activeJob,
                    status: 'COMPLETED',
                    progress: 100
                }
            });
        });

        // NEW: Signal emission event
        this.socket.on('sisas_signal_emitted', (data) => {
            console.log('[SISAS WS] Signal emitted:', data);
            this.stateManager.addRecentSignal(data);
        });

        // NEW: Consumer status update
        this.socket.on('sisas_consumer_status', (data) => {
            console.log('[SISAS WS] Consumer status:', data);
            // Update consumer-specific state
        });

        // NEW: Gate validation result
        this.socket.on('sisas_gate_validation', (data) => {
            console.log('[SISAS WS] Gate validation:', data);
            // Update gate statistics
        });

        // NEW: Evidence extraction
        this.socket.on('evidence_extracted', (data) => {
            console.log('[SISAS WS] Evidence extracted:', data);
            this.stateManager.appendEvidence(data);
        });

        // Connection events
        this.socket.on('connect', () => {
            console.log('[SISAS WS] Connected');
            this.reconnectAttempts = 0;

            // Request initial SISAS update
            this.socket.emit('request_sisas_update');
        });

        this.socket.on('disconnect', () => {
            console.log('[SISAS WS] Disconnected');
            this.stateManager.updateState({
                sisas: {
                    ...this.stateManager.state.sisas,
                    status: 'OFFLINE'
                }
            });
        });

        this.socket.on('error', (error) => {
            console.error('[SISAS WS] Error:', error);
        });
    }

    /**
     * Request job status update
     * @param {string} jobId - Job ID
     */
    requestJobStatus(jobId) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_job_status', { job_id: jobId });
        }
    }

    /**
     * Request SISAS metrics update
     */
    requestSISASUpdate() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_sisas_update');
        }
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// ============================================================================
// EXPORT
// ============================================================================

// Make available globally
if (typeof window !== 'undefined') {
    window.SISASEnhancedStateManager = SISASEnhancedStateManager;
    window.SISASWebSocketHandler = SISASWebSocketHandler;
}
