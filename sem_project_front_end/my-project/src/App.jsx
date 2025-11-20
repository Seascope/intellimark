import { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black-100 p-6">
      <h1 className="text-4xl font-bold text-green-600 mb-6">
        Simple React + Tailwind App
      </h1>

      <button
        onClick={() => setCount(count + 1)}
        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Count is {count}
      </button>

      <div className="mt-6 p-4 bg-white rounded-lg shadow-md w-80 text-center">
        <p className="text-gray-700">
          This is a simple card using Tailwind CSS.
        </p>
      </div>
    </div>
  );
}

export default App;
