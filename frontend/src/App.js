import Header from "./Component/Header";
import Insert from "./Component/Insert";

function App() {
  return (
    <div className="min-h-full h-auto">
      <header className="flex">
        <div className="">
          <Header />
        </div>
      </header>

      <main className="flex justify-center">
        <div>
          <Insert />
        </div>
      </main>
      <footer className="flex">
        <div></div>
      </footer>
    </div>
  );
}

export default App;
