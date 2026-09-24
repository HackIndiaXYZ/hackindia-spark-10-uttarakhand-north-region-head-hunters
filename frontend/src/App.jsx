import { useEffect, useState } from 'react'

function App() {
  const [caseData, setCaseData] = useState(null)
  const [events, setEvents] = useState([])
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
    ])
      .then(([data, eventData]) => {
        setCaseData(data)
        setEvents(eventData)
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
    </main>
  )
}

export default App
