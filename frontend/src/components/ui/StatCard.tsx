import React from 'react';
import { Card } from './Card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SparklineDataPoint {
  val: number;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: string;
  trendValue?: number;
  trendType?: 'positive' | 'negative' | 'neutral';
  sparklineData?: number[];
  color?: 'cyan' | 'emerald' | 'violet' | 'amber' | 'rose';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue = 1,
  trendType,
  sparklineData = [12, 18, 14, 22, 28, 25, 34],
  color = 'cyan',
  onClick,
}) => {
  const isPositive = trendType ? trendType === 'positive' : trendValue > 0;
  const isNegative = trendType ? trendType === 'negative' : trendValue < 0;

  const colorStyles = {
    cyan: {
      border: 'border-cyan-500/20 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      stroke: '#06b6d4',
      fill: '#06b6d422',
    },
    emerald: {
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      stroke: '#10b981',
      fill: '#10b98122',
    },
    violet: {
      border: 'border-violet-500/20 hover:border-violet-500/40',
      iconBg: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
      stroke: '#8b5cf6',
      fill: '#8b5cf622',
    },
    amber: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      stroke: '#f59e0b',
      fill: '#f59e0b22',
    },
    rose: {
      border: 'border-rose-500/20 hover:border-rose-500/40',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      stroke: '#f43f5e',
      fill: '#f43f5e22',
    },
  }[color];

  // SVG Sparkline calculation
  const max = Math.max(...sparklineData, 1);
  const min = Math.min(...sparklineData, 0);
  const range = max - min || 1;
  const width = 100;
  const height = 30;

  const points = sparklineData
    .map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * width;
      const y = height - ((val - min) / range) * (height - 6) - 3;
      return `${x},${y}`;
    })
    .join(' ');

  const areaPoints = `0,${height} ${points} ${width},${height}`;

  return (
    <Card
      onClick={onClick}
      className={`relative group transition-all cursor-pointer ${colorStyles.border} ${
        onClick ? 'hover:-translate-y-1' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2 rounded-xl border ${colorStyles.iconBg}`}>
          {icon}
        </div>
      </div>

      <div className="flex items-baseline justify-between">
        <div>
          <h4 className="text-2xl font-black text-slate-100 tracking-tight">
            {value}
          </h4>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
          )}
        </div>

        {/* Mini SVG Sparkline */}
        <div className="w-24 h-8 shrink-0 relative">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
            <polygon points={areaPoints} fill={colorStyles.fill} />
            <polyline
              fill="none"
              stroke={colorStyles.stroke}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              points={points}
            />
          </svg>
        </div>
      </div>

      {trend && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1">
            {isPositive && <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />}
            {isNegative && <TrendingDown className="w-3.5 h-3.5 text-rose-400" />}
            {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 text-slate-400" />}
            <span
              className={
                isPositive
                  ? 'text-emerald-400 font-bold'
                  : isNegative
                  ? 'text-rose-400 font-bold'
                  : 'text-slate-400'
              }
            >
              {trend}
            </span>
          </div>
          <span className="text-[11px] text-slate-500 font-medium">vs ciclo anterior</span>
        </div>
      )}
    </Card>
  );
};
