"use client"

import { useState, useEffect } from 'react';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

function DocsPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if the docs are accessible before rendering the iframe
    fetch(`${BACKEND_URL}/docs/index.html`)
      .then((response) => {
        if (response.ok) {
          setIsLoading(false);
        } else {
          console.error("Sphinx documentation not accessible");
        }
      })
      .catch((error) => {
        console.error("Error loading documentation:", error);
      });
  }, []);

  return (
    <div>
      {/* Download Links Section */}
      <div>
      <h1 className="p-1 text-xl text-gray-700">
          Download CRISP user manual
      </h1>
        <a
          href="/CRISP_Docs.pdf"
          download="CRISP_guide.pdf"
          style={{ color: 'blue', textDecoration: 'underline' }}
        >
          Click here to download the CRISP guide
        </a>
        <h1 className="p-1 text-xl text-gray-700">
            Download Semester 1 Reports
        </h1>

        <h1 className="p-1 text-xl text-gray-700">
          Download Semester 2 Reports
      </h1>
      </div>

      <hr /> 

      {/* Dynamically Loaded Documentation */}
      <div>

        {/* Display loading state while docs are loading */}
        {isLoading ? (
          <div>Loading documentation...</div>
        ) : (
          <iframe
            src="http://localhost:8000/docs/index.html"
            width="100%"
            height="800px"
            style={{ border: 'none' }}
            title="Sphinx Documentation"
          />
        )}
      </div>
    </div>
  );
}

export default DocsPage;
