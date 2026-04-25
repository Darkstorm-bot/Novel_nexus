import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import StoryEditor from './pages/StoryEditor';
import PipelineMonitor from './pages/PipelineMonitor';
import CharacterManager from './pages/CharacterManager';
import MemoryBrowser from './pages/MemoryBrowser';
import Layout from './components/Layout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="story/:storyId" element={<StoryEditor />} />
            <Route path="story/:storyId/pipeline" element={<PipelineMonitor />} />
            <Route path="story/:storyId/characters" element={<CharacterManager />} />
            <Route path="memory" element={<MemoryBrowser />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
