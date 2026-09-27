import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

const fetchCaseData = async (caseId) => {
  const fetchJson = (url) =>
    fetch(url).then((response) => {
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      return response.json()
    })

  const [caseData, events, findings, anomalies, evidence] = await Promise.all([
    fetchJson(`${API_BASE_URL}/cases/${caseId}`),
    fetchJson(`${API_BASE_URL}/cases/${caseId}/events`),
    fetchJson(`${API_BASE_URL}/cases/${caseId}/findings`),
    fetchJson(`${API_BASE_URL}/cases/${caseId}/anomalies`),
    fetchJson(`${API_BASE_URL}/cases/${caseId}/evidence`),
  ])

  return { caseData, events, findings, anomalies, evidence }
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`
}

const formatDate = (value) => {
  if (!value) return 'Unknown'
  return new Date(value).toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

function App() {
  const [cases, setCases] = useState([])
  const [selectedCaseId, setSelectedCaseId] = useState(null)
  const [caseListLoading, setCaseListLoading] = useState(true)
  const [caseListError, setCaseListError] = useState('')
  const [caseData, setCaseData] = useState(null)
  const [events, setEvents] = useState([])
  const [eventSearch, setEventSearch] = useState('')
  const [selectedEventType, setSelectedEventType] = useState('all')
  const [findings, setFindings] = useState([])
  const [findingSearch, setFindingSearch] = useState('')
  const [selectedFindingType, setSelectedFindingType] = useState('all')
  const [expandedFindingId, setExpandedFindingId] = useState(null)
  const [selectedSupportingEventId, setSelectedSupportingEventId] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [selectedAnomalyModel, setSelectedAnomalyModel] = useState('all')
  const [selectedAnomalyStatus, setSelectedAnomalyStatus] = useState('all')
  const [evidence, setEvidence] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloadError, setDownloadError] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [intakeResult, setIntakeResult] = useState(null)
  const [intakeError, setIntakeError] = useState('')
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/cases`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`)
        }
        return response.json()
      })
      .then((caseRecords) => {
        setCases(caseRecords)
        setCaseListError('')
      })
      .catch((requestError) => setCaseListError(requestError.message))
      .finally(() => setCaseListLoading(false))
  }, [])

  useEffect(() => {
    if (selectedCaseId === null) return

    fetchCaseData(selectedCaseId)
      .then(({ caseData: data, events: eventData, findings: findingData, anomalies: anomalyData, evidence: evidenceData }) => {
        setCaseData(data)
        setEvents(eventData)
        setFindings(findingData)
        setAnomalies(anomalyData)
        setEvidence(evidenceData)
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [selectedCaseId])

  const handleCaseSelect = (caseId) => {
    setSelectedCaseId(caseId)
    setCaseData(null)
    setLoading(true)
    setError('')
    setExpandedFindingId(null)
    setSelectedSupportingEventId(null)
  }

  const refreshDashboard = async () => {
    const refreshedData = await fetchCaseData(caseData.id)
    setCaseData(refreshedData.caseData)
    setEvents(refreshedData.events)
    setFindings(refreshedData.findings)
    setAnomalies(refreshedData.anomalies)
    setEvidence(refreshedData.evidence)
  }

  const downloadReport = async (format) => {
    setDownloadError('')
    try {
      const response = await fetch(
        `${API_BASE_URL}/cases/${caseData.id}/report/${format}`,
      )
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const reportBlob = await response.blob()
      const downloadUrl = URL.createObjectURL(reportBlob)
      const downloadLink = document.createElement('a')
      downloadLink.href = downloadUrl
      downloadLink.download = `CHITRAGUPT_case_${caseData.id}_report.${format}`
      document.body.appendChild(downloadLink)
      downloadLink.click()
      downloadLink.remove()
      URL.revokeObjectURL(downloadUrl)
    } catch (downloadRequestError) {
      setDownloadError(`Report download failed: ${downloadRequestError.message}`)
    }
  }

  const chooseFile = (file) => {
    if (!file) return
    setIntakeError('')
    setIntakeResult(null)
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setSelectedFile(null)
      setIntakeError('Select a CSV evidence file to continue.')
      return
    }
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile || uploading) return

    setUploading(true)
    setIntakeError('')
    setIntakeResult(null)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE_URL}/cases/${caseData.id}/ingest`, {
        method: 'POST',
        body: formData,
      })
      const result = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(result.detail || `Upload failed with status ${response.status}`)
      }
      setIntakeResult(result)
      await refreshDashboard()
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (uploadRequestError) {
      setIntakeError(uploadRequestError.message)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    chooseFile(event.dataTransfer.files?.[0])
  }

  const eventTypes = [
    ...new Set(events.map((event) => event.event_type).filter(Boolean)),
  ].sort()
  const normalizedEventSearch = eventSearch.trim().toLowerCase()
  const filteredEvents = events.filter((event) => {
    const matchesText = [
      event.event_type,
      event.user,
      event.device,
      event.ip_address,
      event.application,
      event.process,
      event.file_path,
      event.description,
    ].some((value) =>
      String(value ?? '').toLowerCase().includes(normalizedEventSearch),
    )
    const matchesEventType =
      selectedEventType === 'all' || event.event_type === selectedEventType

    return matchesText && matchesEventType
  })
  const findingTypes = [
    ...new Set(findings.map((finding) => finding.finding_type).filter(Boolean)),
  ].sort()
  const normalizedFindingSearch = findingSearch.trim().toLowerCase()
  const filteredFindings = findings.filter((finding) => {
    const matchesText = [
      finding.finding_type,
      finding.title,
      finding.description,
      finding.status,
    ].some((value) =>
      String(value ?? '').toLowerCase().includes(normalizedFindingSearch),
    )
    const matchesFindingType =
      selectedFindingType === 'all' ||
      finding.finding_type === selectedFindingType

    return matchesText && matchesFindingType
  })
  const filteredAnomalies = anomalies.filter((anomaly) => {
    const matchesModel =
      selectedAnomalyModel === 'all' ||
      anomaly.model_name === selectedAnomalyModel
    const matchesStatus =
      selectedAnomalyStatus === 'all' ||
      (selectedAnomalyStatus === 'anomalies' && anomaly.is_anomaly === true) ||
      (selectedAnomalyStatus === 'non-anomalies' && anomaly.is_anomaly === false)

    return matchesModel && matchesStatus
  })

  const handleSelectSupportingEvent = (eventId) => {
    setSelectedSupportingEventId(eventId)
    const isFilteredOut = !filteredEvents.some((event) => event.id === eventId)
    if (isFilteredOut) {
      setEventSearch('')
      setSelectedEventType('all')
    }
    setTimeout(() => {
      const targetRow = document.getElementById(`timeline-event-${eventId}`)
      if (targetRow) {
        targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, isFilteredOut ? 60 : 0)
  }

  if (caseListLoading) {
    return (
      <div className="app-state">
        <div className="state-mark">CG</div>
        <p>Loading available investigations...</p>
      </div>
    )
  }

  if (caseListError) {
    return (
      <div className="app-state error-state">
        <div className="state-mark">!</div>
        <p>Unable to load investigations</p>
        <span>{caseListError}</span>
      </div>
    )
  }

  if (!cases.length) {
    return (
      <div className="app-state">
        <div className="state-mark">—</div>
        <p>No investigations available</p>
        <span>There are no cases registered for analysis.</span>
      </div>
    )
  }

  if (selectedCaseId === null) {
    return (
      <div className="case-selection">
        <div className="case-selection-header">
          <div className="brand-lockup">
            <div className="brand-mark">C</div>
            <div>
              <strong>CHITRAGUPT</strong>
              <span>FORENSIC CONSOLE</span>
            </div>
          </div>
          <span className="secure-chip"><span className="status-dot" />{cases.length} investigations available</span>
        </div>
        <div className="case-selection-body">
          <span className="eyebrow accent-text">INVESTIGATION WORKSPACE</span>
          <h1>Select a case to continue</h1>
          <p>Choose an investigation to open its evidence, timeline, findings, and anomaly analysis.</p>
          <div className="case-options">
            {cases.map((caseRecord) => (
              <button className="case-option" type="button" key={caseRecord.id} onClick={() => handleCaseSelect(caseRecord.id)}>
                <span className="case-option-topline"><span>{caseRecord.case_number}</span><em className="status-pill">{caseRecord.status}</em></span>
                <strong>{caseRecord.title}</strong>
                <span className="case-option-description">{caseRecord.description || 'No description available.'}</span>
                <span className="case-option-footer">Opened {formatDate(caseRecord.created_at)} <b>OPEN CASE →</b></span>
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (loading || !caseData) {
    return (
      <div className="app-state">
        <div className="state-mark">CG</div>
        <p>Loading investigation workspace...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-state error-state">
        <div className="state-mark">!</div>
        <p>Unable to load case data</p>
        <span>{error}</span>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">C</div>
          <div>
            <strong>CHITRAGUPT</strong>
            <span>FORENSIC CONSOLE</span>
          </div>
        </div>
        <div className="sidebar-case">
          <span className="eyebrow">ACTIVE CASE</span>
          <strong>{caseData.case_number}</strong>
          <span>{caseData.title}</span>
        </div>
        <nav className="side-nav" aria-label="Investigation sections">
          <a className="active" href="#overview"><span>01</span>Overview</a>
          <a href="#evidence"><span>02</span>Evidence intake</a>
          <a href="#timeline"><span>03</span>Event timeline</a>
          <a href="#findings"><span>04</span>Findings</a>
          <a href="#anomalies"><span>05</span>Anomaly analysis</a>
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Local analysis node</span>
          <small>API / connected</small>
        </div>
      </aside>

      <div className="console">
        <header className="topbar">
          <div className="breadcrumbs"><span>INVESTIGATIONS</span><b>/</b><strong>{caseData.case_number}</strong></div>
          <div className="topbar-meta">
            <span className="secure-chip"><span className="status-dot" />Evidence chain active</span>
            <span className="topbar-time">Updated {formatDate(caseData.updated_at)}</span>
          </div>
        </header>

        <main className="dashboard">
          <section id="overview" className="hero-panel">
            <div className="hero-copy">
              <span className="eyebrow accent-text">CASE FILE / {caseData.id}</span>
              <h1>{caseData.title}</h1>
              <p>{caseData.description || 'No case description has been recorded.'}</p>
              <div className="case-meta-row">
                <span><b>CASE NUMBER</b>{caseData.case_number}</span>
                <span><b>STATUS</b><em className="status-pill">{caseData.status}</em></span>
                <span><b>OPENED</b>{formatDate(caseData.created_at)}</span>
              </div>
            </div>
            <div className="hero-actions">
              <span className="eyebrow">EXPORT REPORT</span>
              <div className="report-actions">
                <button className="button button-ghost" type="button" onClick={() => downloadReport('json')}>JSON</button>
                <button className="button button-ghost" type="button" onClick={() => downloadReport('csv')}>CSV</button>
                <button className="button button-primary" type="button" onClick={() => downloadReport('pdf')}>PDF REPORT</button>
              </div>
              {downloadError && <p className="inline-error" role="alert">{downloadError}</p>}
            </div>
          </section>

          <section className="summary-grid" aria-label="Investigation summary">
            <div className="summary-card cyan-accent"><span className="card-index">01 / EVENTS</span><strong>{events.length}</strong><span>Observed events</span></div>
            <div className="summary-card amber-accent"><span className="card-index">02 / EVIDENCE</span><strong>{evidence.length}</strong><span>Evidence items</span></div>
            <div className="summary-card red-accent"><span className="card-index">03 / FINDINGS</span><strong>{findings.length}</strong><span>Investigation findings</span></div>
            <div className="summary-card violet-accent"><span className="card-index">04 / ANOMALIES</span><strong>{anomalies.filter((item) => item.is_anomaly).length}</strong><span>Flagged model results</span></div>
          </section>

          <section id="evidence" className="panel intake-panel">
            <div className="section-heading">
              <div><span className="eyebrow accent-text">01 / INGESTION</span><h2>Evidence Intake</h2><p>Register a CSV evidence source and run the investigation pipeline.</p></div>
              <span className="section-code">INGEST / CSV</span>
            </div>
            <div className="intake-layout">
              <div
                className={`drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
                onDragEnter={(event) => { event.preventDefault(); setIsDragging(true) }}
                onDragOver={(event) => event.preventDefault()}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
              >
                <input ref={fileInputRef} id="evidence-file" type="file" accept=".csv,text/csv" onChange={(event) => chooseFile(event.target.files?.[0])} />
                <label htmlFor="evidence-file">
                  <span className="upload-glyph">↑</span>
                  <strong>{selectedFile ? selectedFile.name : 'Drop evidence file here'}</strong>
                  <span>{selectedFile ? `${formatBytes(selectedFile.size)} ready for intake` : 'or select a CSV from your workstation'}</span>
                </label>
              </div>
              <div className="intake-action">
                <div><span className="eyebrow">SOURCE REQUIREMENT</span><p>CSV security logs with normalized event fields.</p></div>
                <button className="button button-primary upload-button" type="button" disabled={!selectedFile || uploading} onClick={handleUpload}>
                  {uploading ? 'PROCESSING...' : 'UPLOAD & ANALYZE'}
                </button>
              </div>
            </div>
            {intakeError && <p className="inline-error" role="alert">{intakeError}</p>}
            {intakeResult && (
              <div className="intake-result">
                <span className="result-check">✓</span>
                <div><strong>Evidence processed successfully</strong><span>Record {intakeResult.evidence_id} is now linked to this case.</span></div>
                <div className="result-metrics"><span><b>{intakeResult.event_count}</b> events</span><span><b>{intakeResult.finding_count}</b> findings</span><span><b>{intakeResult.anomaly_count}</b> anomalies</span></div>
              </div>
            )}
          </section>

          <section className="panel" aria-labelledby="evidence-heading">
            <div className="section-heading"><div><span className="eyebrow accent-text">02 / CHAIN OF CUSTODY</span><h2 id="evidence-heading">Evidence Register</h2></div><span className="section-code">{evidence.length} ITEMS</span></div>
            <div className="table-wrap">
              <table><thead><tr><th>Filename</th><th>Source</th><th>Type</th><th>Size</th><th>SHA-256</th><th>Ingested</th><th>Status</th></tr></thead>
                <tbody>{evidence.length ? evidence.map((item) => <tr key={item.id}><td className="strong-cell">{item.filename}</td><td>{item.source || '—'}</td><td><span className="type-tag">{item.evidence_type}</span></td><td>{formatBytes(item.file_size)}</td><td className="hash-cell">{item.sha256}</td><td>{formatDate(item.ingested_at)}</td><td><span className="status-pill">{item.processing_status}</span></td></tr>) : <tr><td className="empty-cell" colSpan="7">No evidence registered for this case.</td></tr>}</tbody>
              </table>
            </div>
          </section>

          <section id="timeline" className="panel" aria-labelledby="timeline-heading">
            <div className="section-heading"><div><span className="eyebrow accent-text">03 / EVENT RECONSTRUCTION</span><h2 id="timeline-heading">Event Timeline</h2></div><span className="section-code">{filteredEvents.length} / {events.length} VISIBLE</span></div>
            <div className="filter-bar"><label className="search-field"><span>⌕</span><input type="text" placeholder="Search events, users, devices..." value={eventSearch} onChange={(event) => setEventSearch(event.target.value)} /></label><select value={selectedEventType} onChange={(event) => setSelectedEventType(event.target.value)}><option value="all">All event types</option>{eventTypes.map((eventType) => <option key={eventType} value={eventType}>{eventType}</option>)}</select></div>
            <div className="table-wrap timeline-table"><table><thead><tr><th>Timestamp</th><th>Event</th><th>Actor / Device</th><th>Network</th><th>Process</th><th>File path</th><th>Description</th></tr></thead><tbody>{filteredEvents.length ? filteredEvents.map((event) => <tr id={`timeline-event-${event.id}`} className={event.id === selectedSupportingEventId ? 'selected-row' : ''} key={event.id}><td className="time-cell">{formatDate(event.timestamp)}</td><td><span className="event-code">{event.event_type}</span></td><td><strong>{event.user}</strong><small>{event.device}</small></td><td>{event.ip_address}</td><td>{event.process}</td><td className="path-cell">{event.file_path || '—'}</td><td>{event.description}</td></tr>) : <tr><td className="empty-cell" colSpan="7">No events match the current filters.</td></tr>}</tbody></table></div>
          </section>

          <div className="split-grid">
            <section id="findings" className="panel" aria-labelledby="findings-heading">
              <div className="section-heading"><div><span className="eyebrow accent-text">04 / DETERMINATIONS</span><h2 id="findings-heading">Investigation Findings</h2></div><span className="section-code">{filteredFindings.length} / {findings.length}</span></div>
              <div className="filter-bar compact"><label className="search-field"><span>⌕</span><input type="text" placeholder="Search findings..." value={findingSearch} onChange={(event) => setFindingSearch(event.target.value)} /></label><select value={selectedFindingType} onChange={(event) => setSelectedFindingType(event.target.value)}><option value="all">All finding types</option>{findingTypes.map((findingType) => <option key={findingType} value={findingType}>{findingType}</option>)}</select></div>
              <div className="finding-list">{filteredFindings.length ? filteredFindings.map((finding) => {
                const supportingEventIds = Array.isArray(finding.supporting_event_ids)
                  ? finding.supporting_event_ids
                  : []
                const signalEntries = finding.signals && typeof finding.signals === 'object'
                  ? Object.entries(finding.signals)
                  : []
                const isExpanded = expandedFindingId === finding.id
                const resolvedEvents = supportingEventIds.map((eventId) => ({
                  id: eventId,
                  event: events.find((event) => event.id === eventId) ?? null,
                }))

                return (
                  <article className="finding-item" key={finding.id}>
                    <div className="finding-topline">
                      <span className="finding-severity">FINDING / {finding.id}</span>
                      <button
                        className="finding-open"
                        type="button"
                        aria-expanded={isExpanded}
                        onClick={() => setExpandedFindingId(isExpanded ? null : finding.id)}
                      >
                        {isExpanded ? 'CLOSE' : 'OPEN'}
                      </button>
                    </div>
                    <h3>{finding.title}</h3>
                    <p>{finding.description}</p>
                    <div className="finding-footer">
                      <span>Confidence <b>{finding.confidence ?? '—'}</b></span>
                      <span>Supporting events</span>
                      <div className="event-links">
                        {supportingEventIds.length
                          ? supportingEventIds.map((eventId) => (
                              <button
                                className="event-link"
                                type="button"
                                key={eventId}
                                onClick={() => handleSelectSupportingEvent(eventId)}
                                title="Click to view in timeline"
                              >
                                #{eventId}
                              </button>
                            ))
                          : <span>No supporting events</span>}
                      </div>
                    </div>
                    {isExpanded && (
                      <div className="finding-detail">
                        <dl className="finding-detail-grid">
                          <div><dt>Finding type</dt><dd>{finding.finding_type || '—'}</dd></div>
                          <div><dt>Title</dt><dd>{finding.title || '—'}</dd></div>
                          <div><dt>Description</dt><dd>{finding.description || '—'}</dd></div>
                          <div><dt>Confidence</dt><dd>{finding.confidence ?? '—'}</dd></div>
                          <div><dt>Status</dt><dd>{finding.status || '—'}</dd></div>
                          <div><dt>Supporting event IDs</dt><dd>{supportingEventIds.length ? supportingEventIds.join(', ') : 'No supporting events'}</dd></div>
                        </dl>
                        <div className="finding-evidence-section">
                          <div className="finding-evidence-header">
                            <span className="eyebrow accent-text">SUPPORTING FORENSIC EVIDENCE</span>
                            <small>{supportingEventIds.length} linked event{supportingEventIds.length === 1 ? '' : 's'}</small>
                          </div>
                          {supportingEventIds.length > 0 ? (
                            <div className="table-wrap evidence-subtable-wrap">
                              <table className="evidence-subtable">
                                <thead>
                                  <tr>
                                    <th>Event ID</th>
                                    <th>Timestamp</th>
                                    <th>Event Type</th>
                                    <th>Actor / Device</th>
                                    <th>File / Process</th>
                                    <th>Description</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {resolvedEvents.map(({ id, event: item }) => {
                                    if (!item) {
                                      return (
                                        <tr key={id} className="unresolved-event-row">
                                          <td className="strong-cell">#{id}</td>
                                          <td colSpan="5" className="unresolved-cell">
                                            Event #{id} could not be resolved from loaded case logs.
                                          </td>
                                        </tr>
                                      )
                                    }
                                    const isSelected = item.id === selectedSupportingEventId
                                    const actorDevice = [item.user, item.device].filter(Boolean).join(' · ') || '—'
                                    const fileProcess = [item.file_path, item.process].filter(Boolean).join(' | ') || '—'

                                    return (
                                      <tr
                                        key={item.id}
                                        className={`evidence-subtable-row ${isSelected ? 'selected-row' : ''}`}
                                        onClick={() => handleSelectSupportingEvent(item.id)}
                                        title="Click to locate event in timeline"
                                      >
                                        <td>
                                          <button
                                            className="event-link"
                                            type="button"
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              handleSelectSupportingEvent(item.id)
                                            }}
                                          >
                                            #{item.id}
                                          </button>
                                        </td>
                                        <td className="time-cell">{formatDate(item.timestamp)}</td>
                                        <td><span className="event-code">{item.event_type || '—'}</span></td>
                                        <td>{actorDevice}</td>
                                        <td className="path-cell" title={fileProcess}>{fileProcess}</td>
                                        <td title={item.description || ''}>{item.description || '—'}</td>
                                      </tr>
                                    )
                                  })}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <div className="empty-substate">No supporting events recorded for this finding.</div>
                          )}
                        </div>
                        {signalEntries.length > 0 && (
                          <div className="finding-signals">
                            <span className="eyebrow accent-text">INVESTIGATION SIGNALS</span>
                            {signalEntries.map(([signalName, signalValue]) => (
                              <div className="signal-row" key={signalName}>
                                <strong>{signalName}</strong>
                                <pre>{JSON.stringify(signalValue, null, 2)}</pre>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </article>
                )
              }) : <div className="empty-state">No findings match the current filters.</div>}</div>
            </section>

            <section id="anomalies" className="panel" aria-labelledby="anomalies-heading">
              <div className="section-heading"><div><span className="eyebrow accent-text">05 / MODEL SIGNALS</span><h2 id="anomalies-heading">Anomaly Analysis</h2></div><span className="section-code">{filteredAnomalies.length} RESULTS</span></div>
              <div className="filter-bar compact"><select value={selectedAnomalyModel} onChange={(event) => setSelectedAnomalyModel(event.target.value)}><option value="all">All models</option><option value="isolation_forest">Isolation Forest</option><option value="lof">LOF</option></select><select value={selectedAnomalyStatus} onChange={(event) => setSelectedAnomalyStatus(event.target.value)}><option value="all">All results</option><option value="anomalies">Anomalies only</option><option value="non-anomalies">Non-anomalies only</option></select></div>
              <div className="anomaly-list">{filteredAnomalies.length ? filteredAnomalies.map((anomaly) => <div className={`anomaly-row ${anomaly.is_anomaly ? 'is-alert' : ''}`} key={anomaly.id}><span className="anomaly-indicator" /><div><strong>{anomaly.model_name}</strong><small>Event #{anomaly.event_id} · {formatDate(anomaly.created_at)}</small></div><span className="anomaly-score">{Number(anomaly.anomaly_score).toFixed(3)}</span><span className={anomaly.is_anomaly ? 'alert-text' : 'normal-text'}>{anomaly.is_anomaly ? 'FLAGGED' : 'NORMAL'}</span></div>) : <div className="empty-state">No anomaly results match the current filters.</div>}</div>
            </section>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
