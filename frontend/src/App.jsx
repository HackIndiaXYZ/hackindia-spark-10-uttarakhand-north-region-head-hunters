import { useEffect, useState } from 'react'

function App() {
  const [caseData, setCaseData] = useState(null)
  const [events, setEvents] = useState([])
  const [findings, setFindings] = useState([])
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
    ])
      .then(([data, eventData, findingData]) => {
        setCaseData(data)
        setEvents(eventData)
        setFindings(findingData)
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>{caseData.case_number}</h1>
      <p>{caseData.title}</p>
      <p>{caseData.description}</p>
      <p>{caseData.status}</p>
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
          {events.map((event) => (
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
          {findings.map((finding) => (
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
    </main>
  )
}

export default App
