This is the final transition milestone. Having completed all 6 Mastery Labs, you will execute a 24-hour mock hackathon to build, deploy, and demo "Voice-Chef" — an interactive, voice-activated AI recipe planner.
This tests your speed of UI prototyping (v0.dev/Lovable), zero-config cloud deployment (Vercel/Railway), and integration of multimodal streaming APIs (Whisper/ElevenLabs/DALL-E).

#### Tasks:
- [ ] Set up the GitHub "Frontend Starter Kit" template with Tailwind and default fetches.
- [ ] Build a robust FastAPI backend with standard schema validation and recipe mock data.
- [ ] Generate a beautiful dark-mode React dashboard using **v0.dev** and connect it to your endpoints.
- [ ] Integrate **Whisper API** to process recording inputs and **DALL-E 3 / Flux** to output food mockups.
- [ ] Deploy the frontend instantly to **Vercel** and the backend to **Railway**, verifying public endpoint routing.
- [ ] Record a 2-minute Loom product pitch demo video showing the app working on local/mobile.

#### 🎓 Learning Checkpoint:
- **Self-Check:** What are the most common latency bottlenecks in a voice-activated RAG system? How does Server-Sent Events (SSE) or WebSockets streaming improve responsiveness?
- **Destructive Testing:** Block the ElevenLabs audio generation API. Observe how the frontend handles audio generation failures and provide visual feedback to the user.
