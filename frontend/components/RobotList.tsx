interface Robot {
  id: string;
  status: string;
  battery: number;
}

interface Props {
  robots: Robot[];
}

export default function RobotList({ robots }: Props) {
  return (
    <div className="space-y-2">
      {robots.length === 0 && <p className="text-gray-500">No active robots</p>}
      {robots.map((robot) => (
        <div key={robot.id} className="p-3 border rounded bg-gray-50 dark:bg-gray-700">
          <div className="flex justify-between items-center mb-1">
            <span className="font-bold">{robot.id}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${
              robot.status === 'IDLE' ? 'bg-gray-200 text-gray-800' : 
              robot.status === 'MOVING' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
            }`}>
              {robot.status}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
            <div 
              className={`h-2.5 rounded-full ${robot.battery > 20 ? 'bg-green-600' : 'bg-red-600'}`} 
              style={{ width: `${robot.battery}%` }}
            ></div>
          </div>
          <div className="text-xs text-right mt-1">{robot.battery}% Battery</div>
        </div>
      ))}
    </div>
  );
}
