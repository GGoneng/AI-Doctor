import { useState } from "react";

import Header from "./Component/Header";
import Insert from "./Component/Insert";
import Chat from "./Component/Chat";
import Preview from "./Component/Preview";
import Loading from "./Component/Loading";

const App = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false); 
  const [id, setID] = useState(null);

  return (
    <div className="min-h-full h-auto">
      <header className="flex">
        <div className="">
          <Header />
        </div>
      </header>

      <main className="flex flex-col items-center">
        <div>
          {loading ? (
            <Loading loading={loading} />
          ) : file ? (
            <Preview file={file} setFile={setFile} />
          ) : (
            <Insert setFile={setFile} />
          )}
        </div>
        <div className="flex flex-col">
          <Chat file={file} setFile={setFile} setLoading={setLoading} id={id} setID={setID}/>
        </div>
      </main>
    </div>
  );
}

export default App;
