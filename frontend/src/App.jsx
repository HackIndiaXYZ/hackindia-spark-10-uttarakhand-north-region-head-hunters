import { useEffect, useState } from 'react'

function App() {
  const [caseData, setCaseData] = useState(null)
  const [events, setEvents] = useState([])
  const [eventSearch, setEventSearch] = useState('')
  const [selectedEventType, setSelectedEventType] = useState('all')
  const [findings, setFindings] = useState([])
  const [findingSearch, setFindingSearch] = useState('')
  const [selectedFindingType, setSelectedFindingType] = useState('all')
  const [anomalies, setAnomalies] = useState([])
  const [selectedAnomalyModel, setSelectedAnomalyModel] = useState('all')
  const [selectedAnomalyStatus, setSelectedAnomalyStatus] = useState('all')
  const [evidence, setEvidence] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchJson = (url) =>
      fetch(url).then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`)
        }
        return response.json()
      })

    Promise.all([
      fetchJson('http://127.0.0.1:8000/cases/1'),
      fetchJson('http://127.0.0.1:8000/cases/1/events'),
      fetchJson('http://127.0.0.1:8000/cases/1/findings'),
      fetchJson('http://127.0.0.1:8000/cases/1/anomalies'),
      fetchJson('http://127.0.0.1:8000/cases/1/evidence'),
    ])
      .then(([data, eventData, findingData, anomalyData, evidenceData]) => {
        setCaseData(data)
        setEvents(eventData)
        setFindings(findingData)
        setAnomalies(anomalyData)
        setEvidence(evidenceData)
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

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

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <section>
        <h1>Case Overview</h1>
        <p>Case Number: {caseData.case_number}</p>
        <p>Title: {caseData.title}</p>
        <p>Description: {caseData.description}</p>
        <p>Status: {caseData.status}</p>
      </section>
      <section>
        <h2>Investigation Summary</h2>
        <p>Total Events: {events.length}</p>
        <p>Total Findings: {findings.length}</p>
        <p>Total Anomalies: {anomalies.length}</p>
        <p>Total Evidence: {evidence.length}</p>
      </section>
      <section>
        <h2>Evidence</h2>
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Source</th>
              <th>Evidence Type</th>
              <th>File Size</th>
              <th>SHA-256</th>
              <th>Ingested At</th>
              <th>Processing Status</th>
            </tr>
          </thead>
          <tbody>
            {evidence.map((item) => (
              <tr key={item.id}>
                <td>{item.filename}</td>
                <td>{item.source}</td>
                <td>{item.evidence_type}</td>
                <td>{item.file_size}</td>
                <td>{item.sha256}</td>
                <td>{item.ingested_at}</td>
                <td>{item.processing_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section>
        <h2>Event Timeline</h2>
        <input
          type="text"
          placeholder="Search events..."
          value={eventSearch}
          onChange={(event) => setEventSearch(event.target.value)}
        />
        <select
          value={selectedEventType}
          onChange={(event) => setSelectedEventType(event.target.value)}
        >
          <option value="all">All Event Types</option>
          {eventTypes.map((eventType) => (
            <option key={eventType} value={eventType}>
              {eventType}
            </option>
          ))}
        </select>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>User</th>
                <th>Device</th>
                <th>IP Address</th>
                <th>Application</th>
                <th>Process</th>
                <th>File Path</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event) => (
                <tr key={event.id}>
                  <td>{event.timestamp}</td>
                  <td>{event.event_type}</td>
                  <td>{event.user}</td>
                  <td>{event.device}</td>
                  <td>{event.ip_address}</td>
                  <td>{event.application}</td>
                  <td>{event.process}</td>
                  <td>{event.file_path}</td>
                  <td>{event.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section>
        <h2>Investigation Findings</h2>
        <input
          type="text"
          placeholder="Search findings..."
          value={findingSearch}
          onChange={(event) => setFindingSearch(event.target.value)}
        />
        <select
          value={selectedFindingType}
          onChange={(event) => setSelectedFindingType(event.target.value)}
        >
          <option value="all">All Finding Types</option>
          {findingTypes.map((findingType) => (
            <option key={findingType} value={findingType}>
              {findingType}
            </option>
          ))}
        </select>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Finding Type</th>
                <th>Title</th>
                <th>Description</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {filteredFindings.map((finding) => (
                <tr key={finding.id}>
                  <td>{finding.finding_type}</td>
                  <td>{finding.title}</td>
                  <td>{finding.description}</td>
                  <td>{finding.confidence}</td>
                  <td>{finding.status}</td>
                  <td>{finding.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section>
        <h2>Anomaly Analysis</h2>
        <select
          value={selectedAnomalyModel}
          onChange={(event) => setSelectedAnomalyModel(event.target.value)}
        >
          <option value="all">All Models</option>
          <option value="isolation_forest">Isolation Forest</option>
          <option value="lof">LOF</option>
        </select>
        <select
          value={selectedAnomalyStatus}
          onChange={(event) => setSelectedAnomalyStatus(event.target.value)}
        >
          <option value="all">All Results</option>
          <option value="anomalies">Anomalies Only</option>
          <option value="non-anomalies">Non-Anomalies Only</option>
        </select>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Model Name</th>
                <th>Anomaly Score</th>
                <th>Is Anomaly</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {filteredAnomalies.map((anomaly) => (
                <tr key={anomaly.id}>
                  <td>{anomaly.event_id}</td>
                  <td>{anomaly.model_name}</td>
                  <td>{anomaly.anomaly_score}</td>
                  <td>{String(anomaly.is_anomaly)}</td>
                  <td>{anomaly.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}

export default App
