interface Props {
  grid: any;
  robots: any[];
}

export default function MapVisualizer({ grid, robots }: Props) {
  // Simple grid visualization
  const cellSize = 30; // pixels
  
  return (
    <div 
      className="relative border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 overflow-hidden"
      style={{ 
        width: grid.width * cellSize, 
        height: grid.height * cellSize 
      }}
    >
      {/* Obstacles */}
      {grid.obstacles.map((obs: number[], i: number) => (
        <div
          key={`obs-${i}`}
          className="absolute bg-red-500"
          style={{
            left: obs[0] * cellSize,
            top: obs[1] * cellSize,
            width: cellSize,
            height: cellSize,
          }}
        />
      ))}

      {/* Robots */}
      {robots.map((robot) => (
        <div
          key={robot.id}
          className="absolute bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold"
          style={{
            left: robot.position[0] * cellSize,
            top: robot.position[1] * cellSize,
            width: cellSize,
            height: cellSize,
            transition: 'all 0.3s ease-in-out'
          }}
        >
          {robot.id}
        </div>
      ))}
    </div>
  );
}
