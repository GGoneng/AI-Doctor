import { useState } from "react";

import Header from "./Component/Header";
import Insert from "./Component/Insert";
import Chat from "./Component/Chat";
import Preview from "./Component/Preview";

function App() {
  const [file, setFile] = useState(null); 

  return (
    <div className="min-h-full h-auto">
      <header className="flex">
        <div className="">
          <Header />
        </div>
      </header>

      <main className="flex flex-col items-center">
        <div>
          {file ? (<Preview file={file} setFile={setFile} />) : (<Insert setFile={setFile} />)}        
        </div>
        <div className="flex flex-col">
          <Chat file={file} />
        </div>
      </main>
    </div>
  );
}

export default App;
