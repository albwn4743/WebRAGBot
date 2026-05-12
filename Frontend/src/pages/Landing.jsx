import React from 'react';
import { FiGlobe, FiZap, FiDatabase, FiMessageSquare, FiArrowRight, FiPlay } from 'react-icons/fi';
import { HiSparkles } from 'react-icons/hi2';
import '../styles/landing.css';

const FEATURES = [
  {
    icon: <FiGlobe />,
    title: 'Smart Web Scraping',
    desc: 'Intelligently scrapes and processes website content with recursive crawling support.'
  },
  {
    icon: <FiDatabase />,
    title: 'RAG Architecture',
    desc: 'Chunks and indexes content for retrieval-augmented generation, ready for vector DBs.'
  },
  {
    icon: <FiMessageSquare />,
    title: 'Contextual Chat',
    desc: 'Ask questions about any website and get accurate, source-cited AI answers.'
  },
  {
    icon: <FiZap />,
    title: 'Powered by Claude',
    desc: 'Uses Anthropic\'s Claude for intelligent, nuanced answers from your scraped content.'
  },
  {
    icon: <HiSparkles />,
    title: 'Multi-page Support',
    desc: 'Crawls multiple pages and builds a comprehensive knowledge base from any domain.'
  },
  {
    icon: <FiDatabase />,
    title: 'Session Management',
    desc: 'Save and revisit chat sessions for different websites with full history support.'
  }
];

function Landing({ onGetStarted }) {
  return (
    <div className="landing">
      <div className="landing-bg" />
      <div className="landing-grid" />

      {/* Nav */}
      <nav className="landing-nav">
        <div className="nav-logo">
          <div className="nav-logo-icon">🌐</div>
          <span className="nav-logo-text">Web<span>RAG</span></span>
        </div>
        <div className="nav-links">
          <button className="nav-btn-ghost">Developed By ALBIN JOY</button>
          {/* <button className="nav-btn-ghost">GitHub</button>
          <button className="nav-btn-primary" onClick={onGetStarted}>
            Launch App
          </button> */}
        </div>
      </nav>

      {/* Hero */}
      <section className="landing-hero">
        {/* <div className="hero-badge">
          <HiSparkles /> RAG-Powered Web Intelligence
        </div> */}

        <h1 className="hero-title">
          Chat with{' '}
          <span className="hero-title-gradient">Any Website</span>
          {/* <br />in Seconds */}
        </h1>

        <p className="hero-subtitle">
          Scrape and converse with any website using AI.<br />
          Built on retrieval-augmented generation for accuracy.
        </p>

        <div className="hero-actions">
          <button className="btn-hero-primary" onClick={onGetStarted}>
            Get Started<FiArrowRight />
          </button>
          <button className="btn-hero-secondary">
            Web Extension<FiZap></FiZap>
          </button>
          {/* <button className="btn-hero-secondary">
            <FiPlay /> Watch Demo
          </button> */}
        </div>

        {/* Demo card */}
        {/* <div className="hero-demo">
          <div className="demo-card">
            <div className="demo-card-header">
              <div className="demo-dot" />
              <div className="demo-dot" />
              <div className="demo-dot" />
              <div className="demo-url-bar">https://docs.anthropic.com</div>
            </div>
            <div className="demo-chat">
              <div className="demo-msg user">
                <div className="demo-avatar user-av">U</div>
                <div className="demo-bubble">What models does Anthropic offer?</div>
              </div>
              <div className="demo-msg">
                <div className="demo-avatar ai">W</div>
                <div className="demo-bubble">
                  Based on the scraped documentation, Anthropic offers Claude Opus 4, Claude Sonnet 4, and Claude Haiku — each optimized for different use cases from deep reasoning to speed...
                </div>
              </div>
            </div>
          </div>
        </div> */}
      </section>

      {/* Features */}
      {/* <section className="landing-features">
        <div className="features-grid">
          {FEATURES.map((f, i) => (
            <div className="feature-card" key={i}>
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </section> */}

      <footer className="landing-footer">
        Built with React, Node.js, Playwright, Weaviate, FastAPI & Groq.
      </footer>
    </div>
  );
}

export default Landing;
