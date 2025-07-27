"use client"

// import { useState, useEffect } from 'react';
// const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

function DocsPage() {

  // const [isLoading, setIsLoading] = useState(true);

  // useEffect(() => {
  //   // Check if the docs are accessible before rendering the iframe
  //   fetch(`${BACKEND_URL}/docs/index.html`)
  //     .then((response) => {
  //       if (response.ok) {
  //         setIsLoading(false);
  //       } else {
  //         console.error("Sphinx documentation not accessible");
  //       }
  //     })
  //     .catch((error) => {
  //       console.error("Error loading documentation:", error);
  //     });
  // }, []);

  return (
    <div>
      {/* Download Links Section */}
      <div>
      <h1 className="p-1 text-2xl text-gray-700">
        <a
          href="/CRISP_Guide.pdf"
          download="CRISP_guide.pdf"
          style={{ color: 'blue', textDecoration: 'underline' }}
        >
          Click here to download the CRISP user guide
        </a>
      </h1>
      </div>

      <hr /> 

      {/* Dynamically Loaded Documentation */}
      <div>
        <iframe
          src="/CRISP_Guide.pdf"
          width="100%"
          height="800px"
          style={{ border: '1px solid #ccc' }}
          title="CRISP User Guide PDF"
        />
        {/* Display loading state while docs are loading */}
        {/* {isLoading ? (
          <div>Loading documentation...</div>
        ) : (
          <iframe
            src="http://localhost:8000/docs/index.html"
            width="100%"
            height="800px"
            style={{ border: 'none' }}
            title="Sphinx Documentation"
          />
        )} */}
      </div>
    
    </div>
  );
}

export default DocsPage;
