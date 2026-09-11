import Chat from './components/Chat'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-mark">OC</span>
          <div>
            <h1>OmniCorp Knowledge Assistant</h1>
            <p className="subtitle">RAG prototype for Customer Success Managers</p>
          </div>
        </div>
      </header>
      <main className="main">
        <Chat />
      </main>
      <footer className="footer">
        <span>Answers are generated strictly from internal documentation · Citations shown below each response</span>
      </footer>
    </div>
  )
}

export default App
