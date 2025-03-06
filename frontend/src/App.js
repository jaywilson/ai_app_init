import React, { useState } from 'react';

function App() {
  // State for user input and server response
  const [userInput, setUserInput] = useState('');
  const [response, setResponse] = useState('');

  // Function to handle button click and send the POST request
  const handleSubmit = async () => {
    try {
      // Send the request to the Ktor server
      const res = await fetch('http://localhost:8080/completion', {
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
      setResponse(data.completion || 'No response'); // Use the 'content' field from the server response
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

        {/* Display server response */}
        <div>
          <label htmlFor="serverResponse">Response from server:</label>
          <br />
          <textarea
              id="serverResponse"
              rows="4"
              style={{ width: '100%' }}
              value={response}
              readOnly
              placeholder="Server response will appear here..."
          />
        </div>
      </div>
  );
}

export default App;