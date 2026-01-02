import { useAppContext } from './AppContext';
import TaskInput from '../components/TaskInput';
import TaskAnalysis from '../components/TaskAnalysis';
import ResourceDisplay from '../components/ResourceDisplay';

export default function GiveFreely() {
  const { state } = useAppContext();

  return (
    <div>
      {state.phase === 'input' && <TaskInput />}
      {state.phase === 'analysis' && <TaskAnalysis />}
      {state.phase === 'resources' && <ResourceDisplay />}
    </div>
  );
}
