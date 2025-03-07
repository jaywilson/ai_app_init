import React, { useState } from 'react';


function App() {
  // State for user input and server response
  const [userInput, setUserInput] = useState('');
  const [response, setResponse] = useState('');

  // Function to handle button click and send the POST request
  const handleSubmit = async () => {
    try {
      // Send the request to the Ktor server
      const res = await fetch('http://localhost:8080/frontend_project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: userInput }), // JSON body includes user input
      });

      // Check if the request was successful
      if (!res.ok) {
        throw new Error(`Server responded with status: ${res.status}`);
      }

      // Extract response text from the server
      const data = await res.json();
      console.log('Response:', data);
      setResponse(data.projectId || data.error); // Use the 'content' field from the server response
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while contacting the server.');
    }
  };

  return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>React Ktor Interaction</h1>

        {/* User input text box */}
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="userInput">Enter your text:</label>
          <br />
          <textarea
              id="userInput"
              rows="4"
              style={{ width: '100%' }}
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type something to send to the server..."
          />
        </div>

        {/* Submit button */}
        <div style={{ marginBottom: '10px' }}>
          <button
              onClick={handleSubmit}
              style={{
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: '#fff',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
          >
            Submit
          </button>
        </div>
        {/* Download button */}
        {response && response !== 'Building Project...' && !response.startsWith('An error') && (
          <div style={{ marginBottom: '10px' }}>
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`http://localhost:8080/download_project?project_id=${response}`);
                  if (!res.ok) {
                    throw new Error(`Download failed with status: ${res.status}`);
                  }
                  
                  // Create blob from response and trigger download
                  const blob = await res.blob();
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${response}.zip`;
                  document.body.appendChild(a);
                  a.click();
                  window.URL.revokeObjectURL(url);
                  document.body.removeChild(a);
                } catch (error) {
                  console.error('Download error:', error);
                  setResponse('Error downloading project');
                }
              }}
              style={{
                padding: '10px 20px',
                backgroundColor: '#28a745',
                color: '#fff', 
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                marginLeft: '10px'
              }}
            >
              Download Project
            </button>
          </div>
        )}
      </div>
  );
}

export default App;