import Header from "./Component/Header";
import Insert from "./Component/Insert";
import Chat from "./Component/Chat";

function App() {
  return (
    <div className="min-h-full h-auto">
      <header className="flex">
        <div className="">
          <Header />
        </div>
      </header>

      <main className="flex flex-col items-center">
        <div>
          <Insert />
        </div>
        <div className="">
          <Chat />
        </div>
      </main>
      <footer className="flex">
        <div></div>
      </footer>
    </div>
  );
}

export default App;
